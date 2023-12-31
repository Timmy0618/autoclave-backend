from flask import Flask
from models.shared import db
from models import model
from routers.routes import routes
from modules.logger import logger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from scheduler.scheduler import init_scheduler

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

routes(app)
logger(app)
CORS(app)

init_scheduler(app)

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=False, port=app.config['PORT'])
