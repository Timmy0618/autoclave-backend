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
    
    def _connect(self):
        """建立連接"""
        try:
            if self.client and self.client.connected:
                return True
            result = self.client.connect()
            if result:
                print(f"✓ Successfully connected to {self.host}:{self.port}")
                return True
            else:
                print(f"✗ Failed to connect to {self.host}:{self.port}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def _ensure_connection(self):
        """確保連接有效，必要時重新連接"""
        if not self.client:
            return False
        if not self.client.connected:
            print("Connection lost, attempting to reconnect...")
            return self._connect()
        return True

    def readSetPressure(self, id):
        """讀取設定壓力 (Holding Register 0)"""
        if not self._ensure_connection():
            return None
        try:
            rr = self.client.read_holding_registers(address=0, count=1, device_id=id)
            if rr.isError():
                print(f"Error reading set pressure: {rr}")
                return None
            value = rr.registers[0]
            return round(value / 100 - 100, 2)
        except Exception as e:
            print(f"Exception reading set pressure: {e}")
            return None

    def readVacuumPressure(self, id):
        """讀取真空壓力 (Input Register 1)"""
        if not self._ensure_connection():
            return None
        try:
            ri = self.client.read_input_registers(address=1, count=1, device_id=id)
            if ri.isError():
                print(f"Error reading vacuum pressure: {ri}")
                return None
            value = ri.registers[0]
            return round(value / 100 - 100, 2)
        except Exception as e:
            print(f"Exception reading vacuum pressure: {e}")
            return None

    def readChamberPressure(self, id):
        """讀取腔室壓力 (Input Register 2)"""
        if not self._ensure_connection():
            return None
        try:
            ri = self.client.read_input_registers(address=2, count=1, device_id=id)
            if ri.isError():
                print(f"Error reading chamber pressure: {ri}")
                return None
            value = ri.registers[0]
            return value / 100
        except Exception as e:
            print(f"Exception reading chamber pressure: {e}")
            return None

    def readMulti(self, id):
        """讀取 PID 參數 (Holding Registers 3-6)"""
        if not self._ensure_connection():
            return None
        try:
            rr = self.client.read_holding_registers(address=3, count=4, device_id=id)
            if rr.isError():
                print(f"Error reading multi: {rr}")
                return None
            kp, ki, kd, step = rr.registers
            return {"kp": kp, "ki": ki, "kd": kd, "step": step}
        except Exception as e:
            print(f"Exception reading multi: {e}")
            return None

    def writePressure(self, id, pressure):
        """寫入目標壓力 (Holding Register 0)"""
        if not self._ensure_connection():
            return False
        try:
            value = int((pressure + 100) * 100)
            print(f"Writing pressure: {pressure} -> register value: {value} to device {id}")
            wr = self.client.write_register(address=0, value=value, device_id=id)
            if wr.isError():
                print(f"Error writing pressure: {wr}")
                return False
            print(f"✓ Successfully wrote pressure")
            return True
        except Exception as e:
            print(f"Exception writing pressure: {e}")
            return False

    def writeKp(self, id, kp):
        """寫入 Kp (Holding Register 3)"""
        if not self._ensure_connection():
            return False
        try:
            wr = self.client.write_register(address=3, value=kp, device_id=id)
            if wr.isError():
                print(f"Error writing Kp: {wr}")
                return False
            return True
        except Exception as e:
            print(f"Exception writing Kp: {e}")
            return False

    def writeMulti(self, id, kp, ki, kd, step):
        """寫入 PID 參數 (Holding Registers 3-6)"""
        if not self._ensure_connection():
            return False
        try:
            values = [kp, ki, kd, step]
            wr = self.client.write_registers(address=3, values=values, device_id=id)
            if wr.isError():
                print(f"Error writing multi: {wr}")
                return False
            return True
        except Exception as e:
            print(f"Exception writing multi: {e}")
            return False

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
