from flask import current_app, jsonify, make_response, request, send_file
from models.model import FestoHistory
from models.shared import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime, timedelta
import pytz
import csv


def get_unique_batch_numbers():
    try:
        start_date_str = request.args.get('startTime')
        end_date_str = request.args.get('endTime')

        # Convert date strings to datetime objects
        taipei_tz = pytz.timezone('Asia/Taipei')
        start_date = datetime.strptime(
            start_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)
        end_date = datetime.strptime(
            end_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)

        # Query the database
        unique_batch_numbers = db.session.query(FestoHistory.batch_number).filter(
            FestoHistory.create_time >= start_date,
            FestoHistory.create_time <= end_date
        ).distinct().all()

        # Convert result to a list of batch numbers
        unique_batch_numbers_list = [
            item.batch_number for item in unique_batch_numbers]

        result = {
            "code": 200,
            "msg": "Success",
            "data": unique_batch_numbers_list
        }

        return make_response(jsonify(result))

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def get_batch_records_csv(data):
    try:
        start_date_str = data.get('startTime')
        end_date_str = data.get('endTime')
        batch_number = data.get('batchNumber')  # 获取batch number

        # Convert date strings to datetime objects
        taipei_tz = pytz.timezone('Asia/Taipei')
        start_date = datetime.strptime(
            start_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)
        end_date = datetime.strptime(
            end_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)

        # Query the database
        query = db.session.query(FestoHistory).filter(
            FestoHistory.create_time >= start_date,
            FestoHistory.create_time <= end_date,
            FestoHistory.batch_number == batch_number
        )

        batch_records = query.all()

        # Create CSV
        csv_filename = 'batch_records.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:  # 添加encoding参数以支持多语言
            fieldnames = ['id', 'slave_id', 'batch_number', 'formula_name',
                          'sequence', 'pressure', 'create_time', 'update_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in batch_records:
                writer.writerow({
                    'id': record.id,
                    'slave_id': record.slave_id,
                    'batch_number': record.batch_number,
                    'formula_name': record.formula_name,
                    'sequence': record.sequence,
                    'pressure': record.pressure,
                    'create_time': record.create_time,
                    'update_time': record.update_time,
                })

        return send_file(csv_filename, as_attachment=True)

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def get_festo_history(data):
    try:
        batch_number = data['batchNumber']
        start_time_str = data['startTime']
        end_time_str = data['endTime']
        time_type = data['type']

        taipei_tz = pytz.timezone('Asia/Taipei')
        start_time = datetime.strptime(
            start_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)
        end_time = datetime.strptime(
            end_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=taipei_tz)

        history_list = []
        # Assume get_period_list is defined
        time_list = __get_period_list(start_time, end_time)

        for time in time_list:
            if time_type == "hour":
                date_format_str = '%Y-%m-%d %H'
            else:
                date_format_str = '%Y-%m-%d %H:%i'

            result = (
                db.session.query(
                    FestoHistory.formula_name.label('formulaName'),
                    func.avg(FestoHistory.pressure).label('avgPressure'),
                    func.date_format(FestoHistory.create_time,
                                     date_format_str).label('time')
                )
                .filter(
                    FestoHistory.batch_number == batch_number,
                    FestoHistory.create_time.between(time[0], time[1])
                )
                .group_by(
                    FestoHistory.formula_name,
                    func.date_format(FestoHistory.create_time, date_format_str)
                )
                .order_by(
                    func.date_format(FestoHistory.create_time, date_format_str)
                )
                .all()
            )

            result_dict = [row._asdict() for row in result]

            history_list.append({str(time[0]): result_dict})

        result = {
            "code": 200,
            "msg": "Success",
            "data": history_list
        }

        return make_response(jsonify(result))
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "Database error."}), 500)

    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify({"code": 500, "msg": "An error occurred."}), 500)


def __get_period_list(startTime, endTime):
    result = []
    difference = abs((startTime-endTime).days)

    for i in range(difference):
        start = startTime+timedelta(days=i)
        end = start+timedelta(hours=23, minutes=59, seconds=59)
        result.append([str(start), str(end)])

    return result
