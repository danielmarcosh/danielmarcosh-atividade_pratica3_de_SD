# Configuração do MQTT com ngrok usando Docker Compose

Este guia explica como configurar o **ngrok** para expor o serviço **MQTT** (utilizando o **Mosquitto**) à internet, usando **Docker Compose**.

## Passos para Configurar o ngrok com Docker Compose

### 1. Estrutura do `docker-compose.yml`

Crie ou edite o arquivo `docker-compose.yml` com o seguinte conteúdo:

```yaml
version: "3"
services:
  mqtt:
    image: toke/mosquitto
    container_name: mqtt
    network_mode: bridge  # Usando a rede bridge para o ngrok se conectar ao MQTT
    expose:
      - "1883"
    ports:
      - "1883:1883"
    restart: unless-stopped

  ngrok:
    image: wernight/ngrok
    container_name: ngrok
    network_mode: bridge
    command: ngrok tcp 1883
    ports:
      - "4040:4040"  # Expor a interface web do ngrok para ver as conexões e status do túnel
    depends_on:
      - mqtt
    restart: unless-stopped
```


### Explicação do docker-compose.yml
- mqtt:
    - Usa a imagem toke/mosquitto para rodar o broker MQTT.
    - Expondo a porta 1883 através de Docker para que o ngrok possa acessar essa porta.
- ngrok:
    - Usa a imagem wernight/ngrok, que já possui o ngrok configurado para criar túneis.
    - O comando ngrok tcp 1883 cria um túnel TCP para a porta 1883 do serviço MQTT.
- Portas:
    - 4040:4040: Expondo a interface web do ngrok, que pode ser acessada em http://localhost:4040 para monitoramento.

### Subir os Containers
```bash
docker-compose up -d
```
#### Isso irá:
- Subir o serviço MQTT.
- Subir o serviço ngrok, que criará o túnel para a porta 1883 do broker MQTT.

### Acessando o MQTT via ngrok
- Após iniciar o Docker Compose, o ngrok criará uma URL pública que você pode usar para acessar o broker MQTT. Para verificar a URL gerada, execute o seguinte comando para visualizar os logs do container ngrok.

```bash
docker logs ngrok
```
- Você verá algo semelhante a:
```
Forwarding                    tcp://0.tcp.ngrok.io:xxxxx -> tcp://mqtt:1883
```
- Onde 0.tcp.ngrok.io:xxxxx é a URL pública que foi gerada. Use essa URL para conectar-se ao seu broker MQTT de qualquer lugar.

### Acessando a Interface Web do ngrok
```arduino
http://localhost:4040
```
- A interface web permitirá visualizar detalhes sobre o tráfego, as conexões e os logs do túnel do ngrok.

### Resumo de como usar:
- Docker Compose é utilizado para configurar e rodar dois serviços: Mosquitto (MQTT) e ngrok.
- Ngrok cria um túnel para a porta 1883 do serviço MQTT, permitindo o acesso público ao broker MQTT.
- Porta 4040 é exposta para acessar a interface web do ngrok e monitorar o tráfego.
- O Ngrok fornece uma URL pública para acessar o serviço MQTT de qualquer lugar.

1. **Crie** ou **edite** o arquivo `docker-compose.yml` com o conteúdo fornecido acima.
2. **Execute** o comando `docker-compose up -d` para iniciar os containers.
3. **Verifique** os logs do ngrok com `docker logs ngrok` para obter a URL pública gerada.
4. **Acesse** a interface web do ngrok via `http://localhost:4040` para monitorar o tráfego.


