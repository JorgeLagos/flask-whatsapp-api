from pymongo import MongoClient
import os

class Config:
    # Configuración de MongoDB - Leer desde variables de entorno
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'flask-wsp-api')
    MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'users')

class MongoConnection:
    _instance = None
    _client = None
    _db = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if self._client is None:
            try:
                self._client = MongoClient(Config.MONGO_URI)
                self._db = self._client[Config.MONGO_DATABASE]
                print(":marca_de_verificación_blanca: Conexión a MongoDB establecida correctamente")
            except Exception as e:
                print(f":x: Error al conectar a MongoDB: {e}")
                self._client = None
                self._db = None
    def get_database(self):
        return self._db
    def get_collection(self, collection_name=None):
        if self._db is not None:
            try:
                col_name = collection_name or Config.COLLECTION_NAME
                collection = self._db[col_name]
                # Verificar que la colección es accesible haciendo un ping simple
                collection.find_one()
                return collection
            except Exception as e:
                print(f"Error al acceder a la colección: {e}")
                return None
        else:
            print("Base de datos no disponible")
            return None
    def close_connection(self):
        if self._client:
            self._client.close()
            print(":candado: Conexión a MongoDB cerrada")
    def test_connection(self):
        try:
            # Test de conexión
            self._client.admin.command('ping')
            return True, "Conexión exitosa a MongoDB"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"