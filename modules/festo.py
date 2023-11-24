from crcmod import *
import serial
import time


class festo:
    def __init__(self, COMPort):
        try:
            self.ser = ""
            self.ser = serial.Serial(COMPort, baudrate=115200, timeout=3)
            self.slaveId = ""
            self.funcCode = ""
            self.bytesCount = ""
            self.data = ""
            self.crc16 = ""
            self.ex = ""
        except serial.SerialException as ex:
            self.ex = ex
            print(ex)
            return False

    def print_response(self):
        print("""slaveId: %s\nfuncCode: %s\nbytesCount: %s\ndata: %s\ncrc16:%s """
              % (
                  (", ".join(hex(b) for b in self.slaveId)),
                  (", ".join(hex(b) for b in self.funcCode)),
                  (", ".join(hex(b) for b in self.bytesCount)),
                  (", ".join(hex(b) for b in self.data)),
                  (", ".join(hex(b) for b in self.crc16))))

    def readSetPressure(self, id):
        inputData = [id, 3, 0, 0, 0, 1]
        crc16 = self.__crc16_maxim(inputData)
        inputData += crc16
        bytes_data = bytearray(inputData)
        self.ser.write(bytes_data)
        self.__print_bytes_array(bytes_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(7)
        self.__print_bytes_array(response, flag='read')
        print("CRC checK: ", self.__checkCRC(response[:-2], response[-2:]))
        self.__setValue(response)
        result = round(int.from_bytes(self.data, "big")/100-100, 2)

        return result

    # Read the vacuum pressure value of pressure sensor feedback
    def readVacuumPressure(self, id):
        inputData = [id, 4, 0, 1, 0, 1]
        crc16 = self.__crc16_maxim(inputData)
        inputData += crc16
        bytes_data = bytearray(inputData)
        self.ser.write(bytes_data)
        self.__print_bytes_array(bytes_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(7)
        self.__print_bytes_array(response, flag='read')
        print("CRC checK: ", self.__checkCRC(response[:-2], response[-2:]))
        self.__setValue(response)
        result = round(int.from_bytes(self.data, "big")/100-100, 2)

        return result

    # Read the feedback pressure value of pressure sensor in pilot chamber (0~600kPa)
    def readChamberPressure(self, id):
        inputData = [id, 4, 0, 2, 0, 1]
        crc16 = self.__crc16_maxim(inputData)
        inputData += crc16
        bytes_data = bytearray(inputData)
        self.ser.write(bytes_data)
        self.__print_bytes_array(bytes_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(7)
        self.__print_bytes_array(response, flag='read')
        checkResult = self.__checkCRC(response[:-2], response[-2:])
        print("CRC checK: ", checkResult)
        self.__setValue(response)

        if (checkResult):
            return int.from_bytes(self.data, "big")/100
        else:
            return "Fail"

    # Read all PID parameter Kp, Ki, Kd, Step
    def readMulti(self, id):
        inputData = [id, 3, 0, 3, 0, 4]
        crc16 = self.__crc16_maxim(inputData)
        inputData += crc16
        bytes_data = bytearray(inputData)
        self.ser.write(bytes_data)
        self.__print_bytes_array(bytes_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(13)
        self.__print_bytes_array(response, flag='read')
        print("CRC checK: ", self.__checkCRC(response[:-2], response[-2:]))
        self.__setValue(response)

        # kp,ki,kd,step
        result = []
        for i in range(int(self.bytesCount[0]/2)):
            result.append(int.from_bytes(self.data[i*2:(i+1)*2], "big"))
        result = {"kp": result[0], "ki": result[1],
                  "kd": result[2], "step": result[3]}

        return result

    # Write a target pressure value
    def writePressure(self, id, pressure):
        pressure = int((pressure + 100) * 100)
        inputData = [id, 6, 0, 0]
        pressureDec = self.__decToByteAry(pressure)
        if (len(pressureDec) == 1):
            pressureDec = [0]+pressureDec
        crc16 = self.__crc16_maxim(inputData + pressureDec)
        inputData += (pressureDec+crc16)
        # Create a bytes object from the integers
        byte_data = bytearray(inputData)
        self.ser.write(byte_data)
        self.__print_bytes_array(byte_data)
        time.sleep(1)
        response = self.ser.read(8)
        self.__print_bytes_array(response, flag='read')
        checkResult = self.__checkCRC(response[:-2], response[-2:])
        print("CRC check: ", checkResult)
        self.__setValue1(response)

        return checkResult

    # write Kp of proportional coefficients in PID parameters

    def writeKp(self, id, kp):
        inputData = [id, 6, 0, 3]
        kpDec = self.__decToByteAry(kp)
        crc16 = self.__crc16_maxim(inputData+kpDec)
        inputData = inputData+kpDec+crc16
        byte_data = bytearray(inputData)
        self.ser.write(byte_data)
        self.__print_bytes_array(byte_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(8)
        print("read 8 byte data:", (", ".join(hex(b) for b in response)))
        print("CRC checK: ", self.__checkCRC(response[:-2], response[-2:]))
        self.__setValue(response)

    # write all PID parameter Kp, ki, kd, Step
    def writeMulti(self, id, kp, ki, kd, step):
        inputData = [id, 16, 0, 3, 0, 4, 8]
        kpDec = self.__decToByteAry(kp)
        kiDec = self.__decToByteAry(ki)
        kdDec = self.__decToByteAry(kd)
        stepDec = self.__decToByteAry(step)
        crc16 = self.__crc16_maxim(inputData+kpDec+kiDec+kdDec+stepDec)
        inputData = inputData+kpDec+kiDec+kdDec+stepDec+crc16
        byte_data = bytearray(inputData)
        self.ser.write(byte_data)
        self.__print_bytes_array(byte_data)
        time.sleep(0.5)  # wait 0.5s
        response = self.ser.read(8)
        self.__print_bytes_array(response, flag='read')
        print("CRC checK: ", self.__checkCRC(response[:-2], response[-2:]))
        self.__setValue(response)

    def __decToByteAry(self, dec):
        result = []
        hexString = f'{dec:x}'
        if len(hexString) % 2 != 0:
            hexString = '0'+hexString
        for i in bytearray.fromhex(hexString):
            result.append(i)

        return result

    def __crc16_maxim(self, read):
        r = bytes(bytearray(read))
        crc16 = crcmod.mkCrcFun(
            0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        crc_hex = hex(crc16(r))
        crc = divmod(int(crc_hex, 16), 0x100)
        return [crc[1], crc[0]]

    def __checkCRC(self, inputData, crcRes):
        # Check if the lengths of inputData and crcRes are as expected
        if len(inputData) < 2 or len(crcRes) < 2:
            return False

        flag = True
        computedCRC = self.__crc16_maxim(inputData)
        for i in range(2):
            if (computedCRC[i] != crcRes[i]):
                flag = False
                break

        return flag

    def __setValue(self, response):
        self.slaveId = [response[0]]
        self.funcCode = [response[1]]
        self.bytesCount = [response[2]]
        self.data = response[3:3+int(self.bytesCount[0])]
        self.crc16 = response[3+int(self.bytesCount[0]):]

    # for write
    def __setValue1(self, response):
        # Check if the length of response is as expected (at least 7 elements)
        if len(response) >= 7:
            self.slaveId = [response[0]]
            self.funcCode = [response[1]]
            self.bytesCount = response[2:3]
            self.data = response[4:6]
            self.crc16 = response[6:]
        else:
            # Handle the case when the response doesn't have enough elements
            # You can add appropriate error handling here
            print("Error: Response does not have enough elements")

    def __print_bytes_array(self, byte_array, flag='write'):
        # print(f"{flag} {len(byte_array)} bytes:")
        # for i in range(0, len(byte_array), 2):
        #     chunk = byte_array[i:i+2]
        #     print(chunk.hex(), end=' ')
        # print("\n")
        return


if __name__ == "__main__":
    print("Start")
    comPort = '/dev/cu.usbserial-LKAC390507'
    festoObj = festo(comPort)
    while (True):
        id = int(input("請輸入機器id:"))
        inputText = input("請輸入指令:")
        if (inputText == 'chamber'):
            chamberPressure = festoObj.readChamberPressure(id)
            print('chamberPressure: %s' % (chamberPressure))
        if (inputText == 'vacuum'):
            vacuumPressure = festoObj.readVacuumPressure(id)
            print('vacuumPressure: %s' % (vacuumPressure))
        if (inputText == 'set'):
            pressure = input("請輸入壓力值:")
            vacuumPressure = festoObj.writePressure(id, float(pressure))
        if (inputText == 'readmulti'):
            result = festoObj.readMulti(id)
            print(result)
        if (inputText == 'writemulti'):
            festoObj.writeMulti(id, 1500, 500, 800, 600)
        if (inputText == 'readsetpressure'):
            result = festoObj.readSetPressure(id)
            print(result)
