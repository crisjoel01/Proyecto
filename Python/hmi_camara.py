import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class HMIWithCamera:
    def __init__(self, root):
        self.root = root
        self.root.title("HMI con Cámara en Python")
        
        # Variables
        self.cap = None
        self.is_camera_running = False
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        # Frame para botones
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Botones
        self.btn_start = ttk.Button(
            button_frame, 
            text="Iniciar Cámara", 
            command=self.start_camera
        )
        self.btn_stop = ttk.Button(
            button_frame, 
            text="Detener Cámara", 
            command=self.stop_camera,
            state=tk.DISABLED
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta para mostrar la cámara
        self.camera_label = ttk.Label(self.root)
        self.camera_label.pack(pady=10)
    
    def start_camera(self):
        if not self.is_camera_running:
            self.cap = cv2.VideoCapture(0)  # Usar cámara 0 (webcam)
            self.is_camera_running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.show_frame()
    
    def show_frame(self):
        if self.is_camera_running:
            ret, frame = self.cap.read()
            if ret:
                # Convertir de BGR (OpenCV) a RGB (Tkinter)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Actualizar la etiqueta
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk)
                
            # Llamar recursivamente cada 10ms (actualización en tiempo real)
            self.camera_label.after(10, self.show_frame)
    
    def stop_camera(self):
        if self.is_camera_running:
            self.cap.release()
            self.is_camera_running = False
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            # Limpiar la imagen
            self.camera_label.config(image=None)

if __name__ == "__main__":
    root = tk.Tk()
    app = HMIWithCamera(root)
    root.mainloop()