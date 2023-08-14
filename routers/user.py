from flask import Blueprint, request
from controller.user import login

user = Blueprint("user", __name__)


@user.route("/login", methods=["POST"])
def user_login():
    data = request.get_json()

    return login(data)


# @user.route("", methods=["GET"])
# def get_users():

#     return read_multi()
