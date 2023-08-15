from flask import current_app, jsonify, make_response, request
from models.model import Schedule, ScheduleDetail, FormulaMain, FestoMain, Pid
from models.shared import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


def create(data):
    try:
        # Extract required parameters from the JSON data
        festo_main_id = data.get("festoMainId")
        formula_id = data.get("formulaId")
        pid_id = data.get("pid")

        formula, error_response = __check_and_get_entities(
            festo_main_id, pid_id, formula_id)
        if error_response:
            return make_response(jsonify(error_response), error_response["code"])

        # Create a new ScheduleMain object and set parameters
        new_schedule_main = Schedule(
            festo_main_id=festo_main_id, pid_id=pid_id)

        # Calculate time_start and time_end based on formula details
        current_time = datetime.now()
        for index, detail in enumerate(formula.formula_details):
            pressure = detail.pressure
            process_time = detail.process_time

            time_start = current_time
            time_end = current_time + timedelta(minutes=process_time)

            new_schedule_detail = ScheduleDetail(
                pressure=pressure,
                sequence=index,
                status=0,
                process_time=process_time,
                time_start=time_start,
                time_end=time_end,
                reset_times=0,
                check_pressure=1
            )

            new_schedule_main.schedule_details.append(new_schedule_detail)

            # Update current_time for the next detail
            current_time = time_end + timedelta(seconds=1)

        # Add the new ScheduleMain object to the database session
        db.session.add(new_schedule_main)
        db.session.commit()

        # Build the result to return
        result = {"code": 201, "msg": "Success", "id": new_schedule_main.id}
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


def read(schedule_id):
    try:
        # Query the Schedule table by schedule_id
        schedule = Schedule.query.get(schedule_id)

        # If the schedule is not found, return an error response
        if schedule is None:
            return make_response(jsonify({"code": 404, "msg": "Schedule not found."}), 404)

        # Build the result to return
        result = {
            "code": 200,
            "msg": "Success",
            "data": {
                "id": schedule.id,
                "festoMainId": schedule.festo_main_id,
                "pidId": schedule.pid_id,
                "scheduleDetails": [
                    {
                        "id": detail.id,
                        "pressure": detail.pressure,
                        "sequence": detail.sequence,
                        "processTime": detail.process_time,
                        "timeStart": detail.time_start.strftime("%Y-%m-%d %H:%M:%S"),
                        "timeEnd": detail.time_end.strftime("%Y-%m-%d %H:%M:%S"),
                        "resetTimes": detail.reset_times
                    }
                    for detail in schedule.schedule_details
                ]
            }
        }
        return make_response(jsonify(result), 200)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def update(schedule_id, data):
    try:
        # Query the Schedule table by schedule_id
        schedule = Schedule.query.get(schedule_id)

        # If the schedule is not found, return an error response
        if schedule is None:
            return make_response(jsonify({"code": 404, "msg": "Schedule not found."}), 404)

        # Extract the required parameters from the JSON data
        festo_main_id = data.get("festoMainId")
        pid_id = data.get("pidId")
        formula_id = data.get("formulaId")

        formula, error_response = __check_and_get_entities(
            festo_main_id, pid_id, formula_id)
        if error_response:
            return make_response(jsonify(error_response), error_response["code"])

        # Update the schedule's parameters
        schedule.festo_main_id = festo_main_id
        schedule.pid_id = pid_id

        # Delete existing schedule details
        for schedule_detail in schedule.schedule_details:
            db.session.delete(schedule_detail)

        update_schedules(formula, schedule.id)

        # Commit the changes to the database
        db.session.commit()

        # Build the result to return
        result = {"code": 200, "msg": "Success", "id": schedule.id}
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


