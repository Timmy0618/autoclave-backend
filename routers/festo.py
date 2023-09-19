from flask import Blueprint, request
from controller.festo import create, read, read_multi, update, delete, get_currently_executing_info

festo = Blueprint("festo", __name__)


@festo.route("", methods=["POST"])
def create_festo():
    data = request.get_json()

    return create(data)


@festo.route("/<int:festo_id>", methods=["GET"])
def read_festo(festo_id):

    return read(festo_id)


@festo.route("", methods=["GET"])
def read_multi_festos():

    return read_multi()


@festo.route("/<int:festo_id>", methods=["PATCH"])
def update_festo(festo_id):
    data = request.get_json()

    return update(festo_id, data)


@festo.route("/<int:festo_id>", methods=["DELETE"])
def delete_festo(festo_id):

    return delete(festo_id)


@festo.route("/executing", methods=["GET"])
def executing_festo():

    return get_currently_executing_info()
