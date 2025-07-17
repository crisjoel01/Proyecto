"""
HMI PARA CONTROL DE ROBOT RPP
Este programa permite:
1. Calcular la cinemática inversa (de posición a articulaciones)
2. Calcular la cinemática directa (de articulaciones a posición)
3. Comunicarse con un robot real mediante puerto serial
4. Visualizar y enviar comandos al robot
"""

# MÓDULOS IMPORTADOS
import tkinter as tk                # Para la interfaz gráfica
from tkinter import ttk, messagebox # Componentes modernos y cuadros de diálogo
import numpy as np                  # Para cálculos matemáticos avanzados
from math import cos, sin, radians  # Funciones trigonométricas
import serial                       # Para comunicación con puerto serial
import time                         # Para manejar retardos

# CONFIGURACIÓN GLOBAL (AJUSTAR SEGÚN HARDWARE)
SERIAL_PORT = '/dev/ttyUSB0'  # Puerto serial (cambiar según sistema operativo)
BAUD_RATE = 115200            # Velocidad de comunicación (debe coincidir con ESP32)
SERIAL_TIMEOUT = 1            # Tiempo de espera para operaciones serial (segundos)

# VARIABLES GLOBALES
puerto_serial = None  # Almacenará el objeto de conexión serial cuando esté activo

# FUNCIONES DE CINEMÁTICA DEL ROBOT
def cinematica_inversa_RPP(x, y, z):
    """
    Calcula los valores de las articulaciones (q1, q2, q3) necesarios para alcanzar
    una posición cartesiana específica (x, y, z).
    
    Parámetros:
        x (int): Coordenada X en mm
        y (int): Coordenada Y en mm 
        z (int): Coordenada Z en mm
    
    Retorna:
        tuple: (q1, q2, q3) donde:
            q1: Ángulo de la articulación rotacional en grados (0-180)
            q2: Extensión de la primera articulación prismática en mm (0-70)
            q3: Extensión de la segunda articulación prismática en mm (0-80)
    """
    # Conversión a enteros para garantizar precisión
    x, y, z = int(x), int(y), int(z)
    
    # Cálculo del ángulo theta1 (articulación rotacional)
    # Fórmula basada en geometría del robot RPP
    theta1 = int(np.degrees(np.arccos(-(y * np.sqrt(x**2 + y**2 - 676) + 26*x)/(x**2 + y**2))))
    
    # Limitar el ángulo al rango físico del servo (0-180°)
    theta1 = max(0, min(180, theta1))
    
    # Cálculo de q2 (altura - articulación prismática vertical)
    q2 = max(0, min(70,z - 45))  # El offset de 45mm corresponde a la altura base
    
    # Cálculo de q3 (radio - articulación prismática horizontal)
    q3 = max(0, min(80,int(np.sqrt(x**2 + y**2 - 676) - 15)))  # 676 = 26^2 (radio base)
    
    return theta1, q2, q3

def cinematica_directa_RPP(q1, q2, q3):
    """
    Calcula la posición cartesiana (x, y, z) del efector final dados los valores
    de las articulaciones del robot.
    
    Parámetros:
        q1 (int): Ángulo de la articulación rotacional en grados
        q2 (int): Extensión de la primera articulación prismática en mm
        q3 (int): Extensión de la segunda articulación prismática en mm
    
    Retorna:
        tuple: (x, y, z) posición del efector final en mm
    """
    # Conversión a enteros y validación
    q1, q2, q3 = int(q1), int(q2), int(q3)
    
    # Convertir ángulo a radianes para funciones trigonométricas
    q1_rad = radians(q1)
    
    # Matriz de transformación homogénea para la articulación rotacional (q1)
    T1 = np.array([
        [cos(q1_rad),   -sin(q1_rad), 0,    0       ],
        [sin(q1_rad),   cos(q1_rad),  0,    0       ],
        [0,             0,            1,    q2 + 87 ],  # 87mm es la altura base del primer eslabón
        [0,             0,            0,    1       ]
    ])
    
    # Matriz de transformación para las articulaciones prismáticas (q2, q3)
    T2 = np.array([
        [1, 0, 0, -26       ],            # Offset en X del efector
        [0, 1, 0, -(q3 + 32)],      # q3 + offset de 15mm
        [0, 0, 1, -42       ],            # Offset en Z del efector
        [0, 0, 0, 1         ]
    ])
    
    # Combinar transformaciones
    T_total = T1 @ T2  # Producto matricial
    
    # Extraer componentes de posición (primeros 3 elementos de la última columna)
    x, y, z = T_total[0:3, 3]
    
    # Redondear y convertir a enteros
    return int(round(x)), int(round(y)), int(round(z))

