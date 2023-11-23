from flask_apscheduler import APScheduler
from flask import current_app
from models.festo import FestoMain, FestoHistory, FestoCurrentDetail
from models.schedule import ScheduleDetail
from sqlalchemy.exc import SQLAlchemyError
from models.shared import db
from modules.festo import festo as festo_obj
from datetime import datetime, timedelta

scheduler = APScheduler()


@scheduler.task('interval', id='schedule', seconds=5)  # 每3600秒执行一次
def perform_schedule():
    with scheduler.app.app_context():
        current_time = datetime.now()
        festo_obj_conn = festo_obj(current_app.config['COM_PORT'])
        if not festo_obj_conn:
            print("RS485 connect error")
            return

        try:
            festos = FestoMain.query.all()

            for festo in festos:
                slave_id = festo.slave_id
                # 讀取 festo 壓力
                festo_pressure = festo_obj_conn.readSetPressure(
                    slave_id)

                schedule_details = ScheduleDetail.query.filter_by(
                    schedule_id=festo.schedule.id).all()

                # 更新 FestoCurrentDetail 表的壓力值
                festo_current_detail = FestoCurrentDetail.query.filter_by(
                    slave_id=slave_id).first()

                if festo_current_detail:
                    festo_current_detail.pressure = festo_pressure
                else:
                    festo_current_detail = FestoCurrentDetail(
                        slave_id=slave_id,
                        pressure=festo_pressure
                    )
                    db.session.add(festo_current_detail)

                for detail in schedule_details:

                    if detail.time_start <= current_time <= detail.time_end:
                        status = detail.status
                        pressure = detail.pressure
                        if status == 0:
                            # 待执行状态，执行相应操作
                            print(
                                f"待執行 Festo Slave ID: {slave_id}, Pressure: {pressure}, Status: {status}")
                            # 更新festo壓力=設定壓力
                            festo_obj_conn.writePressure(slave_id, pressure)
                            # 改變狀態=1
                            detail.status = 1
                        elif status == 1:
                            # 执行中状态
                            # 記錄當前壓力值
                            print(
                                f"執行中 Festo Slave ID: {slave_id}, Pressure: {pressure}, Status: {status}")

                            festo_history = FestoHistory(
                                slave_id=slave_id,
                                batch_number=festo.batch_number,
                                formula_name=festo.formula.name,
                                sequence=detail.sequence,
                                pressure=festo_pressure  # 要改成讀取festo壓力
                            )
                            db.session.add(festo_history)
                            # 檢查壓力有沒有到設定值，沒有的話要reset_times += 1
                            if festo_current_detail.pressure < pressure*0.95 or festo_current_detail.pressure > pressure*1.05:
                                detail.reset_times += 1
                                festo.warning_time += detail.reset_times % 12
                        elif status == 2:
                            # 结束状态
                            # 更新festo壓力=0
                            festo_obj_conn.writePressure(slave_id, 0)
                            detail.status = 2
                            print(
                                f"結束 Festo Slave ID: {slave_id}, Pressure: {pressure}, Status: {status}")

                    elif current_time > detail.time_end:
                        festo_obj_conn.writePressure(slave_id, 0)
                        detail.status = 2
                        festo.warning_time = 0

            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)

        except Exception as e:
            current_app.logger.error(e)

        finally:
            db.session.close()


@scheduler.task('interval', id='history_checker', seconds=86400)
def history_checker():
    with scheduler.app.app_context():
        print("clear history table")
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)

            records_to_delete = FestoHistory.query.filter(
                FestoHistory.create_time <= thirty_days_ago).all()

            for record in records_to_delete:
                db.session.delete(record)

            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)

        except Exception as e:
            current_app.logger.error(e)

        finally:
            db.session.close()


def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
