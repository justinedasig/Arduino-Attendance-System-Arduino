import serial
import requests

arduino = serial.Serial("COM3", 9600)

print("Listening...")

while True:
    line = arduino.readline().decode().strip()
    print("Arduino:", line)

    # RFID LOGIN
    if line.startswith("RFID:"):
        uid = line.replace("RFID:", "")
        requests.get("http://127.0.0.1:8000/api/rfid/", params={"uid": uid})

    # STUDENT ID LOGIN
    if line.startswith("STUDENT:"):
        sid = line.replace("STUDENT:", "")
        requests.get("http://127.0.0.1:8000/api/student/", params={"id": sid})