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

# ------------------ ESTILO PASTEL ------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f3e8ff, #ede9fe);
        font-family: 'Segoe UI', sans-serif;
    }

    h1 {
        text-align: center;
        color: #7c3aed;
        font-weight: 700;
    }

    h2, h3 {
        text-align: center;
        color: #8b5cf6;
    }

    .card {
        background: white;
        padding: 35px;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(168, 85, 247, 0.2);
        max-width: 500px;
        margin: auto;
        margin-top: 30px;
    }

    .description {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .stButton>button {
        background: linear-gradient(90deg, #c4b5fd, #a78bfa);
        color: #4c1d95;
        border-radius: 15px;
        border: none;
        padding: 12px 25px;
        font-size: 16px;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ddd6fe, #c4b5fd);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.title("🔮 Control de Puerta por Voz")

st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("""
<p class="description">
Esta interfaz permite abrir una puerta mediante comandos de voz.
El sistema captura lo que dices y lo envía a través de MQTT,
conectándose con Wokwi para ejecutar la acción en tiempo real.
</p>
""", unsafe_allow_html=True)

image = Image.open('voice_ctrl.jpg')
st.image(image, width=160)

st.write("🎤 Presiona el botón y di el comando para abrir la puerta")

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
        st.success(f"🗣️ Comando: {texto}")

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message = json.dumps({"Act1": texto.strip()})
        client1.publish("voice_mjl", message)

    try:
        os.mkdir("temp")
    except:
        pass

st.markdown('</div>', unsafe_allow_html=True)
