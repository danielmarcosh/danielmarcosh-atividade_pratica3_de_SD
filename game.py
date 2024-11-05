import turtle
import paho.mqtt.client as paho

import random
import json

# Configuração do broker MQTT
BROKER = "localhost" 
PORT = 1883

# Distância de movimento 
MOVE_DISTANCE = 20 

# Limites da tela 
WIDTH = 800 
HEIGHT = 600 

TIME_TO_LIVE = 60

# Inicialização do cliente MQTT
client_pub= paho.Client(paho.CallbackAPIVersion.VERSION1, "admin")
client_sub = paho.Client()

# Função para gerar cores hexadecimais aleatórias 
def random_color(): 
    return f'#{random.randint(0, 0xFFFFFF):06x}'

# ID do dispositivo 
DISP_ID = random.randint(1, 500)
player_color = random_color()

# Callback para quando uma mensagem for publicada
def on_publish(client_pub, userdata, mid): 
    print(f"Dispositivo ID: {DISP_ID} - Dados publicados.")

# Callback para quando o cliente se conectar ao broker
def on_connect(client_sub, userdata, flags, rc):
    print("Connected with result code "+ str(rc))
    client_sub.subscribe("/data")

# Callback para quando uma mensagem for recebida
def on_message(client_sub, userdata, msg):
    # Decodificar a mensagem de payload para uma string
    payload_str = msg.payload.decode()

    try:
        # Tentar converter a string JSON para um objeto Python (dicionário)
        data = json.loads(payload_str)
        print(f"Mensagem recebida: {data}")
        # Iterar sobre o dicionário para mostrar o ID e os valores
        key = data.get('id')   # Obter o id
        value = data.get('coords')  # Obter as coordenadas
        color = data.get('color')  # Obter a cor
        angle = data.get('angle')  # Obter o angulo
        print(f"Dispositivo ID: {key}. Publicou os valores: {value} e a cor {color}")
        if int(key) != DISP_ID:
            print(f"Entrou key: {key}. DISP_ID: {DISP_ID}")
            update_remote_turtle(key, value, color, angle)
    except json.JSONDecodeError:
        # Caso o payload não seja um JSON válido, apenas imprime a string
        print(f"Mensagem recebida: {payload_str}")

# Publish
client_pub.on_publish = on_publish
client_pub.connect(BROKER, PORT)
client_pub.loop_start()
# Subscribe
client_sub.connect(BROKER,PORT,TIME_TO_LIVE)
client_sub.on_connect = on_connect
client_sub.on_message = on_message
client_sub.loop_start()

# Configuração da tela
wn = turtle.Screen()
wn.title("Move Game by @Garrocho")
wn.bgcolor("green")
# wn.setup(width=1.0, height=1.0, startx=None, starty=None)
wn.setup(width=WIDTH, height=HEIGHT, startx=None, starty=None)
# wn.tracer(0) # Desativa atualizações automáticas da tela

# Inicialização Turtle
head = turtle.Turtle()
head.speed(0)
head.shape("turtle")
head.color(player_color)
head.penup()
head.goto(0, 0)

# Dicionário para armazenar turtles remotas 
remote_turtles = {}

# Limites da área de movimento
max_x = wn.window_width() // 2 - 20
max_y = wn.window_height() // 2 - 20

def update_coordinates(): 
    x_cor = head.xcor() 
    y_cor = head.ycor() 
    
    ang = head.heading()

    # Criar o objeto Python (um dicionário)
    message = { 
        "id": DISP_ID, 
        "coords": [x_cor, y_cor], 
        "color": player_color ,
        "angle": ang
    }

    # Converter o dicionário Python para JSON
    message_json = json.dumps(message)

    # Publicar a mensagem JSON no tópico MQTT
    client_pub.publish("/data", message_json)

def update_remote_turtle(disp_id, coords, color, angle): 
    if disp_id not in remote_turtles: 
        remote_turtle = turtle.Turtle() 
        remote_turtle.speed(0) 
        remote_turtle.shape("turtle") 
        remote_turtle.color(color) 
        remote_turtle.penup() 
        remote_turtles[disp_id] = remote_turtle 
    else: 
        remote_turtle = remote_turtles[disp_id]
    # Atualizar a posição da tartaruga remota
    remote_turtle.goto(coords[0], coords[1])
    remote_turtle.setheading(angle)

# Functions
def go_up():
    head.setheading(90)
    if head.ycor() < max_y:
        y = head.ycor()
        head.sety(y + MOVE_DISTANCE)
        update_coordinates()

def go_down():
    head.setheading(270)
    if head.ycor() > -max_y:
        y = head.ycor()
        head.sety(y - MOVE_DISTANCE)
        update_coordinates()        

def go_left():
    head.setheading(180)
    if head.xcor() > -max_x:
        x = head.xcor()
        head.setx(x - MOVE_DISTANCE)
        update_coordinates()

def go_right():
    head.setheading(0)
    if head.xcor() < max_x:
        x = head.xcor()
        head.setx(x + MOVE_DISTANCE)
        update_coordinates()

def close():
    wn.bye()

# Keyboard bindings
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(close, "Escape")

# Main loop
wn.mainloop()

# Finalização do loop do cliente MQTT
client_sub.loop_stop()
client_sub.disconnect()
client_pub.loop_stop()
client_pub.disconnect()