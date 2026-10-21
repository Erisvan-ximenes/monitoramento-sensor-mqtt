import json
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPICS = [("industrial/caldeira/cat/temperatura_alta", 0), 
          ("industrial/caldeira/cat/aumento_repentino", 0)]

class AlarmsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Alarmes Industriais - Caldeira")
        self.root.geometry("600x400")

        # Configuração de Interface
        ttk.Label(root, text="Monitor de Alarmes em Tempo Real", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=18, font=("Consolas", 10))
        self.log_area.pack(padx=10, pady=10)
        
        # Tags de cores para destaques visuais
        self.log_area.tag_config("HIGH_TEMP", foreground="red", background="#ffe6e6")
        self.log_area.tag_config("SUDDEN_RISE", foreground="orange", background="#fff0e6")
        self.log_area.tag_config("INFO", foreground="blue")

        # Inicia MQTT em thread separada para não travar a GUI
        self.mqtt_thread = threading.Thread(target=self.start_mqtt, daemon=True)
        self.mqtt_thread.start()

    def append_log(self, text, tag="INFO"):
        self.log_area.insert(tk.END, text + "\n", tag)
        self.log_area.see(tk.END)

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        topic = msg.topic

        if "temperatura_alta" in topic:
            msg_formatted = f"[ALARME FOGO/TEMP ALTA] Média atingiu {payload['media_atual']} °C!"
            self.root.after(0, self.append_log, msg_formatted, "HIGH_TEMP")

        elif "aumento_repentino" in topic:
            msg_formatted = f"[ALARME VARIAÇÃO] Subida abrupta! Anterior: {payload['media_anterior']}°C -> Atual: {payload['media_atual']}°C (+{payload['variacao']}°C)"
            self.root.after(0, self.append_log, msg_formatted, "SUDDEN_RISE")

    def start_mqtt(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="Service_Alarms_GUI")
        client.on_message = self.on_message
        client.connect(BROKER, PORT, 60)
        client.subscribe(TOPICS)
        self.append_log("[*] Conectado ao Broker MQTT. Aguardando eventos...", "INFO")
        client.loop_forever()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmsApp(root)
    root.mainloop()