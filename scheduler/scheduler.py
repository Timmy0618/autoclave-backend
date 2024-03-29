from flask_apscheduler import APScheduler
from flask import current_app
from models.festo import FestoMain, FestoHistory, FestoCurrentDetail
from models.schedule import ScheduleDetail
from sqlalchemy.exc import SQLAlchemyError
from models.shared import db
from modules.festo import festo as festo_obj
from datetime import datetime, timedelta
import pygame

scheduler = APScheduler()
# 初始化 pygame
pygame.init()

mp3_file_path = "asset/beep-warning.mp3"
festo_obj_conn = None


@scheduler.task('interval', id='schedule', seconds=5)  # 每3600秒执行一次
def perform_schedule():
    with scheduler.app.app_context():
        festo_deviation = current_app.config['FESTO_DEVIATION']
        current_time = datetime.now()

        try:
            festos = FestoMain.query.all()

            for festo in festos:
                slave_id = festo.slave_id
                festo_pressure = festo_obj_conn.readVacuumPressure(slave_id)
                if festo_pressure is None:
                    e = f"Can't read {festo.name} pressure"
                    print(e)
                    current_app.logger.error(e)
                    continue

                schedule_details = ScheduleDetail.query.filter_by(
                    schedule_id=festo.schedule.id).order_by(ScheduleDetail.sequence).all()

                festo_current_detail = FestoCurrentDetail.query.filter_by(
                    slave_id=slave_id).first()

                if festo_current_detail is None:
                    festo_current_detail = FestoCurrentDetail(
                        slave_id=slave_id, pressure=festo_pressure, festo_main_id=festo.id)
                    db.session.add(festo_current_detail)
                else:
                    festo_current_detail.pressure = festo_pressure

                for index, detail in enumerate(schedule_details):
                    if detail.time_start <= current_time <= detail.time_end:
                        status = detail.status
                        dst_pressure = detail.pressure

                        if status == 0:
                            # 待執行狀態
                            print(
                                f"To be executed Festo Slave ID: {slave_id}, Pressure: {dst_pressure}, Status: {status}")
                            festo_obj_conn.writePressure(
                                slave_id, dst_pressure)
                            detail.status = 1
                        elif status == 1:
                            # 執行中狀態
                            print(
                                f"Executing Festo Slave ID: {slave_id}, Pressure: {dst_pressure}, Status: {status}")
                            festo_history = FestoHistory(slave_id=slave_id, batch_number=festo.batch_number,
                                                         formula_name=festo.formula.name, sequence=detail.sequence,
                                                         pressure=festo_pressure)
                            db.session.add(festo_history)
                            # 正負誤差超過 3 就累積錯誤
                            if not (dst_pressure + festo_deviation > festo_pressure > dst_pressure - festo_deviation):
                                # 真空閥可能被關閉，所以要再打開
                                festo_obj_conn.writePressure(
                                    slave_id, dst_pressure)
                                detail.reset_times += 1
                                # 延長 schedule time
                                # __update_schedule_start_time_and_end_time(
                                #     detail.id)
                                current_app.logger.warning(
                                    f"Pressure not reach Festo Slave ID: {slave_id}, Pressure: {festo_pressure}, Dst Pressure: {dst_pressure}, Status: {status}")
                            else:
                                print(
                                f"Festo Slave ID: {slave_id} close valve port")
                                # 到達目標壓力關閉真空閥
                                festo_obj_conn.writePressure(
                                    slave_id, 20000)
                        elif status == 2:
                            # 結束狀態
                            detail.status = 2
                            print(
                                f"End Festo Slave ID: {slave_id}, Pressure: {dst_pressure}, Status: {status}")

                        # 有抓到schedule就結束
                        break

                    elif current_time > detail.time_end:
                        detail.status = 2
                        # 最後一個排成結束了
                        if (index == len(schedule_details)-1) and detail.status == 2:
                            festo_obj_conn.writePressure(slave_id, 0)
                            print(f"stop {festo.name}")

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


@scheduler.task('interval', id='schedule_check_play_mp3', seconds=5)
def schedule_check_play_mp3():
    with scheduler.app.app_context():
        festos = FestoMain.query.all()
        for festo in festos:
            schedule_details = festo.schedule.schedule_details
            for schedule_detail in schedule_details:
                if (schedule_detail.reset_times*5/60 > festo.warning_time) and schedule_detail.status == 1 and schedule_detail.check_pressure:
                    # 播放 MP3 文件
                    pygame.mixer.music.load(mp3_file_path)
                    pygame.mixer.music.play()

                    return
        return


def __update_schedule_start_time_and_end_time(schedule_id):
    current_time = datetime.now()

    schedule = ScheduleDetail.query.filter_by(id=schedule_id).first()

    if schedule:
        new_end_time = current_time + timedelta(minutes=schedule.process_time)
        schedule.time_end = new_end_time

        greater_sequence_details = ScheduleDetail.query.filter(
            (ScheduleDetail.schedule_id == schedule.schedule_id) &
            (ScheduleDetail.sequence > schedule.sequence)
        ).all()

        for detail in greater_sequence_details:

            detail.time_start = new_end_time + timedelta(seconds=1)

            new_end_time = new_end_time + \
                timedelta(minutes=detail.process_time)
            detail.time_end = new_end_time

    else:
        print(f"Schedule with ID {schedule_id} not found.")

    return


def init_scheduler(app):
    try:
        global festo_obj_conn
        festo_obj_conn = festo_obj(current_app.config['COM_PORT'])
    except:
        print("RS485 connect error")
        exit()

    scheduler.init_app(app)
    scheduler.start()
