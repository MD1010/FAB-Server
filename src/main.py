from dotenv import load_dotenv

from consts.server import SERVER_IP
from src.api.routes import register_routes
from src.app import app, socketio


if __name__ == '__main__':
    load_dotenv()
    register_routes()
    socketio.run(app, port=5000, host=SERVER_IP, debug=True)
