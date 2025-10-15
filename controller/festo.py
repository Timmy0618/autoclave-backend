from flask import jsonify, make_response, current_app
from models.festo import FestoMain
from models.formula import FormulaMain
from models.schedule import Schedule
from controller.schedule import update_schedules
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
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
        db.session.add(new_festo)
        db.session.commit()

        # Create a new Schedule for the FestoMain
        new_schedule = Schedule(
            festo_main_id=new_festo.id,
            pid_id=1,  # You can set this value if needed
            create_time=datetime.now(),
            update_time=datetime.now()
        )

        # Add the new FestoMain object to the database session
        db.session.add(new_schedule)
        db.session.commit()

        # Build the result to return
        result = {"code": 201, "msg": "Festo created", "id": new_festo.id}
        return result, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500

    finally:
        db.session.close()


def read(festo_id):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return {"code": 404, "msg": "Festo not found."}, 404

        formula_name = festo.formula.name if festo.formula else None
        formula_id = festo.formula.id if festo.formula else None
        schedules = []
        if festo.schedule:
            schedules = [{
                "id": detail.id,
                "name": formula_name,
                "pressure": detail.pressure,
                "processTime": detail.process_time,
                "sequence": detail.sequence,
                "status": detail.status,
                "checkPressure": detail.check_pressure,
                "timeEnd": detail.time_end.isoformat() if detail.time_end else None,
                "timeStart": detail.time_start.isoformat() if detail.time_start else None,
            } for detail in festo.schedule.schedule_details]

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
                "createTime": festo.create_time.isoformat() if festo.create_time else None,
                "updateTime": festo.update_time.isoformat() if festo.update_time else None,
                "schedules": schedules,
            },
        }

        return result, 200

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500


def read_multi():
    try:
        festos = FestoMain.query.all()

        festo_list = []
        for festo in festos:
            formula_name = festo.formula.name if festo.formula else None
            formula_id = festo.formula.id if festo.formula else None
            schedule_id = festo.schedule.id if festo.schedule else None

            festo_list.append({
                "id": festo.id,
                "name": festo.name,
                "formulaName": formula_name,
                "formulaId": formula_id,
                "slaveId": festo.slave_id,
                "batchNumber": festo.batch_number,
                "warningTime": festo.warning_time*5/60,
                "scheduleId": schedule_id,
                "createTime": festo.create_time.isoformat() if festo.create_time else None,
                "updateTime": festo.update_time.isoformat() if festo.update_time else None
            })

        result = {"code": 200, "msg": "Success",
                  "data": festo_list}
        return result, 200

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500


def update(festo_id, data):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return {"code": 404, "msg": "Festo not found."}, 404

        # Extract the update parameters from the JSON data
        formula_id = data.get("formulaId")
        batch_number = data.get("batchNumber")
        warning_time = data.get("warningTime")
        option = data.get("option")

        if option:
            status = 2
            if option == 'start':
                status = 0

                current_time = datetime.now()

                sorted_details = sorted(
                    festo.schedule.schedule_details, key=lambda x: x.sequence)
                cumulative_time = current_time

                for detail in sorted_details:
                    detail.status = status
                    detail.reset_times = 0

                    # Calculate the end time based on cumulative time and process_time
                    end_time = cumulative_time + \
                        timedelta(minutes=detail.process_time)
                    detail.time_start = cumulative_time
                    detail.time_end = end_time

                    # Update cumulative time for next iteration
                    cumulative_time = end_time+timedelta(seconds=1)

            for detail in festo.schedule.schedule_details:
                detail.status = status

        # Update the festo's properties if provided in the data
        if formula_id:
            formula = FormulaMain.query.get(formula_id)
            if formula is None:
                return {"code": 404, "msg": "Formula not found."}, 404

            # Check if festo has a schedule, if not create one
            if not festo.schedule:
                new_schedule = Schedule(
                    festo_main_id=festo.id,
                    pid_id=1,
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
                db.session.add(new_schedule)
                db.session.flush()  # Get the schedule id without committing
                schedule_id = new_schedule.id
            else:
                # Delete existing schedule details if schedule exists
                for schedule_detail in festo.schedule.schedule_details:
                    db.session.delete(schedule_detail)
                schedule_id = festo.schedule.id

            update_schedules(formula, schedule_id)

            festo.formula = formula

        if batch_number:
            festo.batch_number = batch_number

        if warning_time is not None:
            festo.warning_time = warning_time

        # Commit the changes to the database
        db.session.commit()

        # Build the response
        result = {"code": 200, "msg": "Success", "id": festo.id}
        return result, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500

    finally:
        db.session.close()


def delete(festo_id):
    try:
        festo = FestoMain.query.get(festo_id)

        if festo is None:
            return {"code": 404, "msg": "Festo not found."}, 404

        # Delete the associated schedules and schedule details
        for schedule in festo.schedules:
            for schedule_detail in schedule.schedule_details:
                db.session.delete(schedule_detail)
            db.session.delete(schedule)

        # Delete the festo from the database
        db.session.delete(festo)
        db.session.commit()

        # Build the response
        result = {"code": 200, "msg": "Success", "id": festo.id}
        return result, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500

    finally:
        db.session.close()


def get_currently_executing_info():
    try:
        # 获取当前时间
        current_time = datetime.now()

        # 查询所有 FestoMain
        festos = FestoMain.query.all()

        executing_info = []

        for festo in festos:
            # 查询与当前时间最接近的 Schedule
            nearest_schedule = None
            min_time_diff = None

            for schedule in festo.schedule.schedule_details:
                time_start = schedule.time_start
                time_end = schedule.time_end

                # 检查当前时间是否在时间范围内
                if time_start <= current_time <= time_end:
                    nearest_schedule = schedule
                    break

                # 计算当前时间距离该 Schedule 最近的时间差
                time_diff = min(abs((current_time - time_start).total_seconds()),
                                abs((current_time - time_end).total_seconds()))

                if min_time_diff is None or time_diff < min_time_diff:
                    min_time_diff = time_diff
                    nearest_schedule = schedule

            if nearest_schedule:
                formula = festo.formula

                executing_info.append({
                    "id": festo.id,
                    "festoName": festo.name,
                    "warningTime": festo.warning_time*5/60,
                    "formulaName": formula.name,
                    "schedulePressure": nearest_schedule.pressure,
                    "scheduleSequence": nearest_schedule.sequence,
                    "scheduleStatus": nearest_schedule.status,
                    "checkPressure": nearest_schedule.check_pressure
                })

        # 将查询结果包装成响应格式
        result = {"code": 200, "msg": "Success", "data": executing_info}
        return result, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return {"code": 500, "msg": "Database error."}, 500

    except Exception as e:
        current_app.logger.error(e)
        return {"code": 500, "msg": "An error occurred."}, 500

    finally:
        db.session.close()
