# Sistema de Monitoramento Industrial de Sensor via MQTT

Este projeto foi desenvolvido para a disciplina da pós-graduação e implementa uma arquitetura de monitoramento de temperatura em tempo real para caldeiras industriais utilizando a protocolo MQTT.

## Arquitetura do Sistema

O sistema é dividido em microsserviços independentes que se comunicam através do broker MQTT público (`broker.emqx.io` na porta `1883`):

1. **Simulador de Sensores (`sensor_simulado.py`):** Gera leituras periódicas de temperatura da caldeira enviando payloads em formato JSON.
2. **Sensor Físico / Mobile (Android - IoT MQTT Panel):** Dispositivo real configurado no smartphone para simular um sensor em campo publicando em `industrial/caldeira/sensor/mobile_01/temperatura`.
3. **Serviço CAT (`service_cat.py`):** Processa as leituras recebidas em uma janela móvel de 120 segundos. Avalia duas regras de negócio:
   - **Temperatura Alta:** Média móvel > 200 °C.
   - **Aumento Repentino:** Variação de temperatura ≥ 5 °C em relação à média anterior.
4. **Painel de Alarmes (`service_alarms_gui.py`):** Interface gráfica desenvolvida em Tkinter para exibição dos alertas visuais e sonoros/notificações em tempo real.

## Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Comunicação:** Protocolo MQTT (Biblioteca `paho-mqtt` v2.x)
- **Interface Gráfica:** Tkinter
- **Broker:** EMQX Public Broker (`broker.emqx.io:1883`)
- **Sensor Real:** Aplicativo Android *IoT MQTT Panel*

## Estrutura do Tópicos MQTT

- **Leitura dos Sensores:** `industrial/caldeira/sensor/+/temperatura`
- **Alerta de Temperatura Alta:** `industrial/caldeira/cat/temperatura_alta`
- **Alerta de Aumento Repentino:** `industrial/caldeira/cat/aumento_repentino`

## Como Executar o Projeto

1. Instale as dependências:
   ```bash
   pip install paho-mqtt
-------------------------------------------------------------------------------------------   
Inicie os serviços na seguinte ordem:
Passo 1: Executar a Interface Gráfica de Alarmes:

  python service_alarms_gui.py

 Passo 2: Executar o Serviço CAT:
 
  python service_cat.py

Passo 3: Executar o Simulador de Sensores:

  python sensor_simulado.py

Passo 4: Enviar mensagens via aplicativo móvel IoT MQTT Panel no celular para simular leituras reais de campo.

 Obs. Para validar a comunicação rode o comando abaixo para validar a comunicação ebtre o aplicativo movel e o painel de monitoramento(opcional).
 
 python -c "import paho.mqtt.client as c; cli = c.Client(c.CallbackAPIVersion.VERSION1, 'Sniffer'); cli.connect('broker.emqx.io', 1883); cli.subscribe('industrial/caldeira/sensor/#'); cli.on_message = lambda _,__,m: print(f'\n>>> RECEBIDO DADOS DO CELULAR: Tópico: [{m.topic}] | Payload: [{m.payload.decode()}]'); cli.loop_forever()"

   Mostrando a execução, link: https://drive.google.com/file/d/1c3W_id9J7d7KuzwBX2xUp8utLh4IzACu/view?usp=sharing
