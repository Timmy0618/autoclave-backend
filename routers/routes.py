from routers.swagger import swagger_ui_blueprint
from routers.schedule import schedule
from routers.formula import formula


class routes:
    def __init__(self, app) -> None:
        app.register_blueprint(swagger_ui_blueprint)
        app.register_blueprint(schedule, url_prefix='/schedule')
        app.register_blueprint(formula, url_prefix='/formula')
