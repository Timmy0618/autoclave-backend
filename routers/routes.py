from routers.schedule import schedule_ns
from routers.formula import formula_ns
from routers.user import user_ns
from routers.festo import festo_ns
from routers.history import history_ns


class routes:
    def __init__(self, app, api) -> None:
        api.add_namespace(schedule_ns, path='/schedule')
        api.add_namespace(formula_ns, path='/formula')
        api.add_namespace(user_ns, path='/user')
        api.add_namespace(festo_ns, path='/festo')
        api.add_namespace(history_ns, path='/history')