def update_detail(schedule_detail_id, data):
    try:
        # Query the ScheduleDetail table by schedule_detail_id
        schedule_detail = ScheduleDetail.query.get(schedule_detail_id)

        # If the schedule detail is not found, return an error response
        if schedule_detail is None:
            return make_response(jsonify({"code": 404, "msg": "Schedule detail not found."}), 404)

        # Extract the parameters from the JSON data
        pressure = data.get("pressure")
        process_time = data.get("processTime")
        sequence = data.get("sequence")
        status = data.get("status")
        check_pressure = data.get("checkPressure")
        time_start = data.get("timeStart")
        time_end = data.get("timeEnd")

        # Update the schedule detail's parameters
        if pressure is not None:
            schedule_detail.pressure = pressure
        if process_time is not None:
            schedule_detail.process_time = process_time
        if sequence is not None:
            schedule_detail.sequence = sequence
        if status is not None:
            schedule_detail.status = status
        if check_pressure is not None:
            schedule_detail.check_pressure = check_pressure
        if time_start is not None:
            schedule_detail.time_start = time_start
        if time_end is not None:
            schedule_detail.time_end = time_end

        # Commit the changes to the database
        db.session.commit()

        # Build the result to return
        result = {"code": 200, "msg": "Success", "id": schedule_detail.id}
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


def update_multi_detail(data):
    try:
        for detail_data in data:
            schedule_detail_id = detail_data.get("id")
            pressure = detail_data.get("pressure")
            process_time = detail_data.get("processTime")
            status = detail_data.get("status")
            check_pressure = detail_data.get("checkPressure")

            schedule_detail = ScheduleDetail.query.get(schedule_detail_id)

            if schedule_detail is None:
                return make_response(jsonify({"code": 404, "msg": f"Schedule Detail with ID {schedule_detail_id} not found."}), 404)

            if pressure is not None:
                schedule_detail.pressure = pressure
            if process_time is not None:
                schedule_detail.process_time = process_time
            if status is not None:
                schedule_detail.status = status
            if check_pressure is not None:
                schedule_detail.check_pressure = check_pressure

        db.session.commit()

        result = {"code": 200, "msg": "Success"}
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


def delete(schedule_id):
    try:
        # Query the Schedule table by schedule_id
        schedule = Schedule.query.get(schedule_id)

        # If the schedule is not found, return an error response
        if schedule is None:
            return make_response(jsonify({"code": 404, "msg": "Schedule not found."}), 404)

        # Delete existing schedule details
        for schedule_detail in schedule.schedule_details:
            db.session.delete(schedule_detail)

        # Delete the schedule itself
        db.session.delete(schedule)
        db.session.commit()

        # Build the result to return
        result = {"code": 200, "msg": "Schedule deleted successfully"}
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


def __check_and_get_entities(festo_main_id, pid_id, formula_id):
    # Check if festo_main_id exists
    festo_main = FestoMain.query.get(festo_main_id)
    if festo_main is None:
        return None, {"code": 404, "msg": "FestoMain not found."}

    # Check if pid_id exists
    pid = Pid.query.get(pid_id)
    if pid is None:
        return None, {"code": 404, "msg": "Pid not found."}

    # Retrieve the formula details based on formula_id
    formula = FormulaMain.query.get(formula_id)
    if formula is None:
        return None, {"code": 404, "msg": "Formula not found."}

    return formula, None


def update_schedules(formula, schedule_id):
    current_time = datetime.now()
    # Recreate schedule details based on the new formula details
    for index, detail_data in enumerate(formula.formula_details):
        pressure = detail_data.pressure
        process_time = detail_data.process_time

        time_start = current_time
        time_end = current_time + timedelta(minutes=process_time)

        new_schedule_detail = ScheduleDetail(
            schedule_id=schedule_id,
            pressure=pressure,
            sequence=index,
            status=2,
            process_time=process_time,
            time_start=time_start,
            time_end=time_end,
            reset_times=0  # You can adjust this as needed
        )

        db.session.add(new_schedule_detail)

        # Update current_time for the next detail
        current_time = time_end + timedelta(seconds=1)
