import serial
import time
import cv2
import mediapipe as mp
import numpy as np

# Inicializa a comunicação serial -> UTILIZE A PORTA 'COM' CORRESPONDENTE
arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)

# Inicializa o MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Função para calcular distâncias entre dois pontos
def calc_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

# Função para calcular a abertura dos dedos usando distâncias e verificação de posição
def calc_opening_dist(landmarks):
    distances = []
    
    # Coordenada X do punho (landmark 0) - tratamento especial do polegar
    fist_x = landmarks[0][0]
    
    # Calcular a abertura do polegar usando a distância horizontal (eixo X) entre a ponta do polegar e o punho
    horizontal_distance_thumb = abs(landmarks[4][0] - fist_x)  # Apenas diferença no eixo X
    thumb_opening = min(100, max(0, int((horizontal_distance_thumb / 0.2) * 100)))  # Normaliza para 0-100
    distances.append(thumb_opening)

    # Calcular a abertura dos outros dedos (indicador, médio, anelar, mindinho)
    fingers = [(8, 5), (12, 9), (16, 13), (20, 17)]  # Ponta e base dos dedos

    for tip, base in fingers:
        # Verificar se a ponta do dedo está abaixo da base (eixo Y)
        if landmarks[tip][1] >= landmarks[base][1]:  # Coordenada Y da ponta >= base
            finger_opening = 0
        else:
            finger_distance = calc_distance(landmarks[tip], landmarks[base])
            finger_opening = min(100, max(0, int((finger_distance / 0.2) * 100)))  # Normaliza para 0-100
        distances.append(finger_opening)
    
    return distances

def sendList(aberturaDedos: list, arduino: serial.Serial) -> None:
    mensagem = ','.join(map(str, aberturaDedos))
    arduino.write((mensagem + '\n').encode()) 

# Capturando a imagem da webcam
cap = cv2.VideoCapture(0)

# Verifica se a câmera foi aberta corretamente
if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

# Controle para o intervalo de envio de dados
last_sent_time = time.time()
send_interval = .075  # Intervalo de envio de dados em segundos

while True:
    success, image = cap.read()
    
    if not success:
        print("Erro ao capturar a imagem da câmera.")
        continue
    
    # Convertendo a imagem de BGR para RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Processando a imagem com o MediaPipe
    result = hands.process(image_rgb)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Obtendo os landmarks da mão
            landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            
            # Calculando a abertura dos dedos usando distâncias e verificando a posição
            finger_opening = calc_opening_dist(landmarks)
            
            # Controle para enviar dados a cada intervalo especificado
            current_time = time.time()
            if current_time - last_sent_time > send_interval:
                sendList(finger_opening, arduino)
                last_sent_time = current_time
            
            # Exibir os valores de abertura dos dedos na tela
            for idx, abertura in enumerate(finger_opening):
                cv2.putText(image, f'Dedo {idx+1}: {abertura}', (10, 30 + idx * 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Exibindo a imagem com os landmarks desenhados
    cv2.imshow('MediaPipe Hands', image)

    # Processa eventos da janela OpenCV, como fechamento da janela
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
