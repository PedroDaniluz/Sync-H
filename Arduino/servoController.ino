#include <Servo.h>

Servo meuServo;  // Cria um objeto servo para controlar o servo motor

const int pinoServo = 3; // Pino de controle do servo motor
int valorRecebido = 0; // Valor recebido do Python (índice 1 da lista)
int angulo = 0; // Ângulo para o servo motor

void setup() {
  Serial.begin(9600); // Inicia a comunicação serial
  meuServo.attach(pinoServo); // Anexa o pino de controle ao servo motor
}

void loop() {
  // Verifica se há dados disponíveis para leitura
  if (Serial.available() > 0) {
    // Lê a linha de dados recebida
    String dados = Serial.readStringUntil('\n');
    
    // Divide a string em partes usando a vírgula como delimitador
    int index = 0;
    int valor = 0;
    for (int i = 0; i < dados.length(); i++) {
      if (dados[i] == ',') {
        index++;
      } else {
        if (index == 1) {
          valor = valor * 10 + (dados[i] - '0');
        }
      }
    }
    
    // Mapeia o valor recebido de 0-100 para 0-180 graus
    angulo = map(valor, 0, 100, 50, 100);
    
    // Move o servo para o ângulo mapeado
    meuServo.write(angulo);
  }
}
