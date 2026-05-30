import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import os

# Настройки стиля CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WhaleDetectorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Система автоматического мониторинга гренландских китов — ТГУ")
        self.geometry("1100x650")
        
        # Поиск весов
        self.model_path = "whale_runs/yolov8n_whale_detector/weights/best.pt"
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"Успешно загружены обученные веса: {self.model_path}")
            else:
                self.model = YOLO("yolov8n.pt")
                print("Обученные веса не найдены. Запущена базовая модель YOLOv8n.")
        except Exception as e:
            print("Ошибка инициализации модели:", e)
            self.model = None
            
        self.video_path = None
        self.video_source = None
        self.is_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        
        # ЛЕВАЯ ПАНЕЛЬ
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(self.sidebar, text="Whale-ID Мониторинг", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(pady=20, padx=10)
        
        self.btn_open = ctk.CTkButton(self.sidebar, text="Загрузить видео", command=self.open_video)
        self.btn_open.pack(pady=10, padx=20)
        
        self.btn_detect = ctk.CTkButton(
            self.sidebar, 
            text="Распознавание кита", 
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.start_detection
        )
        self.btn_detect.pack(pady=10, padx=20)
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="Статус: Ожидание файла", text_color="gray")
        self.status_label.pack(pady=5)
        
        self.conf_label = ctk.CTkLabel(self.sidebar, text="Порог уверенности: 0.10")
        self.conf_label.pack(pady=(20, 0))
        self.conf_slider = ctk.CTkSlider(self.sidebar, from_=0.01, to=1.0, command=self.update_conf)
        self.conf_slider.set(0.10)
        self.conf_slider.pack(pady=5, padx=20)
        
        self.btn_stop = ctk.CTkButton(self.sidebar, text="Остановить", fg_color="#bf4343", hover_color="#8c2f2f", command=self.stop_video)
        self.btn_stop.pack(pady=30, padx=20)
        
        # ЦЕНТРАЛЬНЫЙ ПЛЕЕР
        self.video_frame = ctk.CTkFrame(self, corner_radius=10)
        self.video_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Шаг 1: Загрузите видео\nШаг 2: Нажмите «Распознавание кита»", font=ctk.CTkFont(size=15))
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)
        
    def update_conf(self, value):
        self.conf_label.configure(text=f"Порог уверенности: {float(value):.2f}")

    def open_video(self):
        self.stop_video()
        self.video_path = tk.filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if self.video_path:
            filename = os.path.basename(self.video_path)
            self.status_label.configure(text=f"Файл: {filename}", text_color="#2ed573")
            self.video_label.configure(image="", text=f"Файл {filename} успешно загружен.\nНажмите кнопку «Распознавание кита».")
            
    def start_detection(self):
        if not self.video_path:
            return
        if self.is_running:
            return
            
        self.video_source = cv2.VideoCapture(self.video_path)
        if not self.video_source.isOpened():
            self.video_label.configure(text="Ошибка чтения видеофайла.")
            return

        self.is_running = True
        self.status_label.configure(text="Статус: Анализ нейросетью...", text_color="#ffb142")
        
        self.play_thread = threading.Thread(target=self.stream_video, daemon=True)
        self.play_thread.start()

    def stream_video(self):
        while self.is_running and self.video_source.isOpened():
            ret, frame = self.video_source.read()
            if not ret:
                break
            
            current_conf = float(self.conf_slider.get())
            
            try:
                # Получаем предсказание (возвращается список результатов)
                results = self.model.predict(frame, conf=current_conf, verbose=False)
                
                # Извлекаем первый элемент списка и вызываем .plot() без спорных аргументов
                annotated_frame = results[0].plot()
                
                # Конвертация кадра OpenCV (BGR) в формат RGB для PIL
                rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_image)
                pil_img = pil_img.resize((800, 550), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(image=pil_img)
                
                if self.is_running:
                    self.video_label.configure(image=img_tk, text="")
                    self.video_label.image = img_tk
            except Exception as e:
                print(f"Ошибка во время инференса: {e}")
                break
                
        self.video_source.release()
        self.is_running = False
        self.status_label.configure(text="Статус: Анализ завершен", text_color="gray")

    def stop_video(self):
        self.is_running = False
        if self.video_source:
            self.video_source.release()
        self.video_label.configure(image="", text="Шаг 1: Загрузите видео\nШаг 2: Нажмите «Распознавание кита»")
        self.status_label.configure(text="Статус: Ожидание файла", text_color="gray")

if __name__ == "__main__":
    app = WhaleDetectorGUI()
    app.mainloop()
