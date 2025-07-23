import cv2
import numpy as np
from pupil_apriltags import Detector
import math
import time
from collections import deque, defaultdict

def rotation_matrix_to_euler_angles(R):
    sy = math.sqrt(R[0, 0]**2 + R[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.degrees([x, y, z])

def promedio_lista(vectores):
    return np.mean(np.array(vectores), axis=0)

def main():
    # 🔁 Reemplaza esta URL con la de tu cámara IP
    ip_cam_url = "http://10.40.27.211:8080/video"
    cap = cv2.VideoCapture(ip_cam_url)

    if not cap.isOpened():
        print("❌ No se pudo acceder a la cámara IP.")
        return

    # 📷 Cargar parámetros de calibración
    with np.load('parametros_calibracion.npz') as X:
        camera_matrix, dist_coeffs = X['mtx'], X['dist']

    tag_size = 0.075  # Tamaño del tag en metros (7.5 cm)

    detector = Detector(
        families='tag36h11',
        nthreads=1,
        quad_decimate=0.5,
        quad_sigma=0.8,
        refine_edges=False,
        decode_sharpening=0.25,
        debug=False
    )

    objetos = {1: "CARRO", 2: "OBJETO 1", 3: "OBJETO 2", 4: "OBJETO 3"}
    ubicaciones = {5: "UBICACIÓN 1", 6: "UBICACIÓN 2", 7: "UBICACIÓN 3", 8: "UBICACIÓN 4"}

    window_name = 'Detección con Tag 9 como origen'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    print_interval = 5  # segundos
    last_print_time = time.time()

    pose_hist = defaultdict(lambda: deque(maxlen=5))
    origen = None

    print("📡 Sistema activo. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ No se pudo leer el frame desde la cámara.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=(camera_matrix[0, 0], camera_matrix[1, 1],
                           camera_matrix[0, 2], camera_matrix[1, 2]),
            tag_size=tag_size
        )

        for detection in detections:
            tag_id = detection.tag_id
            corners = detection.corners.astype(int)
            center = (int(detection.center[0]), int(detection.center[1]))

            cv2.polylines(frame, [corners], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            texto = f"ID: {tag_id}"
            color = (0, 0, 0)

            if tag_id in objetos:
                color = (255, 0, 0)
                texto = f"{objetos[tag_id]} (ID: {tag_id})"
                cv2.rectangle(frame, (corners[0][0]-10, corners[0][1]-30),
                              (corners[2][0]+10, corners[2][1]+10), color, 2)
            elif tag_id in ubicaciones:
                color = (0, 255, 255)
                texto = f"{ubicaciones[tag_id]} (ID: {tag_id})"
                radius = int(max(abs(corners[0][0] - corners[2][0]),
                                 abs(corners[0][1] - corners[2][1])) // 2)
                cv2.circle(frame, center, radius, color, 2)

            cv2.putText(frame, texto, (corners[0][0], corners[0][1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            t = detection.pose_t.ravel()
            R = detection.pose_R
            euler = rotation_matrix_to_euler_angles(R)

            pose_hist[tag_id].append((t, euler))

            if tag_id == 9:
                origen = promedio_lista([p[0] for p in pose_hist[9]])

        if time.time() - last_print_time >= print_interval:
            last_print_time = time.time()

            for tag_id, data in pose_hist.items():
                posiciones = [p[0] for p in data]
                rotaciones = [p[1] for p in data]

                if posiciones and rotaciones:
                    t_avg = promedio_lista(posiciones)
                    euler_avg = promedio_lista(rotaciones)

                    if origen is not None:
                        t_corr = np.array([
                            t_avg[0] - origen[0],
                            t_avg[1] - origen[1]
                        ])
                    else:
                        t_corr = t_avg[:2]

                    t_cm = np.round(t_corr * 100, 1)
                    euler_deg = np.round(euler_avg, 2)

                    print(f"\n📍 TAG ID {tag_id}")
                    print(f"📏 Posición relativa [x, y] en cm: {t_cm}")
                    print(f"🔄 Rotación [roll, pitch, yaw] en grados: {euler_deg}")

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Sistema cerrado.")

if __name__ == '__main__':
    main()
