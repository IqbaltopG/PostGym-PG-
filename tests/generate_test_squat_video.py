#!/usr/bin/env python3
"""
Membuat video sintetis 5 detik gerakan squat untuk memvalidasi pipeline YOLOv8-pose.
"""
import cv2
import numpy as np

width, height = 640, 640
fps = 25
total_frames = 125 # 5 detik

out = cv2.VideoWriter("tests/sample_squat.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

for i in range(total_frames):
    frame = np.ones((height, width, 3), dtype=np.uint8) * 40 # Background gelap
    
    # Animasi squat naik turun
    t = (i % 60) / 60.0
    # Naik turun sinus
    squat_factor = np.sin(t * np.pi) # 0 -> 1 -> 0
    
    # Koordinat tubuh
    head = (320, int(150 + squat_factor * 80))
    shoulder = (320, int(210 + squat_factor * 80))
    hip = (320, int(320 + squat_factor * 80))
    knee = (int(360 + squat_factor * 40), int(420 + squat_factor * 40))
    ankle = (340, 520)

    # Gambar stick figure manusia
    cv2.circle(frame, head, 30, (200, 200, 200), -1) # Kepala
    cv2.line(frame, head, hip, (200, 200, 200), 8) # Badan
    cv2.line(frame, hip, knee, (0, 200, 255), 8) # Paha
    cv2.line(frame, knee, ankle, (0, 200, 255), 8) # Betis
    
    # Kaki satunya
    cv2.line(frame, hip, (int(280 - squat_factor * 40), int(420 + squat_factor * 40)), (150, 150, 150), 6)
    cv2.line(frame, (int(280 - squat_factor * 40), int(420 + squat_factor * 40)), (300, 520), (150, 150, 150), 6)

    out.write(frame)

out.release()
print("Berhasil membuat tests/sample_squat.mp4!")
