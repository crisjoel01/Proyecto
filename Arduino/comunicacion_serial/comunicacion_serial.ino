void setup() {
  Serial.begin(115200);  // Mismo baud rate que en Python
}

void loop() {
  if (Serial.available() > 0) {
    String datos = Serial.readStringUntil('\n');  // Lee hasta salto de línea
    datos.trim();  // Elimina espacios o \r

    // Opción 1: Parseo con separadores "q0:valor,q1:valor"
    int i0 = datos.indexOf("q1:");
    int i1 = datos.indexOf("q2:");
    int i2 = datos.indexOf("q3:");

    if (i0 != -1 && i1 != -1 && i2 != -1) {
      float q1 = datos.substring(i0 + 3, datos.indexOf(',', i0)).toFloat();
      int q2 = datos.substring(i1 + 3, datos.indexOf(',', i1)).toInt();
      String q3 = datos.substring(i2 + 3);

      Serial.print("Recibido -> q1: ");
      Serial.print(q1);
      Serial.print(", q2: ");
      Serial.print(q2);
      Serial.print(", q3: ");
      Serial.println(q3);
    }

    // Opción 2: Parseo simple (valores separados por comas)
    /*
    int separador1 = datos.indexOf(',');
    int separador2 = datos.lastIndexOf(',');
    float q0 = datos.substring(0, separador1).toFloat();
    int q1 = datos.substring(separador1 + 1, separador2).toInt();
    String q2 = datos.substring(separador2 + 1);
    */
  }
}