# FUNCIONES DE COMUNICACIÓN SERIAL
def conectar_serial():
    """
    Establece conexión serial con el robot.
    
    Retorna:
        serial.Serial: Objeto de conexión serial o None si falla
    """
    global puerto_serial
    
    try:
        # Si ya hay una conexión activa, la retorna
        if puerto_serial and puerto_serial.is_open:
            return puerto_serial
            
        # Crear nueva conexión serial
        puerto_serial = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=SERIAL_TIMEOUT
        )
        
        # Espera para estabilizar la conexión (necesario en algunos hardware)
        time.sleep(2)
        print(f"Conexión establecida en {SERIAL_PORT} a {BAUD_RATE} baudios")
        return puerto_serial
        
    except Exception as e:
        # Mostrar error en interfaz y consola
        messagebox.showerror("Error Serial", f"No se pudo conectar al puerto {SERIAL_PORT}:\n{str(e)}")
        print(f"Error de conexión serial: {str(e)}")
        return None

def cerrar_serial():
    """
    Cierra la conexión serial de manera segura, liberando el puerto.
    """
    global puerto_serial
    
    if puerto_serial and puerto_serial.is_open:
        try:
            puerto_serial.close()
            print("Conexión serial cerrada correctamente")
        except Exception as e:
            print(f"Error al cerrar puerto serial: {str(e)}")
    puerto_serial = None

def enviar_comando_robot(q1, q2, q3):
    """
    Envía los valores articulares al robot mediante comunicación serial.
    
    Parámetros:
        q1 (int): Ángulo de la articulación rotacional en grados
        q2 (int): Extensión de la primera articulación prismática en mm
        q3 (int): Extensión de la segunda articulación prismática en mm
    
    Retorna:
        bool: True si el envío fue exitoso, False si falló
    """
    try:
        # Establecer conexión
        puerto = conectar_serial()
        if not puerto:
            return False
            
        # Formatear mensaje según protocolo especificado
        mensaje = f"q1:{q1},q2:{q2},q3:{q3}\n"  # \n como delimitador final
        
        # Enviar mensaje codificado como bytes
        puerto.write(mensaje.encode())
        
        # Debug en consola
        print(f"[ENVIADO] {mensaje.strip()}")
        return True
        
    except Exception as e:
        # Manejo de errores
        messagebox.showerror("Error Envío", f"Fallo en comunicación serial:\n{str(e)}")
        cerrar_serial()  # Intentar limpiar la conexión
        return False

# FUNCIONES DE LA INTERFAZ GRÁFICA (HMI)
def calcular_desde_posicion():
    """
    Calcula los valores articulares (q1,q2,q3) a partir de la posición ingresada
    por el usuario y actualiza los campos correspondientes.
    """
    try:
        # Obtener valores de la interfaz
        x = int(entry_x.get())
        y = int(entry_y.get())
        z = int(entry_z.get())
        
        # Calcular cinemática inversa
        q1, q2, q3 = cinematica_inversa_RPP(x, y, z)
        
        # Actualizar campos de articulaciones
        entry_q1.delete(0, tk.END)
        entry_q2.delete(0, tk.END)
        entry_q3.delete(0, tk.END)
        entry_q1.insert(0, str(q1))
        entry_q2.insert(0, str(q2))
        entry_q3.insert(0, str(q3))
        
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores enteros válidos")

def calcular_desde_articulaciones():
    """
    Calcula la posición cartesiana (x,y,z) a partir de los valores articulares
    ingresados por el usuario y actualiza los campos correspondientes.
    """
    try:
        # Obtener valores de la interfaz
        q1 = int(entry_q1.get())
        q2 = int(entry_q2.get())
        q3 = int(entry_q3.get())
        
        # Calcular cinemática directa
        x, y, z = cinematica_directa_RPP(q1, q2, q3)
        
        # Actualizar campos de posición
        entry_x.delete(0, tk.END)
        entry_y.delete(0, tk.END)
        entry_z.delete(0, tk.END)
        entry_x.insert(0, str(x))
        entry_y.insert(0, str(y))
        entry_z.insert(0, str(z))
        
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores enteros válidos")

