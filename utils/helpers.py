def get_text_user(message: dict) -> str:
    message_type = message.get('type')
    
    if message_type == 'text':
        return message.get('text', {}).get('body', '')
    
    if message_type == 'interactive':
        interactive = message.get('interactive', {})
        interactive_type = interactive.get('type')

        if interactive_type == 'button_reply':
            return interactive.get('button_reply', {}).get('title', '')

        if interactive_type == 'list_reply':
            return interactive.get('list_reply', {}).get('title', '')

    return ''

def text_message(message: str, phone: str):
    return {
        'messaging_product': 'whatsapp',    
        'recipient_type': 'individual',
        'to': phone,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': message
        }
    }

def text_format_message(message: str, phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': f'{message}, *{message}*, _{message}_, ~{message}~, ```{message}```'
        }
    }

def image_message(message: str, phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'image',
        'image': {
            'link': 'https://funko.com/dw/image/v2/BGTS_PRD/on/demandware.static/-/Sites-funko-master-catalog/default/dw8c649906/images/funko/upload/87245b_OP_LucciChase_POP_GLAM-CH-WEB.png',
            'caption': message
        }
    }

def audio_message(phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'audio',
        'audio': {
            'link': 'https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/audio_whatsapp.mp3'
        }
    }

def video_message(message: str, phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'video',
        'video': {
            'link': 'https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/video_whatsapp.mp4',
            'caption': message
        }
    }

def document_message(message: str, phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'document',
        'document': {
            'link': 'https://biostoragecloud.blob.core.windows.net/resource-udemy-whatsapp-node/document_whatsapp.pdf',
            'caption': message
        }
    }

def location_message(phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'location',
        'location': {
            'latitude': '-33.629036',
            'longitude': '-70.769951',
            'name': 'Estadio Nacional',
            'address': 'Av. Grecia 2001, Ñuñoa, Región Metropolitana'
        }
    }

def buttons_message(phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'interactive',
        'interactive': {
            'type': 'button',
            'body': {
                'text': '¿Confirmas tu registro?'
            },
            'action': {
                'buttons': [
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'btn_001',
                            'title': '👍 Si'
                        }
                    },
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'btn_002',
                            'title': '👎 No'
                        }
                    }
                ]
            }
        }
    }

def list_message(phone: str):
    return {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': phone,
        'type': 'interactive',
        'interactive': {
            'type': 'list',
            'body': {
                'text': '✅ I have these options'
            },
            'footer': {
                'text': 'Select an option'
            },
            'action': {
                'button': 'See options',
                'sections': [
                    {
                        'title': 'Buy and sell products',
                        'rows': [
                            {
                                'id': 'main-buy',
                                'title': 'Buy',
                                'description': 'Buy the best product your home'
                            },
                            {
                                'id': 'main-sell',
                                'title': 'Sell',
                                'description': 'Sell your products'
                            }
                        ]
                    },
                    {
                        'title': '📍Center of Attention',
                        'rows': [
                            {
                                'id': 'main-agency',
                                'title': 'Agency',
                                'description': 'Your can visit our agency'
                            },
                            {
                                'id': 'main-contact',
                                'title': 'Contact center',
                                'description': 'One of our agents will assist you'
                            }
                        ]
                    }
                ]
            }
        }
    }
