
// Pines Nema 17 eje Z
#define Step 27    // Define el Pin de STEP para Motor de eje z
#define Dir 14    // Define el Pin de DIR  para Motor de eje z
#define Enable 12    // Define el Pin de ENABLE  para Motor de eje z

int retardo = 1000;   // Menor numero el giro es mas rapido
int tiempo = 1000;   // durante cuanto timpo da el giro el motor (vueltas)

void setup() {
pinMode(Step, OUTPUT); pinMode(Dir, OUTPUT); pinMode(Enable, OUTPUT);     
}    

void loop() {
  giro(Step,Dir,Enable,1);
  delay(1000);
  giro(Step,Dir,Enable,0);
  delay(1000);
}


void giro(int paso_,int dire_,int habi_,int dir) {
  digitalWrite(habi_, LOW);  // Habilita el Driver
  if( dir==0){ // Bajar eje
   digitalWrite(dire_, LOW);   // direccion de giro 0
   for(int i=0;i<tiempo;i++){  // da  pasos por un tiempo  
    digitalWrite(paso_, HIGH);      
    delayMicroseconds(retardo);          
    digitalWrite(paso_, LOW);       
    delayMicroseconds(retardo); 
   }
  }
  if( dir==1){ // Subir eje
  digitalWrite(dire_, HIGH);   // direccion de giro 1
  for(int i=0;i<tiempo;i++){   // da  pasos por un tiempo  
    digitalWrite(paso_, HIGH);      
    delayMicroseconds(retardo);          
    digitalWrite(paso_, LOW);       
    delayMicroseconds(retardo);  
   }
  }
  digitalWrite(habi_, HIGH);   // quita la habilitacion del Driver

}