from flask import current_app, jsonify, make_response, request
from models.model import FormulaMain, FormulaDetail
from models.shared import db
from sqlalchemy.exc import SQLAlchemyError


def create(data):
    try:
        # Extract required parameters from the JSON data
        name = data.get("name")
        details = data.get("detail")

        # Create FormulaMain object and set parameters
        new_formula = FormulaMain(name=name)

        # Add the new FormulaMain object to the database session
        db.session.add(new_formula)
        db.session.commit()

        # Add details to the new FormulaMain object
        for index, detail in enumerate(details):
            pressure = detail.get("pressure")
            process_time = detail.get("process_time")

            new_detail = FormulaDetail(
                formula_main=new_formula,
                pressure=pressure,
                process_time=process_time,
                sequence=index
            )

            db.session.add(new_detail)

        db.session.commit()

        # Build the result to return
        result = {"code": 201, "msg": "Success",
                  "data": {"id": new_formula.id, "name": new_formula.name}
                  }
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


def read(formula_id):
    try:
        # Query the FormulaMain table by formula_id
        formula = FormulaMain.query.get(formula_id)

        # If the formula is not found, return an error response
        if formula is None:
            return make_response(jsonify({"code": 404, "msg": "Formula not found."}), 404)

        # Build the result to return
        result = {
            "code": 200,
            "msg": "Success",
            "data": {
                "id": formula.id,
                "name": formula.name,
                "details": [{"pressure": detail.pressure, "processTime": detail.process_time} for detail in formula.formula_details]
            },
        }
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def read_multi():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Query the FormulaMain table with offset and limit
        formulas = FormulaMain.query.offset(page-1).limit(limit).all()
        print(formulas)

        # Build a list of formulas with their details
        formula_list = []
        for formula in formulas:
            formula_info = {
                "id": formula.id,
                "name": formula.name,
                "details": [{"pressure": detail.pressure, "processTime": detail.process_time} for detail in formula.formula_details]
            }
            formula_list.append(formula_info)

        # Build the result to return
        result = {
            "code": 200,
            "msg": "Success",
            "data": formula_list
        }
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def update(formula_id, data):
    try:
        # Query the FormulaMain table by formula_id
        formula = FormulaMain.query.get(formula_id)

        # If the formula is not found, return an error response
        if formula is None:
            return make_response(jsonify({"code": 404, "msg": "Formula not found."}), 404)

        # Extract and update the formula's name
        name = data.get("name")
        formula.name = name

        # Delete the old details
        for old_detail in formula.formula_details:
            db.session.delete(old_detail)

        # Add new details to the formula
        details = data.get("detail")
        for index, detail in enumerate(details):
            pressure = detail.get("pressure")
            process_time = detail.get("processTime")

            new_detail = FormulaDetail(
                formula_main=formula,
                pressure=pressure,
                process_time=process_time,
                sequence=index,
            )
            db.session.add(new_detail)

        db.session.commit()

        # Build the result to return
        result = {"code": 200, "msg": "Success"}
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def delete(formula_id):
    try:
        # Query the FormulaMain table by formula_id
        formula = FormulaMain.query.get(formula_id)

        # If the formula is not found, return an error response
        if formula is None:
            return make_response(jsonify({"code": 404, "msg": "Formula not found."}), 404)

        # Delete the formula details
        for detail in formula.formula_details:
            db.session.delete(detail)

        # Delete the formula itself
        db.session.delete(formula)
        db.session.commit()

        # Build the result to return
        result = {"code": 200, "msg": "Success"}
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)
