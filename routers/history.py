from flask import Blueprint, request
from controller.history import get_unique_batch_numbers, get_batch_records_csv, get_festo_history

history = Blueprint("history", __name__)


@history.route("", methods=["POST"])
def get_history():
    data = request.get_json()

    return get_festo_history(data)


@history.route("batch", methods=["GET"])
def get_history_batch_number():

    return get_unique_batch_numbers()


@history.route("export", methods=["POST"])
def export_csv():
    data = request.get_json()

    return get_batch_records_csv(data)
