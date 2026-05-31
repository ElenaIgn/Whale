import os
from ultralytics import YOLO

def start_whale_training():
    print("--- Запуск обучения модели детекции китов YOLOv8n на CPU ---")
    
    
    model = YOLO("yolov8n.pt")
    
    
    model.train(
        data="dataset_config.yaml",
        epochs=30,
        imgsz=640,
        batch=8,           
        device="cpu",      
        project="whale_runs",
        name="yolov8n_whale_detector"
    )
    
    print("\n--- Обучение успешно завершено! ---")
    print("Лучшая модель сохранена в: whale_runs/yolov8n_whale_detector/weights/best.pt")

if __name__ == "__main__":
    start_whale_training()

