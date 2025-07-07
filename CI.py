import numpy as np
from math import cos, sin, radians

def cinematica_inversa_RPP(x, y, z, a=0, b=0):
    """
    Calcula los valores de las articulaciones para alcanzar (x,y,z)
    :return: (theta1, q2, q3) - ángulo en grados y extensiones en metros
    """
    # Cálculo de theta1 (limitado a -90 a 90°)
    theta1 = np.degrees(np.arctan2(y,x))
    theta1 = max(-90, min(90, theta1))  # Limitar al rango del servo
    
    # Cálculo de q2 (altura)
    q2 = z - a
    q2 = max(0, q2)  # No puede ser negativo
    
    # Cálculo de q3 (radio)
    r = np.sqrt(x**2 + y**2) - b
    q3 = max(0, r)  # No puede ser negativo
    
    print("\nResultados de Cinemática Inversa:")
    print(f"Posición deseada: X={x:.3f} m, Y={y:.3f} m, Z={z:.3f} m")
    print(f"\nValores de articulaciones calculados:")
    print(f"Theta1 (q1): {theta1:.2f}°")
    print(f"Extensión q2: {q2:.4f} m")
    print(f"Extensión q3: {q3:.4f} m")
    
    return theta1, q2, q3

# Ejemplo de uso
x_deseado = 0.0
y_deseado = -0.034
z_deseado = 0.025

articulaciones = cinematica_inversa_RPP(x_deseado, y_deseado, z_deseado)