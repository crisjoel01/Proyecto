import numpy as np
from math import cos, sin, radians

def cinematica_inversa_RPP(x, y, z):
    """
    Calcula los valores de las articulaciones para alcanzar (x,y,z)
    :return: (theta1, q2, q3) - ángulo en grados (entero) y extensiones en milímetros (enteros)
    """
    # Cálculo de theta1 (limitado a -90 a 90°)
    theta1 = np.degrees(np.arccos(-(y * np.sqrt(x**2 + y**2 - 676) + 26*x)/(x**2 + y**2)))
    theta1 = int(max(0, min(180, theta1)))  # Limitar al rango del servo y convertir a entero
    
    # Cálculo de q2 (altura)
    q2 = z - 45
    q2 = int(max(0, q2))  # No puede ser negativo y convertir a entero
    
    # Cálculo de q3 (radio)
    r = np.sqrt(x**2 + y**2 - 676) - 15
    q3 = int(max(0, r))  # No puede ser negativo y convertir a entero
    
    print("\nResultados de Cinemática Inversa:")
    print(f"Posición deseada: X={x:.3f} mm, Y={y:.3f} mm, Z={z:.3f} mm")
    print(f"\nValores de articulaciones calculados:")
    print(f"q1: {theta1}°")  # Se imprime como entero
    print(f"q2: {q2} mm")    # Se imprime como entero
    print(f"q3: {q3} mm")    # Se imprime como entero
    
    return theta1, q2, q3

# Ejemplo de uso
x = 26
y = 55
z = 65

articulaciones = cinematica_inversa_RPP(x, y, z)