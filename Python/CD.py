import numpy as np
from math import cos, sin, radians

def cinematica_directa_RPP(theta1, q2, q3, a=0, b=0):
    """
    Calcula la posición (x,y,z) del efector final
    :param theta1: Ángulo de la junta rotacional en grados [0-180]
    :param q2: Extensión de la primera junta prismática (metros)
    :param q3: Extensión de la segunda junta prismática (metros)
    :param A: Radio de la base (metros)
    :param B: Altura inicial del primer eslabón (metros)
    :return: (x, y, z) posición del efector final
    """
    q1 = radians(theta1)
    
    # Matrices de transformación
    # Junta rotacional (R)
    T1 = np.array([
        [cos(q1), -sin(q1), 0, 0],
        [sin(q1), cos(q1), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    # Primera junta prismática (P)
    T2 = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, q2+a],
        [0, 0, 0, 1]
    ])
    
    # Segunda junta prismática (P)
    T3 = np.array([
        [1, 0, 0, q3+b],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    T_total = T1 @ T2 @ T3
    x, y, z = T_total[0:3, 3]
    # Imprimir resultados
    print("\nResultados de Cinemática Directa:")
    print(f"Ángulo theta1 (q1): {theta1}°")
    print(f"Extensión q2: {q2} m")
    print(f"Extensión q3: {q3} m")
    print(f"\nPosición del efector final:")
    print(f"X: {x:.4f} m")
    print(f"Y: {y:.4f} m")
    print(f"Z: {z:.4f} m")
    
    return x, y, z

# Valores de ejemplo para las articulaciones
q1_angulo = -90    # grados
q2_extension = 0.025  # mm
q3_extension = 0.034  # mm

# Llamar a la función con los valores de ejemplo
posicion = cinematica_directa_RPP(q1_angulo, q2_extension, q3_extension)