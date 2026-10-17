import os
os.environ["YOLO_OFFLINE"] = "1"
os.environ["YOLO_VERBOSE"] = "False"
import cv2
import numpy as np
import subprocess
from ultralytics import YOLO, settings
settings.update({'sync': False, 'clearml': False, 'comet': False, 'dvc': False, 'hub': False, 'mlflow': False, 'neptune': False, 'raytune': False})

# Path absolut pasti ke file model lokal
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATE_PATHS = [
    os.path.join(ROOT_DIR, "models", "yolov8n-pose.pt"),
    os.path.join(ROOT_DIR, "yolov8n-pose.pt"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "yolov8n-pose.pt"),
    "/home/ambatron/aplikasi-gym/models/yolov8n-pose.pt",
    "/home/ambatron/aplikasi-gym/yolov8n-pose.pt"
]

MODEL_PATH = None
for p in CANDIDATE_PATHS:
    if os.path.exists(p):
        MODEL_PATH = p
        break

if not MODEL_PATH:
    MODEL_PATH = "/home/ambatron/aplikasi-gym/models/yolov8n-pose.pt"

print(f"[POSE] Menggunakan model pose lokal: {MODEL_PATH}", flush=True)

class PoseAnalyzer:
    def __init__(self, model_path=MODEL_PATH):
        self.model = YOLO(model_path)

    @staticmethod
    def calculate_angle(p1, p2, p3):
        """Menghitung sudut 2D pada titik p2 (vertex) dalam derajat (0 - 180)"""
        a = np.array(p1)
        b = np.array(p2)
        c = np.array(p3)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360.0 - angle
        return angle

    def analyze_video(self, input_video_path: str, output_video_path: str, exercise: str = "squat") -> dict:
        """
        Memproses video, mendeteksi pose kerangka, menghitung repetisi & kedalaman,
        dan menghasilkan video teranotasi yang kompatibel dengan browser web.
        """
        print(f"----> [POSE] Opening cv2.VideoCapture on {input_video_path}...", flush=True)
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            raise ValueError(f"Gagal membuka video: {input_video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"----> [POSE] Video opened: {width}x{height} @ {fps} fps, total {total_f} frames", flush=True)

        # Simpan file sementara sebelum di-remux oleh ffmpeg
        temp_output_path = output_video_path.replace(".mp4", "_raw.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

        # State machine pelacak repetisi
        state = "UP"
        min_angle_in_rep = 180.0
        total_reps = 0
        valid_reps = 0
        shallow_reps = 0
        rep_details = []
        current_feedback = "SIAP"

        # COCO 17 Keypoint Indices
        # 5: L_Shoulder, 6: R_Shoulder, 7: L_Elbow, 8: R_Elbow, 9: L_Wrist, 10: R_Wrist
        # 11: L_Hip, 12: R_Hip, 13: L_Knee, 14: R_Knee, 15: L_Ankle, 16: R_Ankle
        SKELETON_PAIRS = [
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            (5, 11), (6, 12), (11, 12),
            (11, 13), (13, 15), (12, 14), (14, 16)
        ]

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            # Inference YOLO pose (CPU-optimized, ~30-50 FPS)
            results = self.model(frame, device='cpu', verbose=False)
            current_angle = None
            angle_point = None

            if len(results) > 0 and results[0].keypoints is not None:
                kpts = results[0].keypoints.xy.cpu().numpy()
                confs = results[0].keypoints.conf.cpu().numpy() if results[0].keypoints.conf is not None else None

                if len(kpts) > 0 and len(kpts[0]) >= 17:
                    person_kpts = kpts[0]
                    person_confs = confs[0] if confs is not None else [1.0] * 17

                    # Gambar kerangka tubuh
                    for p1_idx, p2_idx in SKELETON_PAIRS:
                        if person_confs[p1_idx] > 0.4 and person_confs[p2_idx] > 0.4:
                            pt1 = (int(person_kpts[p1_idx][0]), int(person_kpts[p1_idx][1]))
                            pt2 = (int(person_kpts[p2_idx][0]), int(person_kpts[p2_idx][1]))
                            cv2.line(frame, pt1, pt2, (255, 255, 255), 2)

                    # Gambar titik sendi
                    for idx, (x, y) in enumerate(person_kpts):
                        if person_confs[idx] > 0.4:
                            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 255), -1)

                    # --- LOGIKA SQUAT ---
                    if exercise.lower() == "squat":
                        # Tentukan sisi kiri vs kanan berdasarkan rata-rata confidence
                        left_conf = (person_confs[11] + person_confs[13] + person_confs[15]) / 3.0
                        right_conf = (person_confs[12] + person_confs[14] + person_confs[16]) / 3.0

                        if left_conf >= right_conf and left_conf > 0.4:
                            hip = person_kpts[11]
                            knee = person_kpts[13]
                            ankle = person_kpts[15]
                        elif right_conf > 0.4:
                            hip = person_kpts[12]
                            knee = person_kpts[14]
                            ankle = person_kpts[16]
                        else:
                            hip = knee = ankle = None

                        if hip is not None and knee is not None and ankle is not None:
                            current_angle = self.calculate_angle(hip, knee, ankle)
                            angle_point = (int(knee[0]), int(knee[1]))

                            # State Machine Rep Counter
                            if current_angle < 140.0:
                                state = "DOWN"
                                if current_angle < min_angle_in_rep:
                                    min_angle_in_rep = current_angle
                                
                                if min_angle_in_rep <= 95.0:
                                    current_feedback = "KEDALAMAN VALID (BAGUS!)"
                                else:
                                    current_feedback = "TURUN LEBIH DALAM LAGI..."

                            elif current_angle >= 150.0 and state == "DOWN":
                                # Repetisi selesai
                                total_reps += 1
                                if min_angle_in_rep <= 95.0:
                                    valid_reps += 1
                                    depth_status = "VALID"
                                    current_feedback = f"REP {total_reps}: KEDALAMAN VALID (MANTAP!)"
                                else:
                                    shallow_reps += 1
                                    depth_status = "SHALLOW"
                                    current_feedback = f"REP {total_reps}: KURANG TURUN (HALF SQUAT)"

                                rep_details.append({
                                    "rep": total_reps,
                                    "min_angle": round(float(min_angle_in_rep), 1),
                                    "depth": depth_status
                                })

                                state = "UP"
                                min_angle_in_rep = 180.0

                    # --- LOGIKA PUSH UP ---
                    elif exercise.lower() == "push_up":
                        left_conf = (person_confs[5] + person_confs[7] + person_confs[9]) / 3.0
                        right_conf = (person_confs[6] + person_confs[8] + person_confs[10]) / 3.0
                        if left_conf >= right_conf and left_conf > 0.4:
                            sh, el, wr = person_kpts[5], person_kpts[7], person_kpts[9]
                        elif right_conf > 0.4:
                            sh, el, wr = person_kpts[6], person_kpts[8], person_kpts[10]
                        else:
                            sh = el = wr = None

                        if sh is not None and el is not None and wr is not None:
                            current_angle = self.calculate_angle(sh, el, wr)
                            angle_point = (int(el[0]), int(el[1]))

                            if current_angle < 100.0:
                                state = "DOWN"
                                if current_angle < min_angle_in_rep:
                                    min_angle_in_rep = current_angle
                                current_feedback = "DADA MENDEKATI LANTAI"
                            elif current_angle >= 150.0 and state == "DOWN":
                                total_reps += 1
                                is_valid = min_angle_in_rep <= 90.0
                                if is_valid:
                                    valid_reps += 1
                                    current_feedback = f"REP {total_reps}: VALID"
                                else:
                                    shallow_reps += 1
                                    current_feedback = f"REP {total_reps}: KURANG TURUN"
                                rep_details.append({
                                    "rep": total_reps,
                                    "min_angle": round(float(min_angle_in_rep), 1),
                                    "depth": "VALID" if is_valid else "SHALLOW"
                                })
                                state = "UP"
                                min_angle_in_rep = 180.0

            # --- RENDER HUD TELEMETRI ---
            # Header Bar Transparan
            hud_bg = frame.copy()
            cv2.rectangle(hud_bg, (0, 0), (width, 85), (20, 20, 20), -1)
            cv2.addWeighted(hud_bg, 0.75, frame, 0.25, 0, frame)

            # Teks Judul & Counter
            cv2.putText(frame, f"POST GYM AI | {exercise.upper()} FORM CHECK", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv2.LINE_AA)

            rep_text = f"REPS: {total_reps}  (VALID: {valid_reps} | SHALLOW: {shallow_reps})"
            cv2.putText(frame, rep_text, (20, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Indikator Feedback Status
            status_color = (0, 255, 0) if "VALID" in current_feedback else (0, 165, 255)
            cv2.putText(frame, current_feedback, (width - 450, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2, cv2.LINE_AA)

            # Indikator Sudut di titik sendi
            if current_angle is not None and angle_point is not None:
                angle_color = (0, 255, 0) if current_angle <= 95.0 else (0, 165, 255) if current_angle < 140 else (255, 255, 255)
                cv2.circle(frame, angle_point, 18, angle_color, 2)
                cv2.putText(frame, f"{int(current_angle)} deg", (angle_point[0] + 15, angle_point[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, angle_color, 2, cv2.LINE_AA)

            out.write(frame)

        cap.release()
        out.release()

        # Remux video ke format H.264 (kompatibel penuh dengan browser Chrome/Safari/Firefox)
        try:
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", temp_output_path,
                "-vcodec", "libx264",
                "-crf", "23",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                output_video_path
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)
        except Exception as e:
            # Jika ffmpeg gagal, gunakan raw output
            print(f"[!] Warning ffmpeg encoding: {e}")
            if os.path.exists(temp_output_path) and not os.path.exists(output_video_path):
                os.rename(temp_output_path, output_video_path)

        # Evaluasi Saran / Feedback Keseluruhan
        accuracy = (valid_reps / total_reps * 100.0) if total_reps > 0 else 0.0
        if total_reps == 0:
            overall_feedback = "Tidak terdeteksi repetisi penuh. Pastikan seluruh tubuh (dari pinggul sampai telapak kaki) terlihat jelas di kamera."
        elif accuracy >= 80.0:
            overall_feedback = f"Luar biasa! Form latihan sangat solid ({valid_reps} dari {total_reps} rep mencapai kedalaman optimal di bawah 95°)."
        elif accuracy >= 50.0:
            overall_feedback = f"Cukup bagus, namun {shallow_reps} repetisi masih tergolong 'Half Squat'. Fokus dorong pinggul sedikit lebih rendah hingga sejajar lutut."
        else:
            overall_feedback = f"Kedalaman squat masih kurang ({shallow_reps} dari {total_reps} rep belum cukup turun). Coba kurangi beban sedikit untuk memprioritaskan full range of motion."

        return {
            "status": "success",
            "exercise": exercise,
            "total_reps": total_reps,
            "valid_reps": valid_reps,
            "shallow_reps": shallow_reps,
            "accuracy_percent": round(accuracy, 1),
            "rep_details": rep_details,
            "overall_feedback": overall_feedback,
            "video_url": f"/processed/{os.path.basename(output_video_path)}"
        }
