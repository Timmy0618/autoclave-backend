from flask import Blueprint, request
from controller.schedule import create, read, update, delete, update_detail, update_multi_detail

schedule = Blueprint("schedule", __name__)


@schedule.route("", methods=["POST"])
def create_schedule():
    data = request.get_json()

    return create(data)


@schedule.route("/<int:schedule_id>", methods=["GET"])
def read_schedule(schedule_id):

    return read(schedule_id)


@schedule.route("/<int:schedule_id>", methods=['PATCH'])
def update_schedule(schedule_id):
    data = request.get_json()

    return update(schedule_id, data)


@schedule.route("/detail/<int:schedule_detail_id>", methods=['PATCH'])
def update_schedule_detail(schedule_detail_id):
    data = request.get_json()

    return update_detail(schedule_detail_id, data)


@schedule.route("/detail", methods=['PATCH'])
def update_schedule_detail_multi():
    data = request.get_json()

    return update_multi_detail(data)


@schedule.route("/<int:schedule_id>", methods=['DELETE'])
def delete_schedule(schedule_id):

    return delete(schedule_id)

# @schedule("/<int:festoId>", methods=['GET'])
# def read_schedule(festoId):

#     return read()


# @schedule("/checkPressure/<int:schedule_id>", methods=['PATCH'])
# def updateCheckPressure(schedule_id):

#     return updateCheckPressure(schedule_id)
