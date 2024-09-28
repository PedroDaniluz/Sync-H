#include <Servo.h>

Servo indicador;  // Cria um objeto servo para controlar o servo motor
Servo medio;
Servo anelar;
Servo minimo;
Servo polegar;

int anguloIndicador = 0; // Ângulo para o servo motor
int anguloMedio = 0;
int anguloAnelar = 0;
int anguloMinimo = 0;
int anguloPolegar = 0;

void setup() {
  Serial.begin(9600); // Inicia a comunicação serial
  indicador.attach(3); // Anexa o pino de controle ao servo motor
  medio.attach(5);
  anelar.attach(6);
  minimo.attach(9);
  polegar.attach(10);
}

void loop() {
  // Verifica se há dados disponíveis para leitura
  if (Serial.available() > 0) {
    // Lê a linha de dados recebida
    String dados = Serial.readStringUntil('\n');

    // Divide a string em partes usando a vírgula como delimitador
    int valores[5]; // Temos cinco dedos
    int index = 0;
    int startPos = 0;
    for (int i = 0; i <= dados.length(); i++) {
      // Inclui o caractere final '\0'
      if (dados[i] == ',' || i == dados.length()) {
        String valueString = dados.substring(startPos, i);
        valores[index] = valueString.toInt();
        index++;
        startPos = i + 1;
      }
      // Limita a leitura a 5 valores
      if (index >= 5) {
        break;
      }
    }

    // Verifica se todos os valores foram lidos
    if (index == 5) {
      // Mapeia os valores recebidos de 0-100 para os ângulos correspondentes
      anguloPolegar = map(valores[0], 0, 100, 100, 75);
      anguloIndicador = map(valores[1], 0, 100, 80, 120);
      anguloMedio = map(valores[2], 0, 100, 110, 55);
      anguloAnelar = map(valores[3], 0, 100, 110, 60);
      anguloMinimo = map(valores[4], 0, 100, 135, 70);

      // Move os servos para os ângulos mapeados
      polegar.write(anguloPolegar);
      indicador.write(anguloIndicador);
      medio.write(anguloMedio);
      anelar.write(anguloAnelar);
      minimo.write(anguloMinimo);
    }
  }
}
