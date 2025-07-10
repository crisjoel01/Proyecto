// Pines para los finales de carrera (configuración Pull-Down)
const int finalCarrera1 = 32;  // GPIO13 zabajo
const int finalCarrera2 = 33;  // GPIO12 zarriba
const int finalCarrera3 = 35;  // GPIO14 xdentro
const int finalCarrera4 = 34;  // GPIO27 xfuera

void setup() {
  // Inicializar comunicación serial
  Serial.begin(115200);
  
  // Configurar pines como entradas con Pull-Down interno
  pinMode(finalCarrera1, INPUT_PULLDOWN);
  pinMode(finalCarrera2, INPUT_PULLDOWN);
  pinMode(finalCarrera3, INPUT_PULLDOWN);
  pinMode(finalCarrera4, INPUT_PULLDOWN);
  
  Serial.println("Iniciando prueba de finales de carrera (Pull-Down)...");
  Serial.println("Estado de los finales de carrera (1 = pulsado, 0 = libre):");
}

void loop() {
  // Leer el estado de los finales de carrera
  int estado1 = digitalRead(finalCarrera1);
  int estado2 = digitalRead(finalCarrera2);
  int estado3 = digitalRead(finalCarrera3);
  int estado4 = digitalRead(finalCarrera4);
  
  // Mostrar estados por el monitor serial
  Serial.print("FC1: ");
  Serial.print(estado1);
  Serial.print(" | FC2: ");
  Serial.print(estado2);
  Serial.print(" | FC3: ");
  Serial.print(estado3);
  Serial.print(" | FC4: ");
  Serial.println(estado4);
  
  // Pequeña pausa para no saturar el puerto serial
  delay(500);
}