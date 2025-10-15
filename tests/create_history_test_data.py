"""
創建 FestoHistory 測試資料腳本
用於測試 get_festo_history 功能
"""
from app import app
from models.shared import db
from models.model import FestoHistory
from datetime import datetime, timedelta
import pytz

def create_history_test_data():
    with app.app_context():
        try:
            print("="*60)
            print("開始創建 FestoHistory 高密度測試資料...")
            print("="*60)
            print("⚠️  此腳本將創建大量資料（預計約 100,000+ 筆記錄）")
            print("   資料密度: 每 3 秒一筆記錄")
            print("   創建過程可能需要數分鐘，請耐心等待...")
            print("="*60)
            
            # 使用台北時區
            taipei_tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(taipei_tz)
            
            # 批次號碼
            batch_numbers = ["BATCH-TEST-001", "BATCH-TEST-002", "BATCH-HISTORY-001"]
            
            # 為每個批次創建歷史資料
            total_records = 0
            
            # 批次 1: BATCH-TEST-001 (最近24小時的高密度資料)
            print(f"\n創建批次: BATCH-TEST-001")
            for hour in range(24):
                for minute in range(60):
                    for second in range(0, 60, 3):  # 每3秒一個資料點
                        record_time = current_time - timedelta(hours=hour, minutes=minute, seconds=second)
                        
                        # 為不同的 sequence 創建資料
                        for seq in range(1, 4):  # 3個序列
                            history = FestoHistory(
                                slave_id=1,
                                batch_number="BATCH-TEST-001",
                                formula_name="測試配方A",
                                sequence=seq,
                                pressure=100 + (seq * 25) + (second % 30),  # 變化的壓力值
                                create_time=record_time,
                                update_time=record_time
                            )
                            db.session.add(history)
                            total_records += 1
                            
                            # 每1000筆提交一次，避免記憶體問題
                            if total_records % 1000 == 0:
                                db.session.flush()
                                print(f"  已創建 {total_records} 筆記錄...")
            
            print(f"✓ BATCH-TEST-001: 創建了 {total_records} 筆記錄（每3秒一筆，3個序列）")
            
            # 批次 2: BATCH-TEST-002 (最近12小時的高密度資料)
            print(f"\n創建批次: BATCH-TEST-002")
            batch2_start = total_records
            for hour in range(12):
                for minute in range(60):
                    for second in range(0, 60, 3):  # 每3秒一個資料點
                        record_time = current_time - timedelta(hours=hour, minutes=minute, seconds=second)
                        
                        history = FestoHistory(
                            slave_id=2,
                            batch_number="BATCH-TEST-002",
                            formula_name="測試配方B",
                            sequence=1,
                            pressure=180 + (second % 40),
                            create_time=record_time,
                            update_time=record_time
                        )
                        db.session.add(history)
                        total_records += 1
                        
                        # 每1000筆提交一次
                        if total_records % 1000 == 0:
                            db.session.flush()
                            print(f"  已創建 {total_records} 筆記錄...")
            
            print(f"✓ BATCH-TEST-002: 創建了 {total_records - batch2_start} 筆記錄（每3秒一筆）")
            
            # 批次 3: BATCH-HISTORY-001 (最近6小時的超高密度資料)
            print(f"\n創建批次: BATCH-HISTORY-001")
            batch3_start = total_records
            for hour in range(6):
                for minute in range(60):
                    for second in range(0, 60, 3):  # 每3秒一個資料點
                        record_time = current_time - timedelta(hours=hour, minutes=minute, seconds=second)
                        
                        for seq in range(1, 3):  # 2個序列
                            history = FestoHistory(
                                slave_id=3,
                                batch_number="BATCH-HISTORY-001",
                                formula_name="高壓配方",
                                sequence=seq,
                                pressure=150 + (seq * 30) + (second % 20),
                                create_time=record_time,
                                update_time=record_time
                            )
                            db.session.add(history)
                            total_records += 1
                            
                            # 每1000筆提交一次
                            if total_records % 1000 == 0:
                                db.session.flush()
                                print(f"  已創建 {total_records} 筆記錄...")
            
            print(f"✓ BATCH-HISTORY-001: 創建了 {total_records - batch3_start} 筆記錄（每3秒一筆，2個序列）")
            
            # 提交所有變更
            db.session.commit()
            
            print("\n" + "="*60)
            print("✓ FestoHistory 測試資料創建成功！")
            print("="*60)
            print(f"\n創建的資料摘要:")
            print(f"- 總共創建: {total_records:,} 筆 FestoHistory 記錄")
            print(f"- 批次數量: 3 個")
            print(f"- 資料密度: 每 3 秒一筆記錄")
            print(f"- 時間範圍: {(current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')} ~ {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n批次詳細資訊:")
            print(f"\n1. BATCH-TEST-001:")
            print(f"   - Formula: 測試配方A")
            print(f"   - Slave ID: 1")
            print(f"   - 時間範圍: 最近24小時")
            print(f"   - Sequences: 1, 2, 3")
            print(f"   - 壓力範圍: 100-155")
            print(f"   - 預估記錄數: {24 * 60 * 20 * 3:,} 筆")
            
            print(f"\n2. BATCH-TEST-002:")
            print(f"   - Formula: 測試配方B")
            print(f"   - Slave ID: 2")
            print(f"   - 時間範圍: 最近12小時")
            print(f"   - Sequences: 1")
            print(f"   - 壓力範圍: 180-220")
            print(f"   - 預估記錄數: {12 * 60 * 20:,} 筆")
            
            print(f"\n3. BATCH-HISTORY-001:")
            print(f"   - Formula: 高壓配方")
            print(f"   - Slave ID: 3")
            print(f"   - 時間範圍: 最近6小時")
            print(f"   - Sequences: 1, 2")
            print(f"   - 壓力範圍: 150-210")
            print(f"   - 預估記錄數: {6 * 60 * 20 * 2:,} 筆")
            
            print(f"\n測試 API 範例:")
            print(f"\n1. 查詢 BATCH-TEST-001 的歷史 (按小時聚合):")
            print(f"   POST /history/")
            print(f"   Body: {{")
            print(f"     \"batchNumber\": \"BATCH-TEST-001\",")
            print(f"     \"startTime\": \"{(current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}\",")
            print(f"     \"endTime\": \"{current_time.strftime('%Y-%m-%d %H:%M:%S')}\",")
            print(f"     \"type\": \"hour\"")
            print(f"   }}")
            
            print(f"\n2. 查詢批次號碼列表:")
            print(f"   GET /history/batch?startTime={(current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}&endTime={current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n3. 匯出 CSV (BATCH-HISTORY-001 最近1小時):")
            print(f"   POST /history/export")
            print(f"   Body: {{")
            print(f"     \"batchNumber\": \"BATCH-HISTORY-001\",")
            print(f"     \"startTime\": \"{(current_time - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}\",")
            print(f"     \"endTime\": \"{current_time.strftime('%Y-%m-%d %H:%M:%S')}\"")
            print(f"   }}")
            
            print(f"\n⚠️  注意: 此腳本會創建大量資料（預計 {24*60*20*3 + 12*60*20 + 6*60*20*2:,} 筆記錄）")
            print(f"   創建過程可能需要幾分鐘，請耐心等待...")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.session.close()

if __name__ == "__main__":
    create_history_test_data()
