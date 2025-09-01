import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from config import MongoConnection, Config

from utils import helpers
from services import whatsapp

load_dotenv()

app = Flask(__name__)
mongo = MongoConnection()

@app.route('/welcome', methods=['GET'])
def welcome():
    return 'method: welcome'

@app.route('/whatsapp', methods=['GET'])
def wsp_verify_token():
    try:
        accessToken = os.getenv('WSP_API_VERIFY_TOKEN')
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
        print(body)

        entry = (body.get('entry') or [{}])[0]
        changes = (entry.get('changes') or [{}])[0]
        value = changes.get('value', {})
        messages = (value.get('messages') or [{}])[0]
        phone = messages.get('from')


        buscar_rut('17167209-0')

        print(phone, messages)

        


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




def buscar_rut(rut: str):
    try:
        if not rut:
            return jsonify({
                'success': False,
                'error': 'RUT no proporcionado'
            })
        
        collection = mongo.get_collection()
        if collection is not None:
            # Buscar la persona por RUT (búsqueda flexible)
            persona = collection.find_one({
                '$or': [
                    {'rut': rut},
                    {'rut': rut.replace('.', '').replace('-', '')},
                    {'rut': {'$regex': rut.replace('.', '').replace('-', ''), '$options': 'i'}}
                ]
            })

            print(persona)
            
            # if persona:
            #     return jsonify({
            #         'success': True,
            #         'found': True,
            #         'persona': {
            #             'rut': persona.get('rut', ''),
            #             'nombre': persona.get('nombre', '')
            #         }
            #     })
            # else:
            #     return jsonify({
            #         'success': True,
            #         'found': False,
            #         'message': 'RUT no encontrado'
            #     })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo conectar a la base de datos'
            })
            
    except Exception as e:
        print(f"Error al buscar RUT: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        })



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
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
