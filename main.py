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
        # print(body)

        entry = (body.get('entry') or [{}])[0]
        changes = (entry.get('changes') or [{}])[0]
        value = changes.get('value', {})
        messages = (value.get('messages') or [{}])[0]

        typeMsg = messages.get('type')
        phone = messages.get('from')

        text = helpers.get_text_user(messages)



        # Save jsonDataFile mongo
        jsonDataFile = None
        if typeMsg in ['image', 'document']:

            text = typeMsg

            jsonDataFile = messages.get(typeMsg)
            
            data = {
                "phone": phone,
                "file": jsonDataFile
            }

            collection = mongo.get_collection('files')
            collection.insert_one(data)

            wsp_file_id = jsonDataFile.get('id')
            status, file_data = whatsapp.get_file(wsp_file_id)


        print(text)

        # wsp_send_message(text, phone)
        wsp_process_message(text, phone)

        return 'EVENT_RECEIVED'
    except:
        return 'EVENT_RECEIVED'


def wsp_process_message(message: str, phone: str):
    message = message.lower()
    listData = []

    # Buscar a la persona por número de teléfono para personalizar respuestas
    persona = buscar_persona_por_telefono(phone)
    nombre_usuario = persona.get('nombre', '') if persona else ''
    
    # Extraer solo el primer nombre si hay varios nombres
    if nombre_usuario:
        primer_nombre = nombre_usuario.split()[0]
    else:
        primer_nombre = ''

    if any(p in message for p in ['hi', 'hello', 'hola', 'buenas']):
        # Personalizar el saludo si se encontró el nombre
        if primer_nombre:
            saludo = f'Hola {primer_nombre}, espero te encuentres bien.'
        else:
            saludo = 'Hola, ¿Cómo estás?'
        
        data = helpers.text_message(saludo, phone)
        dataMsg2 = helpers.text_message('Para continuar envíame la foto de tu cédula de identidad', phone)
        listData.extend([data, dataMsg2])

    elif any(p in message for p in ['thanks', 'thank', 'thank you', 'gracias']):
        # Personalizar el agradecimiento si se encontró el nombre
        if primer_nombre:
            agradecimiento = f'Gracias por contactarnos {primer_nombre}'
        else:
            agradecimiento = 'Gracias por contactarnos'
        
        data = helpers.text_message(agradecimiento, phone)
        listData.extend([data])


    elif any(p in message for p in ['image', 'document']):
        data = helpers.text_message(f'Gracias {primer_nombre} por la información cargada, esta sera procesada y registrada en sistema', phone)
        data2 = helpers.text_message(f'Espere ⏰ mientras se procesa su documento 📄', phone)
        # dataLocation = helpers.location_message(phone)
        listData.extend([data, data2])




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
        # Personalizar mensaje de error si se encontró el nombre
        if primer_nombre:
            mensaje_error = f'Lo siento {primer_nombre}, no entiendo lo que me quieres decir'
        else:
            mensaje_error = 'Lo siento, no entiendo lo que me quieres decir'
        
        data = helpers.text_message(mensaje_error, phone)
        listData.extend([data])

    for item in listData:
        whatsapp.send_message(item)




def buscar_persona_por_telefono(phone: str):
    """
    Busca una persona en la base de datos usando el número de teléfono
    """
    try:
        if not phone:
            return None
        
        collection = mongo.get_collection('users')
        if collection is not None:
            # Limpiar el número de teléfono para la búsqueda
            phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '')
            
            # Buscar la persona por número de teléfono (búsqueda flexible)
            persona = collection.find_one({
                '$or': [
                    {'numero': phone},
                    {'numero': phone_clean},
                    {'numero': f'+{phone_clean}'},
                    {'numero': {'$regex': phone_clean, '$options': 'i'}}
                ]
            })
            
            return persona
        else:
            print("No se pudo conectar a la base de datos")
            return None
            
    except Exception as e:
        print(f"Error al buscar persona por teléfono: {e}")
        return None

# def buscar_rut(rut: str):
#     try:
#         if not rut:
#             return jsonify({
#                 'success': False,
#                 'error': 'RUT no proporcionado'
#             })
        
#         collection = mongo.get_collection()
#         if collection is not None:
#             # Buscar la persona por RUT (búsqueda flexible)
#             persona = collection.find_one({
#                 '$or': [
#                     {'rut': rut},
#                     {'rut': rut.replace('.', '').replace('-', '')},
#                     {'rut': {'$regex': rut.replace('.', '').replace('-', ''), '$options': 'i'}}
#                 ]
#             })

#             print(persona)
            
#             # if persona:
#             #     return jsonify({
#             #         'success': True,
#             #         'found': True,
#             #         'persona': {
#             #             'rut': persona.get('rut', ''),
#             #             'nombre': persona.get('nombre', '')
#             #         }
#             #     })
#             # else:
#             #     return jsonify({
#             #         'success': True,
#             #         'found': False,
#             #         'message': 'RUT no encontrado'
#             #     })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'No se pudo conectar a la base de datos'
#             })
            
#     except Exception as e:
#         print(f"Error al buscar RUT: {e}")
#         return jsonify({
#             'success': False,
#             'error': 'Error interno del servidor'
#         })



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
