import sys
import time
import random
import json
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883

def main():
    sensor_id = sys.argv[1] if len(sys.argv) > 1 else "sensor_01"
    topic = f"industrial/caldeira/sensor/{sensor_id}/temperatura"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f"Publisher_{sensor_id}")
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print(f"[*] Sensor {sensor_id} iniciado. Publicando em '{topic}'...")

    try:
        while True:
            # Gera leitura simulada (simula normalidade ou picos para teste)
            temp = round(random.uniform(180.0, 210.0), 2)
            payload = json.dumps({
                "sensor_id": sensor_id,
                "temperatura": temp,
                "timestamp": time.time()
            })
            
            client.publish(topic, payload)
            print(f"[{sensor_id}] Enviado: {temp} °C")
            
            # Requisito: Envio a cada 60 segundos
            time.sleep(60)
            
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
        print("\n[!] Sensor finalizado.")

if __name__ == "__main__":
    main()