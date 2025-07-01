// para la librermadhephaestus
#include <ESP32Servo.h>

Servo miServo;

const int pinServo = 15; // Pin GPIO al que está conectado el servo

void setup() 
{
  miServo.attach(pinServo);
}

void loop() 
{
  miServo.write(0);    // Mover el servo a 0 grados

}