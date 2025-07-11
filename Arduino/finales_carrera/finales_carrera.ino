// Pines para los finales de carrera (configuración Pull-Down)
const int FC1 = 32;  // GPIO13 zabajo
const int FC2 = 33;  // GPIO12 zarriba
const int FC3 = 35;  // GPIO14 xdentro
const int FC4 = 34;  // GPIO27 xfuera

void setup() {
  // Inicializar comunicación serial
  Serial.begin(115200);
  
  // Configurar pines como entradas con Pull-Down interno
  pinMode(FC1, INPUT);
  pinMode(FC2, INPUT);
  pinMode(FC3, INPUT);
  pinMode(FC4, INPUT);
  
  Serial.println("Iniciando prueba de finales de carrera (Pull-Down)...");
  Serial.println("Estado de los finales de carrera (1 = pulsado, 0 = libre):");
}

void loop() {
  
  Serial.println("Probando finales de carrera...");
  Serial.print("FC1: "); Serial.println(digitalRead(FC1));
  Serial.print("FC2: "); Serial.println(digitalRead(FC2));
  Serial.print("FC3: "); Serial.println(digitalRead(FC3));
  Serial.print("FC4: "); Serial.println(digitalRead(FC4));
  delay(1000);
}
