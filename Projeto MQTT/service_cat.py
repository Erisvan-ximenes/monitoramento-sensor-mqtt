import time
import json
from collections import deque
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883

TOPIC_SENSORS = "industrial/caldeira/sensor/+/temperatura"
TOPIC_HIGH_TEMP = "industrial/caldeira/cat/temperatura_alta"
TOPIC_SUDDEN_RISE = "industrial/caldeira/cat/aumento_repentino"

# Estruturas para cálculo da janela de 120 segundos
readings = deque()  # Armazena tuplas (timestamp, valor)
last_averages = deque(maxlen=2)  # Mantém as duas últimas médias calculadas

def on_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode().strip()
        current_time = time.time()
        
        # Tenta interpretar como JSON (sensores simulados via Python)
        try:
            data = json.loads(raw_payload)
            temp = float(data["temperatura"])
            sensor_id = data.get("sensor_id", msg.topic.split('/')[-2])
        except (json.JSONDecodeError, KeyError, TypeError):
            # Fallback para valor numérico puro (IoT MQTT Panel / Smartphone)
            temp = float(raw_payload)
            sensor_id = f"Smartphone ({msg.topic.split('/')[-2]})"

        # Adiciona nova leitura com timestamp atual
        readings.append((current_time, temp))
        
        # Remove leituras com mais de 120 segundos
        while readings and (current_time - readings[0][0]) > 120:
            readings.popleft()
            
        # Calcula média atual na janela de 120s
        current_avg = sum(val for _, val in readings) / len(readings)
        print(f"[CAT] Leitura de [{sensor_id}]: {temp:.2f} °C | Média (120s): {current_avg:.2f} °C ({len(readings)} amostra(s))")
        
        # Regra 1: Temperatura Alta (> 200°C)
        if current_avg > 200.0:
            alert_payload = json.dumps({
                "evento": "temperatura_alta",
                "media_atual": round(current_avg, 2),
                "timestamp": current_time
            })
            client.publish(TOPIC_HIGH_TEMP, alert_payload)
            print(f"  --> [ALERTA DISPARADO] Temperatura Alta: {current_avg:.2f} °C")

        # Regra 2: Aumento Repentino (Diferença >= 5°C entre as duas últimas médias)
        if len(last_averages) > 0:
            previous_avg = last_averages[-1]
            diff = current_avg - previous_avg
            if diff >= 5.0:
                alert_payload = json.dumps({
                    "evento": "aumento_repentino",
                    "media_anterior": round(previous_avg, 2),
                    "media_atual": round(current_avg, 2),
                    "variacao": round(diff, 2),
                    "timestamp": current_time
                })
                client.publish(TOPIC_SUDDEN_RISE, alert_payload)
                print(f"  --> [ALERTA DISPARADO] Aumento Repentino: +{diff:.2f} °C")

        # Atualiza o histórico de médias
        last_averages.append(current_avg)

    except Exception as e:
        print(f"[CAT] Erro ao processar mensagem do tópico '{msg.topic}': {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="Service_CAT")
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    
    client.subscribe(TOPIC_SENSORS)
    print(f"[*] Serviço CAT ativo. Escutando '{TOPIC_SENSORS}'...")
    
    client.loop_forever()

if __name__ == "__main__":
    main()