from flask import Blueprint, request
from controller.formula import create, read, read_multi, update, delete

formula = Blueprint("formula", __name__)


@formula.route("", methods=["POST"])
def create_formula():
    data = request.get_json()

    return create(data)


@formula.route("/<int:formula_id>", methods=["GET"])
def read_formula(formula_id):

    return read(formula_id)


@formula.route("", methods=["GET"])
def read_multi_formula():

    return read_multi()


@formula.route("/<int:formula_id>", methods=["PATCH"])
def update_formula(formula_id):
    data = request.get_json()

    return update(formula_id, data)


@formula.route("/<int:formula_id>", methods=["DELETE"])
def delete_formula(formula_id):

    return delete(formula_id)
