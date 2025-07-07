#include <ESP32Servo.h>

// ===================================================================
// ==================== SECCIÓN DE VARIABLES =========================
// ===================================================================

// ---------------- Variables para el Servo ----------------
int anguloServo = 0;   // Ángulo inicial del servo (0 grados)
const int anguloMaxServo = 180; // Ángulo máximo del servo

// ---------------- Variables de velocidad y duración ----------------
int retardo = 1000;    // Retardo entre pasos (velocidad). Menor valor = más rápido
int pasosMax = 50000;  // Paso máximo para homing o movimientos largos (seguridad)

// ---------------- Pines de finales de carrera ----------------
#define Limit_Z_Inicio 32
#define Limit_Z_Final  33

#define Limit_X_Inicio 34
#define Limit_X_Final  35

// ===================================================================
// ==================== DEFINICIÓN DE PINES ==========================
// ===================================================================

// Motor NEMA 17 - eje Z (vertical)
#define Step_Z 27
#define Dir_Z 14
#define Enable_Z 4

// Motor NEMA 17 - eje X (horizontal)
#define Step_X 25
#define Dir_X 26
#define Enable_X 13

// Servo
Servo miServo;
const int pinServo = 2;

// ===================================================================
// ==================== CONFIGURACIÓN INICIAL ========================
// ===================================================================

void setup() {
  // Configuración pines motores
  pinMode(Step_Z, OUTPUT);
  pinMode(Dir_Z, OUTPUT);
  pinMode(Enable_Z, OUTPUT);

  pinMode(Step_X, OUTPUT);
  pinMode(Dir_X, OUTPUT);
  pinMode(Enable_X, OUTPUT);

  // Pines finales de carrera con resistencia pull-up interna
  pinMode(Limit_Z_Inicio, INPUT_PULLUP);
  pinMode(Limit_Z_Final, INPUT_PULLUP);
  pinMode(Limit_X_Inicio, INPUT_PULLUP);
  pinMode(Limit_X_Final, INPUT_PULLUP);

  // Inicializa servo
  miServo.attach(pinServo);

  // Inicializa comunicación serial
  Serial.begin(115200);
  Serial.println("Iniciando sistema...");

  // Ejecuta posicion inicial al energizar
  posicionInicial();
}

// ===================================================================
// ==================== FUNCIONES AUXILIARES =========================
// ===================================================================

// Función para mover motor paso a paso con protección contra finales de carrera
// Mueve hasta 'pasosMax' pasos o hasta que final de carrera correspondiente se active
// direccionMovimiento: 0 = hacia inicio, 1 = hacia final
void moverMotorConFinales(int pinStep, int pinDir, int pinEnable, int direccionMovimiento, int pinLimitInicio, int pinLimitFinal, int pasosMax) {
  digitalWrite(pinEnable, LOW);  // Habilita el driver

  // Define la dirección del motor según la dirección solicitada
  digitalWrite(pinDir, direccionMovimiento == 0 ? LOW : HIGH);

  int pasosRealizados = 0;

  // Mueve el motor mientras el final de carrera no esté activado y no se exceda el máximo de pasos
  while (pasosRealizados < pasosMax) {
    // Chequea final de carrera según dirección
    if (direccionMovimiento == 0 && digitalRead(pinLimitInicio) == LOW) {
      Serial.println("Final de carrera INICIO activado, deteniendo motor.");
      break;
    }
    if (direccionMovimiento == 1 && digitalRead(pinLimitFinal) == LOW) {
      Serial.println("Final de carrera FINAL activado, deteniendo motor.");
      break;
    }

    // Da un paso
    digitalWrite(pinStep, HIGH);
    delayMicroseconds(retardo);
    digitalWrite(pinStep, LOW);
    delayMicroseconds(retardo);

    pasosRealizados++;
  }

  digitalWrite(pinEnable, HIGH);  // Deshabilita el driver
  Serial.print("Pasos realizados: ");
  Serial.println(pasosRealizados);
}

// Función para posicionar el brazo robótico en posición inicial al encender
// Coloca servo en 0°, baja eje Z hasta final de carrera inicio, retrocede eje X hasta final de carrera inicio
void posicionInicial() {
  Serial.println("Ejecutando posición inicial...");

  // Posiciona servo en 0 grados
  miServo.write(0);
  delay(1000);

  // Baja eje Z hasta activar final de carrera inicio (posición más baja)
  Serial.println("Bajando eje Z hasta posición inicial...");
  moverMotorConFinales(Step_Z, Dir_Z, Enable_Z, 0, Limit_Z_Inicio, Limit_Z_Final, pasosMax);

  delay(500);

  // Retrocede eje X hasta activar final de carrera inicio (posición más cerca del motor)
  Serial.println("Retrocediendo eje X hasta posición inicial...");
  moverMotorConFinales(Step_X, Dir_X, Enable_X, 0, Limit_X_Inicio, Limit_X_Final, pasosMax);

  delay(500);

  Serial.println("Posición inicial completada.");
}

// ===================================================================
// ==================== LOOP PRINCIPAL ===============================
// ===================================================================

void loop() {
  // Revisa si hay datos recibidos por serial
  if (Serial.available() > 0) {
    char comando = Serial.read();

    switch (comando) {
      case 'W': // Subir motor Z hasta final de carrera final
      case 'w':
        Serial.println("Comando recibido: Subir eje Z");
        moverMotorConFinales(Step_Z, Dir_Z, Enable_Z, 1, Limit_Z_Inicio, Limit_Z_Final, pasosMax);
        break;

      case 'S': // Bajar motor Z hasta final de carrera inicio
      case 's':
        Serial.println("Comando recibido: Bajar eje Z");
        moverMotorConFinales(Step_Z, Dir_Z, Enable_Z, 0, Limit_Z_Inicio, Limit_Z_Final, pasosMax);
        break;

      case 'A': // Avanzar motor X hasta final de carrera final
      case 'a':
        Serial.println("Comando recibido: Avanzar eje X");
        moverMotorConFinales(Step_X, Dir_X, Enable_X, 1, Limit_X_Inicio, Limit_X_Final, pasosMax);
        break;

      case 'D': // Retroceder motor X hasta final de carrera inicio
      case 'd':
        Serial.println("Comando recibido: Retroceder eje X");
        moverMotorConFinales(Step_X, Dir_X, Enable_X, 0, Limit_X_Inicio, Limit_X_Final, pasosMax);
        break;

      // Control de servo con números 0 a 9 (de 0° a 90° en pasos de 10 grados)
      case '0': case '1': case '2': case '3': case '4':
      case '5': case '6': case '7': case '8': case '9':
        {
          int valor = comando - '0';  // Convierte char a int (0 a 9)
          int angulo = map(valor, 0, 9, 0, anguloMaxServo); // Mapea a 0 - 180 grados
          Serial.print("Comando recibido: Mover servo a ");
          Serial.print(angulo);
          Serial.println(" grados");
          miServo.write(angulo);
          break;
        }

      default:
        Serial.print("Comando no reconocido: ");
        Serial.println(comando);
        break;
    }
  }
}
