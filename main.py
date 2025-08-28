import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from utils import helpers
from services import whatsapp

load_dotenv()

app = Flask(__name__)

@app.route('/welcome', methods=['GET'])
def welcome():
    return 'method: welcome'

@app.route('/whatsapp', methods=['GET'])
def wsp_verify_token():
    try:
        accessToken = 'ABC1234'
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token != None and challenge != None and token == accessToken:
            return challenge
        else:
            return '', 400
    except:
        return '', 400

@app.route('/whatsapp', methods=['POST'])
def wsp_received_message():
    try:
        body = request.get_json(silent=True) or {}

        entry = (body.get('entry') or [{}])[0]
        changes = (entry.get('changes') or [{}])[0]
        value = changes.get('value', {})
        messages = (value.get('messages') or [{}])[0]
        phone = messages.get('from')

        text = helpers.get_text_user(messages)
        # wsp_send_message(text, phone)
        wsp_process_message(text, phone)

        return 'EVENT_RECEIVED'
    except:
        return 'EVENT_RECEIVED'


def wsp_process_message(message: str, phone: str):
    message = message.lower()
    listData = []

    if any(p in message for p in ['hi', 'hello', 'hola', 'buenas']):
        data = helpers.text_message('Hola, ¿Como estas?', phone)
        dataMenu = helpers.list_message(phone)
        listData.extend([data, dataMenu])

    elif any(p in message for p in ['thanks', 'thank', 'thank you', 'gracias']):
        data = helpers.text_message('Gracias por contactarnos', phone)
        listData.extend([data])

    elif any(p in message for p in ['agency']):
        data = helpers.text_message('Esta es nuestra agencia', phone)
        dataLocation = helpers.location_message(phone)
        listData.extend([data, dataLocation])

    elif any(p in message for p in ['contact']):
        data = helpers.text_message('*Contact Center:*\n56963230969', phone)
        listData.extend([data])

    elif any(p in message for p in ['buy']):
        data = helpers.buttons_message(phone)
        listData.extend([data])

    elif any(p in message for p in ['sell']):
        data = helpers.buttons_message(phone)
        listData.extend([data])

    elif any(p in message for p in ['register']):
        data = helpers.text_message('Ingresa al siguiente links para registrar\nhttps://qa-gestioncontratistas.cmp.cl/#/auth/forgot-password', phone)
        listData.extend([data])

    elif any(p in message for p in ['login', 'log in']):
        data = helpers.text_message('Ingresa al siguiente links para login\nhttps://qa-gestioncontratistas.cmp.cl/#/auth/login', phone)
        listData.extend([data])

    else:
        data = helpers.text_message('Lo siento, no entiendo lo que me quieres decir', phone)
        listData.extend([data])

    for item in listData:
        whatsapp.send_message(item)

# def wsp_send_message(message: str, phone: str):
#     message = message.lower()

#     if 'text' in message: data = helpers.text_message(message, phone)
#     if 'format' in message: data = helpers.text_format_message(message, phone)
#     if 'image' in message: data = helpers.image_message(message, phone)
#     if 'audio' in message: data = helpers.audio_message(phone)
#     if 'video' in message: data = helpers.video_message(message, phone)
#     if 'document' in message: data = helpers.document_message(message, phone)
#     if 'location' in message: data = helpers.location_message(phone)
#     if 'button' in message: data = helpers.buttons_message(phone)
#     if 'list' in message: data = helpers.list_message(phone)

#     whatsapp.send_message(data)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, port=os.getenv('PORT', default=5000))
