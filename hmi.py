import numpy as np
from math import cos, sin, radians, atan2, sqrt, degrees
import serial
import time
import tkinter as tk
from tkinter import ttk

# =============================================
# TUS FUNCIONES DE CINEMÁTICA (MANTENIDAS SIN CAMBIOS)
# =============================================

def cinematica_directa_RPP(theta1, q2, q3, a=0.1, b=0.2):
    q1 = radians(theta1)
    
    T1 = np.array([
        [cos(q1), -sin(q1), 0, 0],
        [sin(q1), cos(q1), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    T2 = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, q2+a],
        [0, 0, 0, 1]
    ])
    
    T3 = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, q3+b],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    T_total = T1 @ T2 @ T3
    x, y, z = T_total[0:3, 3]
    return round(x, 4), round(y, 4), round(z, 4)

def cinematica_inversa_RPP(x, y, z, a=0, b=0):
    theta1 = degrees(atan2(y,x))
    theta1 = max(-90, min(180, theta1))
    
    q2 = z - a
    q2 = max(0, q2)
    
    r = sqrt(x**2 + y**2) - b
    q3 = max(0, r)
    
    print("\nResultados de Cinemática Inversa:")
    print(f"Posición deseada: X={x:.3f} m, Y={y:.3f} m, Z={z:.3f} m")
    print(f"\nValores de articulaciones calculados:")
    print(f"Theta1 (q1): {theta1:.2f}°")
    print(f"Extensión q2: {q2:.4f} m")
    print(f"Extensión q3: {q3:.4f} m")
    
    return theta1, q2, q3

# =============================================
# CLASE DE COMUNICACIÓN CON ESP32 (CORREGIDA)
# =============================================

class BrazoESP32:
    def __init__(self, port='COM3', baudrate=115200):
        try:
            # Verificar si el módulo serial está instalado correctamente
            try:
                import serial
                self.serial = serial.Serial(port, baudrate, timeout=1)
                time.sleep(2)
                print(f"Conexión establecida con ESP32 en {port}")
            except AttributeError:
                print("ERROR: El módulo 'serial' no está instalado correctamente.")
                print("Ejecuta: pip install pyserial")
                self.serial = None
            except ImportError:
                print("ERROR: No se encontró el módulo serial")
                print("Ejecuta: pip install pyserial")
                self.serial = None
        except Exception as e:
            print(f"Error al conectar con ESP32: {e}")
            self.serial = None
    
    def enviar_comando(self, q1, q2, q3):
        if not self.serial:
            print("Error: No hay conexión con ESP32")
            return False
        
        try:
            q1 = int(max(-90, min(180, q1)))
            q2 = max(0.0, float(q2))
            q3 = max(0.0, float(q3))
            
            cmd = f"Q1,{q1};Q2,{q2:.3f};Q3,{q3:.3f}\n"
            self.serial.write(cmd.encode())
            print(f"Comando enviado: {cmd.strip()}")
            
            respuesta = self.serial.readline().decode().strip()
            if respuesta:
                print(f"ESP32 responde: {respuesta}")
            return True
        except Exception as e:
            print(f"Error al enviar comando: {e}")
            return False
    
    def cerrar(self):
        if self.serial:
            self.serial.close()
            print("Conexión con ESP32 cerrada")

# =============================================
# INTERFAZ GRÁFICA CORREGIDA (SIN RESOLUTION)
# =============================================

