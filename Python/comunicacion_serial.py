import serial
import time

# Configura el puerto serial (ajusta el nombre del puerto)
puerto = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)

try:
    while True:
        # Ejemplo de variables (reemplaza con tus valores reales)
        q0 = 10.5  # float
        q1 = 20    # int
        q2 = "Hola"  # string

        # Formato 1: Envía como cadena estructurada
        mensaje = f"q0:{q0},q1:{q1},q2:{q2}\n"  # \n es el delimitador final
        puerto.write(mensaje.encode())  # Envía como bytes

        # Formato alternativo (solo valores separados por comas):
        # puerto.write(f"{q0},{q1},{q2}\n".encode())

        print(f"Enviado: {mensaje.strip()}")  # Debug
        time.sleep(1)  # Espera 1 segundo entre envíos

except KeyboardInterrupt:
    puerto.close()  # Cierra el puerto al terminar
    print("Comunicación cerrada.")