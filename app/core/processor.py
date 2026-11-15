import cv2
import numpy as np
import csv
import json
from ultralytics import YOLO
from pathlib import Path


class VideoProcessor:
    def __init__(self, model_path="weights/yolo11n.pt"):
        print(f"[初始化] 正在加载 YOLO 模型: {model_path} ...")
        self.model = YOLO(model_path)

        # 【重点修改】我们不写死坐标了，在 process 方法里根据视频实际大小动态生成
        self.zone_points = None

    def process(self, input_path: str, output_dir: str = "outputs"):
        input_path_obj = Path(input_path)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        stem = input_path_obj.stem
        video_out = out_dir / f"{stem}_result.mp4"
        csv_out = out_dir / f"{stem}_stats.csv"
        snap_dir = out_dir / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            return None

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

        # 【重点修改】根据视频尺寸，动态在画面正中央画一个巨大的禁入区
        # 这样保证无论你传什么分辨率的视频，区域一定在画面里！
        self.zone_points = np.array([
            [int(w * 0.2), int(h * 0.3)],  # 左上
            [int(w * 0.8), int(h * 0.3)],  # 右上
            [int(w * 0.8), int(h * 0.9)],  # 右下
            [int(w * 0.2), int(h * 0.9)]  # 左下
        ], np.int32)

        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 或者 *'H264'
        out = cv2.VideoWriter(str(video_out), fourcc, fps, (w, h))

        csv_file = open(csv_out, "w", newline="", encoding="utf-8-sig")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["frame_idx", "time_sec", "person_count", "intrude_count"])

        frame_idx = 0
        max_person = 0
        total_intrusions = 0
        alarm_cooldown = 0
        alarm_records = []

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # ================== 1. 画半透明禁入区 ==================
                overlay = frame.copy()
                cv2.fillPoly(overlay, [self.zone_points], (0, 0, 255))  # 填充红色
                frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)  # 透明度 30%
                cv2.polylines(frame, [self.zone_points], True, (0, 0, 255), 3)  # 红色边框加粗到3
                cv2.putText(frame, "DANGER ZONE", (self.zone_points[0][0], self.zone_points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # ================== 2. YOLO 检测 ==================
                results = self.model(frame, conf=0.15, classes=[0],iou=0.3, imgsz=1280, verbose=False)  # 置信度降到0.3，更容易检出
                boxes = results[0].boxes

                person_count = 0
                intrude_count = 0

                if boxes is not None and len(boxes) > 0:
                    for i in range(len(boxes)):
                        x1, y1, x2, y2 = map(int, boxes.xyxy[i].cpu().numpy())
                        conf = float(boxes.conf[i])
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        person_count += 1

                        # ================== 3. 判断是否入侵 ==================
                        is_inside = cv2.pointPolygonTest(self.zone_points, (cx, cy), False) >= 0

                        if is_inside:
                            intrude_count += 1
                            # 入侵：画红框，写 Intruder
                            color = (0, 0, 255)
                            label = f"Intruder {conf:.2f}"
                        else:
                            # 正常：画绿框，写 Person
                            color = (0, 255, 0)
                            label = f"Person {conf:.2f}"

                        # 画检测框
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        # 画中心点
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
                        # 写标签
                        cv2.putText(frame, label, (x1, max(y1 - 10, 20)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # ================== 4. 告警截图 ==================
                if intrude_count > 0 and alarm_cooldown == 0:
                    snap_name = f"{stem}_alarm_{frame_idx}.jpg"
                    cv2.imwrite(str(snap_dir / snap_name), frame)
                    alarm_cooldown = 30

                    alarm_records.append({
                        "frame_idx": frame_idx,
                        "time_sec": round(frame_idx / fps, 2),
                        "snapshot_url": f"/outputs/snapshots/{snap_name}"
                    })

                if alarm_cooldown > 0:
                    alarm_cooldown -= 1

                # ================== 5. 状态栏 HUD ==================
                hud_text = f"Frame: {frame_idx} | Persons: {person_count} | Intruders: {intrude_count}"
                cv2.rectangle(frame, (0, 0), (500, 40), (0, 0, 0), -1)
                cv2.putText(frame, hud_text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                out.write(frame)
                csv_writer.writerow([frame_idx, f"{frame_idx / fps:.2f}", person_count, intrude_count])

                max_person = max(max_person, person_count)
                total_intrusions += intrude_count

                if frame_idx % 50 == 0:
                    print(f"  已处理 {frame_idx} 帧...")

                frame_idx += 1

        finally:
            cap.release()
            out.release()
            csv_file.close()

        return {
            "status": "success",
            "video_path": str(video_out),
            "csv_path": str(csv_out),
            "processed_frames": frame_idx,
            "max_persons": max_person,
            "total_intrusions": total_intrusions,
            "alarm_records": alarm_records
        }