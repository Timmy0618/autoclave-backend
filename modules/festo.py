import os
from pymodbus.client import ModbusTcpClient


class festo:
    def __init__(self, host, port=502):
        """
        初始化 Festo 連接（透過 Modbus/TCP）
        
        Args:
            host: RS485 轉以太網設備的 IP 位址
            port: TCP 連接埠 (預設 502)
        """
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host, port=port, timeout=5, retries=3)
        self._connect()

    def _ensure_connection(self):
        """
        確保連線處於可用狀態；如果被閒置斷線則重新連線。
        返回 bool 代表目前是否可用。
        """
        if self.client and getattr(self.client, "connected", False):
            return True
        return self._connect()
    
    def _connect(self):
        """建立連接"""
        try:
            if self.client and self.client.connected:
                return True
            
            # 嘗試連接
            result = self.client.connect()
            
            # pymodbus 的 connect() 通常返回 True 或拋出異常
            # 如果沒有拋出異常，我們認為連接成功
            if result is True or result is None:  # 有些版本返回 None
                # 額外驗證連接是否真的有效
                if hasattr(self.client, 'connected') and self.client.connected:
                    print(f"✓ Successfully connected to {self.host}:{self.port}")
                    return True
                else:
                    print(f"✗ Connection established but not confirmed")
                    return False
            else:
                print(f"✗ Failed to connect to {self.host}:{self.port}")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def _call(self, fn, *args, **kwargs):
        """
        統一的 Modbus 調用包裝，先確保連線，失敗才重連（無 heartbeat）。
        為避免閒置後的半開連線，每次操作前都刷新連線。
        """
        # 避免半開連線：先關閉舊 socket，再重新建立
        if self.client:
            self.client.close()
        if not self._connect():
            print("Modbus operation failed: connection not available")
            return None
        try:
            # 直接嘗試操作，不預先檢查連接
            resp = fn(*args, **kwargs)
            if resp.isError():
                raise IOError(f"Modbus error: {resp}")
            return resp
        except Exception as e:
            # 收到斷線後，先嘗試重新連線再重試，不預先噴錯
            if self.client:
                self.client.close()
            if self._connect():
                try:
                    print("Retrying operation after reconnect...")
                    resp = fn(*args, **kwargs)
                    if resp.isError():
                        raise IOError(f"Modbus error after reconnect: {resp}")
                    print("✓ Operation succeeded after reconnect")
                    return resp
                except Exception as e2:
                    print(f"Retry after reconnect also failed: {e2}")
            print(f"Modbus operation failed: {e}")
            return None

    def readSetPressure(self, id):
        """讀取設定壓力 (Holding Register 0)"""
        rr = self._call(
            self.client.read_holding_registers,
            address=0, count=1, device_id=id
        )
        if rr is None:
            return None
        value = rr.registers[0]
        return round(value / 100 - 100, 2)

    def readVacuumPressure(self, id):
        """讀取真空壓力 (Input Register 1)"""
        ri = self._call(
            self.client.read_input_registers,
            address=1, count=1, device_id=id
        )
        if ri is None:
            return None
        value = ri.registers[0]
        return round(value / 100 - 100, 2)

    def readChamberPressure(self, id):
        """讀取腔室壓力 (Input Register 2)"""
        ri = self._call(
            self.client.read_input_registers,
            address=2, count=1, device_id=id
        )
        if ri is None:
            return None
        value = ri.registers[0]
        return value / 100

    def readMulti(self, id):
        """讀取 PID 參數 (Holding Registers 3-6)"""
        rr = self._call(
            self.client.read_holding_registers,
            address=3, count=4, device_id=id
        )
        if rr is None:
            return None
        kp, ki, kd, step = rr.registers
        return {"kp": kp, "ki": ki, "kd": kd, "step": step}

    def writePressure(self, id, pressure):
        """寫入目標壓力 (Holding Register 0)"""
        value = int((pressure + 100) * 100)
        print(f"Writing pressure: {pressure} -> register value: {value} to device {id}")
        wr = self._call(
            self.client.write_register,
            address=0, value=value, device_id=id
        )
        if wr is None:
            return False
        print(f"✓ Successfully wrote pressure")
        return True

    def writeKp(self, id, kp):
        """寫入 Kp (Holding Register 3)"""
        wr = self._call(
            self.client.write_register,
            address=3, value=kp, device_id=id
        )
        return wr is not None

    def writeMulti(self, id, kp, ki, kd, step):
        """寫入 PID 參數 (Holding Registers 3-6)"""
        values = [kp, ki, kd, step]
        wr = self._call(
            self.client.write_registers,
            address=3, values=values, device_id=id
        )
        return wr is not None

    def close(self):
        """關閉連接"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            self.client = None

    def __del__(self):
        """析構函數，確保連接被關閉"""
        self.close()


if __name__ == "__main__":
    print("Start")
    # 使用環境變數讀取 IP 和端口
    host = os.environ.get('FESTO_HOST', '192.168.0.87')
    port = int(os.environ.get('FESTO_PORT', 502))
    festoObj = festo(host, port)
    while True:
        try:
            id = int(input("請輸入機器id:"))
            inputText = input("請輸入指令:")
            if inputText == 'chamber':
                chamberPressure = festoObj.readChamberPressure(id)
                print('chamberPressure: %s' % (chamberPressure))
            elif inputText == 'vacuum':
                vacuumPressure = festoObj.readVacuumPressure(id)
                print('vacuumPressure: %s' % (vacuumPressure))
            elif inputText == 'set':
                pressure = float(input("請輸入壓力值:"))
                result = festoObj.writePressure(id, pressure)
                print('Write pressure result: %s' % result)
            elif inputText == 'readmulti':
                result = festoObj.readMulti(id)
                print(result)
            elif inputText == 'writemulti':
                kp = int(input("請輸入 Kp:"))
                ki = int(input("請輸入 Ki:"))
                kd = int(input("請輸入 Kd:"))
                step = int(input("請輸入 Step:"))
                result = festoObj.writeMulti(id, kp, ki, kd, step)
                print('Write multi result: %s' % result)
            elif inputText == 'readsetpressure':
                result = festoObj.readSetPressure(id)
                print(result)
            elif inputText == 'exit':
                festoObj.close()
                break
            else:
                print("未知指令")
        except ValueError:
            print("請輸入有效的數字")
        except Exception as e:
            print(f"錯誤: {e}")
