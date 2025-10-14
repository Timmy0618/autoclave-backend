from flask import Flask
from models.shared import db
from models import model
from routers.routes import routes
from modules.logger import logger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from scheduler.scheduler import init_scheduler
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask_restx import Api, fields

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

api = Api(app, title='Autoclave API', description='Autoclave backend API documentation', version='1.0')

routes(app, api)
logger(app)
CORS(app)

app.logger.info("應用程式啟動中...")

# init_scheduler(app)

if __name__ == '__main__':
    app_asgi = WsgiToAsgi(app)
    uvicorn.run(app_asgi, host='0.0.0.0', port=app.config['PORT'])
