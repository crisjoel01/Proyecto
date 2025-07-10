// para la librermadhephaestus
#include <ESP32Servo.h>

Servo miServo;

const int pinServo = 15; // Pin GPIO al que está conectado el servo

void setup() 
{
  miServo.attach(pinServo);
}

void loop() {
  // Mueve el servo de 0° a 180° en pasos de 1°
  for (int pos = 0; pos <= 180; pos++) {
    miServo.write(pos);  // Establece la posición
    delay(15);  // Espera para que el servo llegue a la posición
    Serial.print("Posición: ");
    Serial.println(pos);
  }

  delay(1000);  // Espera 1 segundo

  // Mueve el servo de 180° a 0° en pasos de 1°
  for (int pos = 180; pos >= 0; pos--) {
    miServo.write(pos);
    delay(15);
    Serial.print("Posición: ");
    Serial.println(pos);
  }

  delay(1000);  // Espera 1 segundo antes de repetir
}