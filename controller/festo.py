from flask import jsonify, make_response, current_app
from models.festo import FestoMain
from models.formula import FormulaMain
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from models.shared import db


def create(data):
    try:
        # Extract parameters from the request body
        name = data.get("name")
        slave_id = data.get("slaveId")
        batch_number = data.get("batchNumber")
        warning_time = data.get("warningTime")

        # Create a new FestoMain object and set parameters
        new_festo = FestoMain(
            name=name,
            slave_id=slave_id,
            batch_number=batch_number,
            warning_time=warning_time,
            create_time=datetime.now(),
            update_time=datetime.now()
        )

        # Add the new FestoMain object to the database session
        db.session.add(new_festo)
        db.session.commit()

        # Build the result to return
        result = {"code": 201, "msg": "Festo created", "id": new_festo.id}
        return make_response(jsonify(result), 201)

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)

    finally:
        db.session.close()


def read(festo_id):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return make_response(jsonify({"code": 404, "msg": "Festo not found."}), 404)

        formula_name = festo.formula.name if festo.formula else None
        formula_id = festo.formula.id if festo.formula else None

        # Build the response
        result = {
            "code": 200,
            "msg": "Success",
            "data": {
                "id": festo.id,
                "name": festo.name,
                "formulaName": formula_name,
                "formulaId": formula_id,
                "slaveId": festo.slave_id,
                "batchNumber": festo.batch_number,
                "warningTime": festo.warning_time,
                "createTime": festo.create_time,
                "updateTime": festo.update_time
            },

        }

        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)


def read_multi():
    try:
        festos = FestoMain.query.all()

        festo_list = []
        for festo in festos:
            formula_name = festo.formula.name if festo.formula else None
            formula_id = festo.formula.id if festo.formula else None

            festo_list.append({
                "id": festo.id,
                "name": festo.name,
                "formulaName": formula_name,
                "formulaId": formula_id,
                "slaveId": festo.slave_id,
                "batchNumber": festo.batch_number,
                "warningTime": festo.warning_time,
                "createTime": festo.create_time,
                "updateTime": festo.update_time
            })

        result = {"code": 200, "msg": "Success",
                  "data": festo_list}
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)


def update(festo_id, data):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return make_response(jsonify({"code": 404, "msg": "Festo not found."}), 404)

        # Extract the update parameters from the JSON data
        formula_id = data.get("formulaId")
        batch_number = data.get("batchNumber")
        warning_time = data.get("warningTime")

        # Update the festo's properties if provided in the data
        if formula_id:
            formula = FormulaMain.query.get(formula_id)
            if formula is None:
                return make_response(jsonify({"code": 404, "msg": "Formula not found."}), 404)
            festo.formula = formula

        if batch_number:
            festo.batch_number = batch_number

        if warning_time is not None:
            festo.warning_time = warning_time

        # Commit the changes to the database
        db.session.commit()

        # Build the response
        result = {"code": 200, "msg": "Success", "id": festo.id}
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)

    finally:
        db.session.close()


def delete(festo_id):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return make_response(jsonify({"code": 404, "msg": "Festo not found."}), 404)

        # Delete the festo from the database
        db.session.delete(festo)
        db.session.commit()

        # Build the response
        result = {"code": 200, "msg": "Success", "id": festo.id}
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)

    finally:
        db.session.close()
