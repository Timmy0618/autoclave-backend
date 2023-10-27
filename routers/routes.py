from routers.swagger import swagger_ui_blueprint
from routers.schedule import schedule
from routers.formula import formula
from routers.user import user
from routers.festo import festo
from routers.history import history


class routes:
    def __init__(self, app) -> None:
        app.register_blueprint(swagger_ui_blueprint)
        app.register_blueprint(schedule, url_prefix='/schedule')
        app.register_blueprint(formula, url_prefix='/formula')
        app.register_blueprint(user, url_prefix='/user')
        app.register_blueprint(festo, url_prefix='/festo')
        app.register_blueprint(history, url_prefix='/history')
