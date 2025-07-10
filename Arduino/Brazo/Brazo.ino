//Librerias
#include <ESP32Servo.h> //libreria servo

// Pines Nema 17 eje Z
#define Step 27    // Define el Pin de STEP para Motor de eje z
#define Dir 26    // Define el Pin de DIR  para Motor de eje z
#define Enable 25    // Define el Pin de ENABLE  para Motor de eje z

//Pines Nema 17 eje x
#define Step2 5    // Define el Pin de STEP para Motor de eje x
#define Dir2 18    // Define el Pin de DIR  para Motor de eje x
#define Enable2 19    // Define el Pin de ENABLE  para Motor de eje x

// Pines para los finales de carrera (configuración Pull-Down)
const int FC1 = 32;  // GPIO13 zabajo
const int FC2 = 33;  // GPIO12 zarriba
const int FC3 = 35;  // GPIO14 xdentro
const int FC4 = 34;  // GPIO27 xfuera

//Variables Nema
int retardo = 1000;   // Menor numero el giro es mas rapido
int pasos = 1000;   // 100pasos==1mm
int dir = 0; //direcciòn de giro 1->hacia fuera y 0->hacia dentro

//valores q
int q1 = 0; // q de servo
int q2 = 0; // q de eje Z
int q3 = 0; // q de eje X

//Declaraciòn servo
const int pinServo = 15; // Pin GPIO al que está conectado el servo
Servo miServo;

void setup() {

  // Inicializar comunicación serial
  Serial.begin(115200);
  
  // Configurar pines como entradas con Pull-Down interno
  pinMode(FC1, INPUT_PULLDOWN);
  pinMode(FC2, INPUT_PULLDOWN);
  pinMode(FC3, INPUT_PULLDOWN);
  pinMode(FC4, INPUT_PULLDOWN);

  //Inicializaciòn de motores Nema
  pinMode(Step, OUTPUT); pinMode(Dir, OUTPUT); pinMode(Enable, OUTPUT); //Nema Z
  pinMode(Step2, OUTPUT); pinMode(Dir2, OUTPUT); pinMode(Enable2, OUTPUT);  //Nema X

  //Inicializaciòn del motor servo
  miServo.attach(pinServo);

}    

void loop() {
  miServo.write(0);
  delay(1000);
  //giro(Step,Dir,Enable,0);
  //delay(1000);
  giro(Step2,Dir2,Enable2,1);
  delay(1000);
  //giro(Step,Dir,Enable,0);
  //delay(1000);
  giro(Step2,Dir2,Enable2,0);
  delay(1000);
  
}

void pos0(){
   
}
void giro(int paso_,int dire_,int habi_,int dir_) {
  digitalWrite(habi_, LOW);  // Habilita el Driver
  if(dir_ == 0){ // extremo fuera eje
    digitalWrite(dire_, LOW);   // direccion de giro 0
    while (FC1==0 && FC4==0){ // condiciòn de finales de carrera externos
      for(int i=0; i<pasos; i++){  // da  pasos por un tiempo  
        digitalWrite(paso_, HIGH);      
        delayMicroseconds(retardo);          
        digitalWrite(paso_, LOW);       
        delayMicroseconds(retardo); 
      }
    } 
  }
  if(dir_ == 1){ // extremo dentro eje
    digitalWrite(dire_, HIGH);   // direccion de giro 1
    while (FC2==0 && FC3==0){ // condiciòn de finales de carrera internos
      for(int i=0; i<pasos; i++){   // da  pasos por un tiempo  
        digitalWrite(paso_, HIGH);      
        delayMicroseconds(retardo);          
        digitalWrite(paso_, LOW);       
        delayMicroseconds(retardo);  
      }
    }
  }
  digitalWrite(habi_, HIGH);   // quita la habilitacion del Driver
}