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
    background: linear-gradient(135deg, #F8F3FA, #EFE7F3);
    font-family: 'Segoe UI', sans-serif;
}

/* Título */
h1 {
    text-align: center;
    color: #9B6BAF;
    font-weight: 700;
}

/* Tarjeta principal */
.card {
    background: white;
    padding: 35px;
    border-radius: 25px;
    text-align: center;
    box-shadow: 0px 10px 25px rgba(218, 177, 218, 0.4);
    max-width: 520px;
    margin: auto;
    margin-top: 30px;
}

/* Bloques de texto */
.block {
    background: #F3E8F6;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    color: #5B4B63;
    font-size: 14px;
}

/* Botón */
.stButton>button {
    background: #DAB1DA;
    color: #4B2E59;
    border-radius: 15px;
    border: none;
    padding: 12px 25px;
    font-size: 16px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton>button:hover {
    background: #E6C7E6;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.title("🔮 Control Inteligente por Voz")

st.markdown('<div class="card">', unsafe_allow_html=True)

# Descripción en bloques
st.markdown("""
<div class="block">
Este sistema permite controlar dispositivos mediante comandos de voz.
</div>

<div class="block">
Puedes abrir o cerrar la puerta 🚪 y encender o apagar la luz 💡 en tiempo real.
</div>

<div class="block">
La información se envía mediante MQTT y se conecta con Wokwi para ejecutar las acciones.
</div>
""", unsafe_allow_html=True)

# Imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=150)

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
