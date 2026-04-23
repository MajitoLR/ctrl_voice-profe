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

# ------------------ ESTILO MORADO ------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a0f2e, #2e1a47);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    h1 {
        text-align: center;
        color: #d6b3ff;
    }

    h2, h3 {
        text-align: center;
        color: #c084fc;
    }

    .card {
        background: rgba(255,255,255,0.05);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0px 0px 20px rgba(128,0,255,0.3);
        margin-top: 20px;
    }

    .stButton>button {
        background: linear-gradient(90deg, #a855f7, #7c3aed);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #c084fc, #9333ea);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.title("🔮 INTERFACES MULTIMODALES")
st.subheader("Control por voz para abrir puerta")

st.markdown('<div class="card">', unsafe_allow_html=True)

image = Image.open('voice_ctrl.jpg')
st.image(image, width=180)

st.write("🎤 Toca el botón y da la orden para abrir la puerta")

# ------------------ BOTÓN VOZ ------------------
stt_button = Button(label="🎙️ Iniciar", width=200)

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
