// Librerías
#include <ESP32Servo.h>
#include <micro_ros_arduino.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int32_multi_array.h>
#include "/home/dax/ROS2DEV/ros2_ws/robot_control/srv/move_robot.h"

// Definición de pines (igual que antes)
#define Step 5
#define Dir 18
#define Enable 19
#define Step2 27
#define Dir2 12
#define Enable2 25
const int FC1 = 32, FC2 = 33, FC3 = 35, FC4 = 34;
const int pinServo = 15;

Servo miServo;
int retardo = 1000, pasos = 0, dir = 0;
int q1 = 0, q2 = 0, q3 = 0;
int q1a = 0, q2a = 0, q3a = 0;

// Variables micro-ROS
rcl_node_t node;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_service_t service;
robot_control__srv__MoveRobot_Request req;
robot_control__srv__MoveRobot_Response res;
rclc_executor_t executor;

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

void error_loop() {
  while(1) {
    delay(100);
  }
}

// Callback del servicio
void move_robot_callback(const void *request, void *response) {
  robot_control__srv__MoveRobot_Request *req_in = (robot_control__srv__MoveRobot_Request *)request;
  robot_control__srv__MoveRobot_Response *res_out = (robot_control__srv__MoveRobot_Response *)response;
  
  // Asignar valores recibidos
  q1 = req_in->q1;
  q2 = req_in->q2;
  q3 = req_in->q3;
  
  // Procesar movimientos
  bool success = true;
  
  if (q2 != q2a) {
    int delta_q2 = q2 - q2a;
    pasos = abs(delta_q2) * 100;
    if (delta_q2 > 0) {
      giro(Step, Dir, Enable, 0, 1);
    } else {
      giro(Step, Dir, Enable, 1, 1);
    }
    q2a = q2;
    pasos = 0;
  }
  
  if(q3 != q3a) {
    int delta_q3 = q3 - q3a;
    pasos = abs(delta_q3) * 100;
    if (delta_q3 > 0) {
      giro(Step2, Dir2, Enable2, 1, 2);
    } else {
      giro(Step2, Dir2, Enable2, 0, 2);
    }
    q3a = q3;
    pasos = 0;
  }
  
  if (q1 != q1a) {
    q1a = q1;
    miServo.write(q1);
  }
  
  // Configurar respuesta
  res_out->success = success;
  res_out->current_q1 = q1a;
  res_out->current_q2 = q2a;
  res_out->current_q3 = q3a;
}

void setup() {
  // Configuración de hardware (igual que antes)
  pinMode(FC1, INPUT); pinMode(FC2, INPUT); pinMode(FC3, INPUT); pinMode(FC4, INPUT);
  pinMode(Step, OUTPUT); pinMode(Dir, OUTPUT); pinMode(Enable, OUTPUT);
  pinMode(Step2, OUTPUT); pinMode(Dir2, OUTPUT); pinMode(Enable2, OUTPUT);
  miServo.attach(pinServo);

  // Inicializar micro-ROS
  set_microros_transports();
  delay(2000);
  
  allocator = rcl_get_default_allocator();
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));
  
  // Crear nodo
  RCCHECK(rclc_node_init_default(&node, "esp32_robot_service", "", &support));
  
  // Crear servicio
  RCCHECK(rclc_service_init_default(
    &service,
    &node,
    ROSIDL_GET_SRV_TYPE_SUPPORT(robot_control, srv, MoveRobot),
    "/robot_control/move_robot"));
  
  // Inicializar executor
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_service(&executor, &service, &req, &res, move_robot_callback));
  
  // Posición home
  home();
}

void loop() {
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)));
}

// Las funciones home() y giro() permanecen igual que en tu código original
void home() {
  pasos = 12000;
  giro(Step2, Dir2, Enable2, 1, 2);
  delay(500);
  giro(Step, Dir, Enable, 1, 1);
  delay(500);
  miServo.write(180);
  delay(500);
  pasos = 0;
  q1a = 180;
  q2a = 0;
  q3a = 80;
}

void giro(int paso_, int dire_, int habi_, int dir_, int nema_) {
  digitalWrite(habi_, LOW);
  bool emergencia = false;

  digitalWrite(dire_, dir_ ? HIGH : LOW);

  for (int i = 0; i < pasos; i++) {
    if (dir_ == 0) {
      if (digitalRead(FC2) == HIGH && nema_ == 1 ) {
        emergencia = true;
        q2 = 70;
      } else if (digitalRead(FC3) == HIGH && nema_ == 2 ) {
        emergencia = true;
        q3 = 0;
      }
    } else {
      if (digitalRead(FC1) == HIGH && nema_ == 1 ) {
        emergencia = true;
        q2 = 0;
      } else if (digitalRead(FC4) == HIGH && nema_ == 2 ) {
        emergencia = true;
        q3 = 80;
      }
    }

    if (emergencia) {
      for (int j = 0; j < 3; j++) {
        digitalWrite(paso_, HIGH);
        delayMicroseconds(100);
        digitalWrite(paso_, LOW);
        delayMicroseconds(100);
      }
      break;
    }

    digitalWrite(paso_, HIGH);
    delayMicroseconds(retardo);
    digitalWrite(paso_, LOW);
    delayMicroseconds(retardo);
  }

  digitalWrite(habi_, HIGH);
}
