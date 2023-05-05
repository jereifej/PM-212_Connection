import tkinter as tk
from tkinter import *
import serial
import serial.tools.list_ports
import time
import threading
import numpy as np

BAUD = 19200



root = tk.Tk()
root.geometry("200x200")
root.title("Power Measurement")

def MeasureOnThread(COM, entry):
    global is_on
    ser = serial.Serial(COM, BAUD)
    while is_on:
        ser.write(b'v')
        output = ser.readline()

        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        time.sleep(.1)
    print("done!")
    ser.close()

def TakeSingleMeasurement(COM, entry):
    if not is_on:
        ser = serial.Serial(COM, BAUD)
        ser.write(b'v')
        output = ser.readline()

        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        ser.close()


is_on = False
def TakeContMeasurement(COM, entry, this_button):
    global is_on
    if not is_on:
        is_on = True
        this_button.config(fg="black", bg="yellow")
        t1 = threading.Thread(daemon=True, target=MeasureOnThread, args=(COM, entry))
        t1.start()
    else:
        is_on = False
        this_button.config(fg="black", bg="white")

def DisplayMeasurementGUI(COM):
    measure_entry = tk.Entry(justify="center")
    measure_entry.insert(0, "dB")
    measure_entry.pack()

    single_measurement = tk.Button(text="Measure", command=lambda: TakeSingleMeasurement(COM, measure_entry),
                                   fg="black", bg="white")
    single_measurement.pack()

    continuous_measurement = tk.Button(text="Continuous Measure",
                                       command=lambda: TakeContMeasurement(COM, measure_entry,
                                                                           continuous_measurement),
                                       fg="black", bg="white")
    continuous_measurement.pack()

def RemoveMeasurementGUI(COM):
    return

def PrintCheckList(checklist, varlist):
    for i in range(len(checklist)):
        com = checklist[i].cget('text')
        if varlist[i].get() == 1:
            DisplayMeasurementGUI(com)
        else:
            RemoveMeasurementGUI(com)


ports = serial.tools.list_ports.comports()
checklist = np.empty(shape=(len(ports),), dtype=tk.Checkbutton)
varlist = np.empty(shape=(len(ports),), dtype=IntVar)
for i in range(len(checklist)):
    ID = ports[i][0]
    varlist[i] = IntVar()
    checklist[i] = tk.Checkbutton(root, text=ID,variable=varlist[i], onvalue=1, offvalue=0, command=lambda: PrintCheckList(checklist, varlist))
    checklist[i].pack()

root.mainloop()
is_on = False