def enviar_valores_robot():
    """
    Obtiene los valores articulares de la interfaz y los envía al robot
    mediante comunicación serial.
    """
    try:
        # Obtener valores de la interfaz
        q1 = int(entry_q1.get())
        q2 = int(entry_q2.get())
        q3 = int(entry_q3.get())
        
        # Enviar comandos al robot
        if enviar_comando_robot(q1, q2, q3):
            # Mostrar confirmación
            messagebox.showinfo(
                "Envío Exitoso",
                f"Valores enviados al robot:\n"
                f"q1: {q1}°\n"
                f"q2: {q2} mm\n"
                f"q3: {q3} mm"
            )
    except ValueError:
        messagebox.showerror("Error", "Los valores articulares deben ser números enteros")

def on_closing():
    """
    Función ejecutada al cerrar la ventana. Garantiza un cierre seguro
    liberando los recursos de comunicación serial.
    """
    cerrar_serial()  # Cerrar conexión serial
    root.destroy()   # Cerrar ventana principal

# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA
# Crear ventana principal
root = tk.Tk()
root.title("Control Robot RPP - HMI")
root.geometry("280x420")  # Tamaño inicial de la ventana

# Configuración de estilos visuales
style = ttk.Style()
style.configure("TFrame", padding=10)  # Espaciado interno para frames
style.configure("TButton", padding=5)  # Botones más grandes
style.configure("Accent.TButton", foreground="white", background="#4CAF50")  # Botón verde
style.configure("Warning.TButton", foreground="white", background="#f44336")  # Botón rojo

# COMPONENTES DE LA INTERFAZ
# Frame para controles de posición
frame_pos = ttk.LabelFrame(root, text="Posición (X,Y,Z) - mm", padding=10)
frame_pos.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

# Campos para posición X,Y,Z
ttk.Label(frame_pos, text="X (mm):").grid(row=0, column=0, sticky="w")
entry_x = ttk.Entry(frame_pos)
entry_x.grid(row=0, column=1)

ttk.Label(frame_pos, text="Y (mm):").grid(row=1, column=0, sticky="w")
entry_y = ttk.Entry(frame_pos)
entry_y.grid(row=1, column=1)

ttk.Label(frame_pos, text="Z (mm):").grid(row=2, column=0, sticky="w")
entry_z = ttk.Entry(frame_pos)
entry_z.grid(row=2, column=1)

# Botón para calcular articulaciones
ttk.Button(
    frame_pos, 
    text="Calcular Articulaciones →", 
    command=calcular_desde_posicion
).grid(row=3, columnspan=2, pady=5)

# Frame para controles de articulaciones
frame_art = ttk.LabelFrame(root, text="Articulaciones", padding=10)
frame_art.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

# Campos para articulaciones q1,q2,q3
ttk.Label(frame_art, text="q1 (°):").grid(row=0, column=0, sticky="w")
entry_q1 = ttk.Entry(frame_art)
entry_q1.grid(row=0, column=1)

ttk.Label(frame_art, text="q2 (mm):").grid(row=1, column=0, sticky="w")
entry_q2 = ttk.Entry(frame_art)
entry_q2.grid(row=1, column=1)

ttk.Label(frame_art, text="q3 (mm):").grid(row=2, column=0, sticky="w")
entry_q3 = ttk.Entry(frame_art)
entry_q3.grid(row=2, column=1)

# Botón para calcular posición
ttk.Button(
    frame_art, 
    text="Calcular Posición →", 
    command=calcular_desde_articulaciones
).grid(row=3, columnspan=2, pady=5)

# Frame para botones de control
frame_control = ttk.Frame(root, padding=10)
frame_control.grid(row=2, column=0, sticky="ew")

# Botón para enviar valores al robot
ttk.Button(
    frame_control,
    text="ENVIAR AL ROBOT",
    command=enviar_valores_robot,
    style="Accent.TButton"
).pack(fill=tk.X)

# Botón para desconectar
ttk.Button(
    frame_control,
    text="DESCONECTAR",
    command=cerrar_serial,
    style="Warning.TButton"
).pack(fill=tk.X, pady=5)

# CONFIGURACIÓN FINAL
# Configurar función para manejar el cierre de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Iniciar el bucle principal de la interfaz
root.mainloop()