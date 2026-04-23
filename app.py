import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json

# ------------------ MQTT ------------------
def on_publish(client,userdata,result):
    print("el dato ha sido publicado \n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("mjandtm")
client1.on_message = on_message

# ------------------ ESTILO ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #E9D5EC, #DCC6E0);
    font-family: 'Segoe UI', sans-serif;
}

/* 🔧 SOLUCIÓN: bajar todo para que no lo tape el header */
.block-container {
    padding-top: 4rem;
}

/* Título */
h1 {
    text-align: center;
    color: #4B2E59;
    font-weight: 800;
    margin-bottom: 30px;
}

/* CONTENEDOR */
.container {
    max-width: 800px;
    margin: auto;
}

/* CARDS */
.card {
    display: flex;
    align-items: center;
    gap: 20px;
    background: linear-gradient(135deg, #DAB1DA, #CFA7CF);
    padding: 25px;
    border-radius: 25px;
    margin-bottom: 20px;
    box-shadow: 0px 8px 20px rgba(155, 107, 175, 0.3);
}

/* ICONOS */
.icon {
    font-size: 35px;
    background: rgba(255,255,255,0.4);
    padding: 15px;
    border-radius: 50%;
}

/* TEXTO */
.text {
    color: #3B2A44;
    font-size: 16px;
    font-weight: 500;
}

/* BOTÓN */
.stButton>button {
    background: #DAB1DA;
    color: #3B2A44;
    border-radius: 15px;
    border: none;
    padding: 12px 25px;
    font-size: 16px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton>button:hover {
    background: #CFA7CF;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.title("🔮 Control Inteligente por Voz")

st.markdown('<div class="container">', unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="icon">🎤</div>
    <div class="text">
        Este sistema permite controlar dispositivos mediante comandos de voz.
    </div>
</div>

<div class="card">
    <div class="icon">🚪</div>
    <div class="text">
        Puedes abrir o cerrar la puerta y encender o apagar la luz 💡 en tiempo real.
    </div>
</div>

<div class="card">
    <div class="icon">📡</div>
    <div class="text">
        La información se envía mediante MQTT y se conecta con Wokwi para ejecutar las acciones.
    </div>
</div>
""", unsafe_allow_html=True)

# Espacio + instrucción
st.markdown("<br>", unsafe_allow_html=True)
st.write("🎤 Presiona el botón y da un comando")

# ------------------ BOTÓN ------------------
stt_button = Button(label="🎙️ Hablar", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ------------------ RESULTADO ------------------
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT")
        st.success(f"🗣️ Comando recibido: {texto}")

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message = json.dumps({"Act1": texto.strip()})
        client1.publish("voice_mjl", message)

    try:
        os.mkdir("temp")
    except:
        pass

st.markdown('</div>', unsafe_allow_html=True)
