"""
創建測試資料腳本
用於測試 get_currently_executing_info 功能
"""
from app import app
from models.shared import db
from models.festo import FestoMain
from models.formula import FormulaMain, FormulaDetail
from models.schedule import Schedule, ScheduleDetail
from models.pid import Pid
from datetime import datetime, timedelta

def create_test_data():
    with app.app_context():
        try:
            # 清理現有測試資料（可選）
            print("開始創建測試資料...")
            
            # 1. 創建 PID（如果不存在）
            pid = Pid.query.filter_by(id=1).first()
            if not pid:
                pid = Pid(
                    id=1,
                    kp=10,
                    ki=5,
                    kd=2,
                    step=1,
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
                db.session.add(pid)
                print("✓ 創建 PID")
            else:
                print("✓ PID 已存在")
            
            # 2. 創建 Formula
            formula1 = FormulaMain(
                name="測試配方A",
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(formula1)
            db.session.flush()
            print(f"✓ 創建配方: {formula1.name}")
            
            # 3. 創建 Formula Details
            formula_details = [
                FormulaDetail(
                    formula_main_id=formula1.id,
                    sequence=1,
                    pressure=100,
                    process_time=10,  # 10分鐘
                    create_time=datetime.now(),
                    update_time=datetime.now()
                ),
                FormulaDetail(
                    formula_main_id=formula1.id,
                    sequence=2,
                    pressure=150,
                    process_time=15,  # 15分鐘
                    create_time=datetime.now(),
                    update_time=datetime.now()
                ),
                FormulaDetail(
                    formula_main_id=formula1.id,
                    sequence=3,
                    pressure=200,
                    process_time=20,  # 20分鐘
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
            ]
            for detail in formula_details:
                db.session.add(detail)
            print(f"✓ 創建 {len(formula_details)} 個配方詳細資料")
            
            # 4. 創建 FestoMain
            festo1 = FestoMain(
                name="測試設備1",
                formula_main_id=formula1.id,
                slave_id=1,
                batch_number="BATCH-TEST-001",
                warning_time=60,  # 60秒
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(festo1)
            db.session.flush()
            print(f"✓ 創建 Festo: {festo1.name}")
            
            # 5. 創建 Schedule
            schedule1 = Schedule(
                festo_main_id=festo1.id,
                pid_id=1,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(schedule1)
            db.session.flush()
            print(f"✓ 創建 Schedule for {festo1.name}")
            
            # 6. 創建 Schedule Details（包含當前時間的執行排程）
            current_time = datetime.now()
            
            # 第一個階段：已完成（過去的時間）
            schedule_detail1 = ScheduleDetail(
                schedule_id=schedule1.id,
                sequence=1,
                pressure=100,
                status=1,  # 已完成
                check_pressure=True,
                process_time=10,
                reset_times=0,
                time_start=current_time - timedelta(minutes=25),
                time_end=current_time - timedelta(minutes=15),
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            
            # 第二個階段：正在執行（包含當前時間）
            schedule_detail2 = ScheduleDetail(
                schedule_id=schedule1.id,
                sequence=2,
                pressure=150,
                status=0,  # 正在執行
                check_pressure=True,
                process_time=15,
                reset_times=0,
                time_start=current_time - timedelta(minutes=5),  # 5分鐘前開始
                time_end=current_time + timedelta(minutes=10),   # 10分鐘後結束
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            
            # 第三個階段：待執行（未來的時間）
            schedule_detail3 = ScheduleDetail(
                schedule_id=schedule1.id,
                sequence=3,
                pressure=200,
                status=2,  # 待執行
                check_pressure=False,
                process_time=20,
                reset_times=0,
                time_start=current_time + timedelta(minutes=11),
                time_end=current_time + timedelta(minutes=31),
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            
            db.session.add(schedule_detail1)
            db.session.add(schedule_detail2)
            db.session.add(schedule_detail3)
            print(f"✓ 創建 3 個 Schedule Details")
            
            # 7. 再創建一個 Festo 設備用於測試
            formula2 = FormulaMain(
                name="測試配方B",
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(formula2)
            db.session.flush()
            
            formula_detail2 = FormulaDetail(
                formula_main_id=formula2.id,
                sequence=1,
                pressure=180,
                process_time=30,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(formula_detail2)
            
            festo2 = FestoMain(
                name="測試設備2",
                formula_main_id=formula2.id,
                slave_id=2,
                batch_number="BATCH-TEST-002",
                warning_time=120,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(festo2)
            db.session.flush()
            
            schedule2 = Schedule(
                festo_main_id=festo2.id,
                pid_id=1,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(schedule2)
            db.session.flush()
            
            # 創建一個正在執行的排程
            schedule_detail4 = ScheduleDetail(
                schedule_id=schedule2.id,
                sequence=1,
                pressure=180,
                status=0,  # 正在執行
                check_pressure=True,
                process_time=30,
                reset_times=0,
                time_start=current_time - timedelta(minutes=10),
                time_end=current_time + timedelta(minutes=20),
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.session.add(schedule_detail4)
            print(f"✓ 創建第二個 Festo 及其排程")
            
            # 提交所有變更
            db.session.commit()
            
            print("\n" + "="*50)
            print("✓ 測試資料創建成功！")
            print("="*50)
            print(f"\n創建的資料摘要:")
            print(f"- 2 個 Festo 設備")
            print(f"- 2 個配方")
            print(f"- 4 個配方詳細資料")
            print(f"- 2 個排程")
            print(f"- 4 個排程詳細資料")
            print(f"\n當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n測試設備1 ({festo1.name}):")
            print(f"  - 階段2 正在執行中")
            print(f"  - 時間範圍: {schedule_detail2.time_start.strftime('%H:%M:%S')} ~ {schedule_detail2.time_end.strftime('%H:%M:%S')}")
            print(f"  - 壓力: {schedule_detail2.pressure}")
            print(f"\n測試設備2 ({festo2.name}):")
            print(f"  - 階段1 正在執行中")
            print(f"  - 時間範圍: {schedule_detail4.time_start.strftime('%H:%M:%S')} ~ {schedule_detail4.time_end.strftime('%H:%M:%S')}")
            print(f"  - 壓力: {schedule_detail4.pressure}")
            print(f"\n現在可以調用 GET /festo/executing 來查看執行中的設備資訊")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.session.close()

if __name__ == "__main__":
    create_test_data()
