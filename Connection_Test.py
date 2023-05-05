import serial
import time

ser = serial.Serial('COM3', 19200)
print(ser.is_open)

ser.write(b'r')

output = ser.readline()
ser.flush()

print(output)
time.sleep(1)

ser.close()
print(ser.is_open)
