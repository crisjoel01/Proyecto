import numpy as np
from math import cos, sin, radians

def cinematica_directa_RPP(theta1, q2, q3):
    """
    Calcula la posición (x,y,z) del efector final
    :param theta1: Ángulo de la junta rotacional en grados [0-180]
    :param q2: Extensión de la primera junta prismática (metros)
    :param q3: Extensión de la segunda junta prismática (metros)
    :return: (x, y, z) posición del efector final en milímetros (enteros)
    """
    q1 = radians(theta1)
    
    # Matrices de transformación
    T1 = np.array([
        [cos(q1), -sin(q1), 0, 0],
        [sin(q1), cos(q1), 0, 0],
        [0, 0, 1, q2 + 87],
        [0, 0, 0, 1]
    ])
    
    T2 = np.array([
        [1, 0, 0, -26],
        [0, 1, 0, -(q3 + 15)],
        [0, 0, 1, -42],
        [0, 0, 0, 1]
    ])
    
    T_total = T1 @ T2
    x, y, z = T_total[0:3, 3]
    x, y, z = int(round(x)), int(round(y)), int(round(z))  # Convertir a enteros
    
    # Imprimir resultados
    print("\nResultados de Cinemática Directa:")
    print(f"Ángulo theta1 (q1): {theta1}°")
    print(f"Extensión q2: {q2} mm")
    print(f"Extensión q3: {q3} mm")
    print(f"\nPosición del efector final:")
    print(f"X: {x} mm")  # Sin decimales
    print(f"Y: {y} mm")  # Sin decimales
    print(f"Z: {z} mm")  # Sin decimales
    
    return x, y, z

# Valores de ejemplo para las articulaciones
q1 = 180    # grados
q2 = 20     # mm
q3 = 40     # mm

# Llamar a la función con los valores de ejemplo
posicion = cinematica_directa_RPP(q1, q2, q3)