class BrazoRPP_HMI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Brazo RPP - ESP32")
        
        # Conexión ESP32 (configurar puerto correcto)
        self.esp32 = BrazoESP32(port='COM4', baudrate=115200)
        
        # Variables
        self.q1 = tk.DoubleVar(value=0.0)
        self.q2 = tk.DoubleVar(value=0.0)
        self.q3 = tk.DoubleVar(value=0.0)
        self.x = tk.DoubleVar(value=0.0)
        self.y = tk.DoubleVar(value=0.0)
        self.z = tk.DoubleVar(value=0.2)
        self.a = tk.DoubleVar(value=0.0)
        self.b = tk.DoubleVar(value=0.0)
        
        # Configurar interfaz
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame de parámetros
        frame_params = ttk.LabelFrame(self.root, text="Parámetros Físicos")
        frame_params.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ttk.Label(frame_params, text="a:").grid(row=0, column=0)
        ttk.Entry(frame_params, textvariable=self.a, width=6).grid(row=0, column=1)
        
        ttk.Label(frame_params, text="b:").grid(row=0, column=2)
        ttk.Entry(frame_params, textvariable=self.b, width=6).grid(row=0, column=3)
        
        # Frame de control por articulaciones (CORREGIDO)
        frame_artic = ttk.LabelFrame(self.root, text="Control por Articulaciones")
        frame_artic.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Slider para q1 (sin cambios)
        ttk.Label(frame_artic, text="Theta1 (q1):").grid(row=0, column=0)
        ttk.Scale(frame_artic, from_=-90, to=180, variable=self.q1).grid(row=0, column=1)
        ttk.Entry(frame_artic, textvariable=self.q1, width=8).grid(row=0, column=2)
        ttk.Label(frame_artic, text="°").grid(row=0, column=3)
        
        # Sliders para q2 y q3 (CORREGIDOS)
        ttk.Label(frame_artic, text="Extensión q2:").grid(row=1, column=0)
        self.slider_q2 = tk.Scale(frame_artic, from_=0, to=50, orient=tk.HORIZONTAL, 
                                 variable=self.q2, resolution=0.1)
        self.slider_q2.grid(row=1, column=1)
        ttk.Entry(frame_artic, textvariable=self.q2, width=8).grid(row=1, column=2)
        ttk.Label(frame_artic, text="cm").grid(row=1, column=3)
        
        ttk.Label(frame_artic, text="Extensión q3:").grid(row=2, column=0)
        self.slider_q3 = tk.Scale(frame_artic, from_=0, to=50, orient=tk.HORIZONTAL,
                                 variable=self.q3, resolution=0.1)
        self.slider_q3.grid(row=2, column=1)
        ttk.Entry(frame_artic, textvariable=self.q3, width=8).grid(row=2, column=2)
        ttk.Label(frame_artic, text="cm").grid(row=2, column=3)
        
        # Configurar conversión de cm a m
        self.q2.trace_add('write', lambda *_: self.convertir_cm_a_m('q2'))
        self.q3.trace_add('write', lambda *_: self.convertir_cm_a_m('q3'))
        
        ttk.Button(frame_artic, text="Mover Brazo", command=self.mover_articulaciones).grid(row=3, column=0, columnspan=4)
        ttk.Button(frame_artic, text="Calcular Posición", command=self.calcular_posicion).grid(row=4, column=0, columnspan=4)
        
        # Resto de la interfaz (sin cambios)
        frame_pos = ttk.LabelFrame(self.root, text="Control por Posición")
        frame_pos.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(frame_pos, text="X:").grid(row=0, column=0)
        ttk.Entry(frame_pos, textvariable=self.x, width=8).grid(row=0, column=1)
        ttk.Label(frame_pos, text="m").grid(row=0, column=2)
        
        ttk.Label(frame_pos, text="Y:").grid(row=1, column=0)
        ttk.Entry(frame_pos, textvariable=self.y, width=8).grid(row=1, column=1)
        ttk.Label(frame_pos, text="m").grid(row=1, column=2)
        
        ttk.Label(frame_pos, text="Z:").grid(row=2, column=0)
        ttk.Entry(frame_pos, textvariable=self.z, width=8).grid(row=2, column=1)
        ttk.Label(frame_pos, text="m").grid(row=2, column=2)
        
        ttk.Button(frame_pos, text="Mover a Posición", command=self.mover_a_posicion).grid(row=3, column=0, columnspan=3)
        ttk.Button(frame_pos, text="Calcular Articulaciones", command=self.calcular_articulaciones).grid(row=4, column=0, columnspan=3)
        
        frame_estado = ttk.LabelFrame(self.root, text="Estado Actual")
        frame_estado.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ttk.Label(frame_estado, text="Posición:").grid(row=0, column=0)
        self.lbl_pos = ttk.Label(frame_estado, text="X: 0.000 m, Y: 0.000 m, Z: 0.200 m")
        self.lbl_pos.grid(row=0, column=1, columnspan=3)
        
        ttk.Label(frame_estado, text="Articulaciones:").grid(row=1, column=0)
        self.lbl_art = ttk.Label(frame_estado, text="q1: 0°, q2: 0.000 m, q3: 0.000 m")
        self.lbl_art.grid(row=1, column=1, columnspan=3)
    
    def convertir_cm_a_m(self, variable):
        """Convierte centímetros (sliders) a metros (variables)"""
        if variable == 'q2':
            self.q2.set(self.slider_q2.get() / 100)  # cm a m
        elif variable == 'q3':
            self.q3.set(self.slider_q3.get() / 100)  # cm a m
    
    def mover_articulaciones(self):
        q1 = self.q1.get()
        q2 = self.q2.get()
        q3 = self.q3.get()
        
        if self.esp32.enviar_comando(q1, q2, q3):
            x, y, z = cinematica_directa_RPP(q1, q2, q3, self.a.get(), self.b.get())
            self.lbl_pos.config(text=f"X: {x:.3f} m, Y: {y:.3f} m, Z: {z:.3f} m")
            self.lbl_art.config(text=f"q1: {q1:.1f}°, q2: {q2:.3f} m, q3: {q3:.3f} m")
    
    def calcular_posicion(self):
        q1 = self.q1.get()
        q2 = self.q2.get()
        q3 = self.q3.get()
        a = self.a.get()
        b = self.b.get()
        
        x, y, z = cinematica_directa_RPP(q1, q2, q3, a, b)
        self.x.set(round(x, 3))
        self.y.set(round(y, 3))
        self.z.set(round(z, 3))
        self.lbl_pos.config(text=f"X: {x:.3f} m, Y: {y:.3f} m, Z: {z:.3f} m")
    
    def mover_a_posicion(self):
        x = self.x.get()
        y = self.y.get()
        z = self.z.get()
        a = self.a.get()
        b = self.b.get()
        
        q1, q2, q3 = cinematica_inversa_RPP(x, y, z, a, b)
        self.q1.set(round(q1, 1))
        self.q2.set(round(q2, 3))
        self.q3.set(round(q3, 3))
        self.slider_q2.set(q2 * 100)  # m a cm
        self.slider_q3.set(q3 * 100)  # m a cm
        
        if self.esp32.enviar_comando(q1, q2, q3):
            self.lbl_art.config(text=f"q1: {q1:.1f}°, q2: {q2:.3f} m, q3: {q3:.3f} m")
    
    def calcular_articulaciones(self):
        x = self.x.get()
        y = self.y.get()
        z = self.z.get()
        a = self.a.get()
        b = self.b.get()
        
        q1, q2, q3 = cinematica_inversa_RPP(x, y, z, a, b)
        self.q1.set(round(q1, 1))
        self.q2.set(round(q2, 3))
        self.q3.set(round(q3, 3))
        self.slider_q2.set(q2 * 100)  # m a cm
        self.slider_q3.set(q3 * 100)  # m a cm
        self.lbl_art.config(text=f"q1: {q1:.1f}°, q2: {q2:.3f} m, q3: {q3:.3f} m")

# =============================================
# EJECUCIÓN PRINCIPAL
# =============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = BrazoRPP_HMI(root)
    
    def on_closing():
        if hasattr(app, 'esp32'):
            app.esp32.cerrar()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()