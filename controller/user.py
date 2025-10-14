from flask import request, jsonify, make_response, current_app
from flask_jwt_extended import (create_access_token, get_jwt_identity)
from models.user import User  # Import your User model
from sqlalchemy.exc import SQLAlchemyError


def login(data):
    try:
        # Extract username and password from the request body
        name = data.get("name")
        password = data.get("password")

        # Query the user by name
        user = User.query.filter_by(name=name).first()

        # If the user is not found or password doesn't match, return an error response
        if user is None or user.password != password:
            return {"code": 401, "msg": "Invalid credentials."}, 401

        # Build the result to return
        result = {"code": 200, "msg": "Login successful",
                  "data": {"accessToken": create_access_token(identity=user.id)}}
        return result, 200

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500
