//Librerias
#include <ESP32Servo.h> //libreria servo

// Pines Nema 17 eje Z
#define Step 5    // Define el Pin de STEP para Motor de eje z
#define Dir 18    // Define el Pin de DIR  para Motor de eje z
#define Enable 19    // Define el Pin de ENABLE  para Motor de eje z

//Pines Nema 17 eje x
#define Step2 27    // Define el Pin de STEP para Motor de eje x
#define Dir2 12    // Define el Pin de DIR  para Motor de eje x
#define Enable2 25    // Define el Pin de ENABLE  para Motor de eje x

// Pines para los finales de carrera (configuración Pull-Down)
const int FC1 = 32;  // GPIO13 zabajo
const int FC2 = 33;  // GPIO12 zarriba
const int FC3 = 35;  // GPIO14 xdentro
const int FC4 = 34;  // GPIO27 xfuera

//Declaraciòn servo
const int pinServo = 15; // Pin GPIO al que está conectado el servo
Servo miServo;

// Variables de finales de carrera
int estado1 = 0;
int estado2 = 0;
int estado3 = 0;
int estado4 = 0;

//Variables Nema
int retardo = 1000;   // Menor numero el giro es mas rapido
int pasos = 0;   // 100pasos==1mm
int dir = 0; //direcciòn de giro 1->hacia fuera y 0->hacia dentro

//valores q
int q1 = 0; // q de servo
int q2 = 0; // q de eje Z
int q3 = 0; // q de eje X

//q anteriores
int q1a = 0;
int q2a = 0;
int q3a = 0;

void setup() {

  // Inicializar comunicación serial
  Serial.begin(115200);
  delay(1000);  // Pequeña pausa para estabilizar
  Serial.println("ESP32 iniciada");  // Mensaje de prueba
  
  // Configurar pines como entradas con Pull-Down interno
  pinMode(FC1, INPUT);
  pinMode(FC2, INPUT);
  pinMode(FC3, INPUT);
  pinMode(FC4, INPUT);

  //Inicializaciòn de motores Nema
  pinMode(Step, OUTPUT); pinMode(Dir, OUTPUT); pinMode(Enable, OUTPUT); //Nema Z
  pinMode(Step2, OUTPUT); pinMode(Dir2, OUTPUT); pinMode(Enable2, OUTPUT);  //Nema X

  //Inicializaciòn del motor servo
  miServo.attach(pinServo);

  //posiciòn home
  home();
}    

void loop() {

  //Comunicaciòn serial
  if (Serial.available() > 0) {
    String datos = Serial.readStringUntil('\n');  // Lee hasta salto de línea
    datos.trim();  // Elimina espacios o \r

    // Opción 1: Parseo con separadores "q0:valor,q1:valor"
    int i0 = datos.indexOf("q1:");
    int i1 = datos.indexOf("q2:");
    int i2 = datos.indexOf("q3:");

    if (i0 != -1 && i1 != -1 && i2 != -1) {
      int q1 = datos.substring(i0 + 3, datos.indexOf(',', i0)).toInt();
      int q2 = datos.substring(i1 + 3, datos.indexOf(',', i1)).toInt();
      int q3 = datos.substring(i2 + 3).toInt();

      Serial.print("Recibido -> q1: ");
      Serial.print(q1);
      Serial.print(", q1a: ");
      Serial.print(q1a);
      Serial.print(", q2: ");
      Serial.print(q2);
      Serial.print(", q2a: ");
      Serial.print(q2a);
      Serial.print(", q3: ");
      Serial.print(q3);
      Serial.print(", q3a: ");
      Serial.println(q3a);

      // Càlculo de pasos
      if (q2 != q2a){
        q2 = q2-q2a; //càlculo de mm a mover
        if (q2 > 0) {  // desplazamiento positivo
          pasos = q2*100; //cálculo de pasos a ejecutar
          giro(Step,Dir,Enable,0,1);
          delay(500);
        }else if (q2 < 0) { // desplazamiento negativo
          pasos = abs(q2)*100;
          giro(Step,Dir,Enable,1,1);
          delay(500);
        } 
        Serial.print("Desplazamiento -> q2: ");
        Serial.print(q2);
        Serial.print(", pasos: ");
        Serial.println(pasos);
        q2a = q2a + q2; //Valor actual es el anterior del siguiente
        pasos=0;
      }
      if(q3 != q3a){
        q3 = q3-q3a;
        if (q3 > 0) {  // desplazamiento positivo
          pasos = q3*100;
          giro(Step2,Dir2,Enable2,1,2);
          delay(500);
        }else if (q3 < 0) { // desplazamiento negativo
          pasos = abs(q3)*100;
          giro(Step2,Dir2,Enable2,0,2);
          delay(500);
        }
        Serial.print("Desplazamiento -> q3: ");
        Serial.print(q3);
        Serial.print(", pasos: ");
        Serial.println(pasos);
        q3a = q3a + q3;
        pasos=0;
      }
      if (q1 != q1a){
        q1a = q1;
        miServo.write(q1);
        delay(500);
        Serial.print("Desplazamiento -> q1: ");
        Serial.println(q1);
      }
    }
  }
}

void home(){
  pasos = 12000;
  
  giro(Step2,Dir2,Enable2,1,2);
  delay(500);
  giro(Step,Dir,Enable,1,1);
  delay(500);
  miServo.write(0);
  delay(500);
  pasos = 0;
  q1a = 0;
  q2a = 0;
  q3a = 80;
}

void giro(int paso_, int dire_, int habi_, int dir_, int nema_) {
  digitalWrite(habi_, LOW);  // Habilita el motor
  bool emergencia = false;   // Bandera de parada

  // Configura dirección
  digitalWrite(dire_, dir_ ? HIGH : LOW);

  for (int i = 0; i < pasos; i++) {
    // Verificación ACTIVA de finales de carrera (adaptada a tus pines)
    if (dir_ == 0) { // Dirección 0 (FC2 o FC3 deben parar)
      if (digitalRead(FC2) == HIGH && nema_ == 1 ) {
        emergencia = true;
        q2 = 70;
        Serial.println("ALTO: FC2 activado (dirección 0)");
      }else if (digitalRead(FC3) == HIGH && nema_ == 2 ){
        emergencia = true;
        q3 = 0;
        Serial.println("ALTO: FC3 activado (dirección 0)");
      }
    } 
    else { // Dirección 1 (FC1 o FC4 deben parar)
      if (digitalRead(FC1) == HIGH && nema_ == 1 ) {
        emergencia = true;
        q2 = 0;
        Serial.println("ALTO: FC1 activado (dirección 1)");
      }else if (digitalRead(FC4) == HIGH && nema_ == 2 ){
        emergencia = true;
        q3 = 80;
        Serial.println("ALTO: FC4 activado (dirección 1)");
      }
    }

    // Si hay emergencia: freno inmediato
    if (emergencia) {
      for (int j = 0; j < 3; j++) { // Freno de emergencia (3 pasos rápidos)
        digitalWrite(paso_, HIGH);
        delayMicroseconds(100);  // Pulso ultra corto
        digitalWrite(paso_, LOW);
        delayMicroseconds(100);
      }
      break; // Sale del bucle principal
    }

    // Paso normal (solo si no hay emergencia)
    digitalWrite(paso_, HIGH);
    delayMicroseconds(retardo);
    digitalWrite(paso_, LOW);
    delayMicroseconds(retardo);
  }

  digitalWrite(habi_, HIGH); // Deshabilita el motor
  if (emergencia) {
    Serial.println("Motor detenido por emergencia");
  }
}