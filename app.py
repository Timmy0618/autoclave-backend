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

# Define models for Swagger
festo_model = api.model('Festo', {
    'id': fields.Integer(description='Festo ID'),
    'name': fields.String(description='Festo name'),
    # Add other fields as needed
})

user_login_model = api.model('UserLogin', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

# Response models
success_response = api.model('SuccessResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})

error_response = api.model('ErrorResponse', {
    'code': fields.Integer(description='Error code'),
    'msg': fields.String(description='Error message')
})

login_response = api.model('LoginResponse', {
    'code': fields.Integer(description='Response code'),
    'msg': fields.String(description='Response message'),
    'data': fields.Nested(api.model('LoginData', {
        'accessToken': fields.String(description='JWT access token')
    }))
})

routes(app, api)
logger(app)
CORS(app)

app.logger.info("應用程式啟動中...")

# init_scheduler(app)

if __name__ == '__main__':
    app_asgi = WsgiToAsgi(app)
    uvicorn.run(app_asgi, host='0.0.0.0', port=app.config['PORT'])
