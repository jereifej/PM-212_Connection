import tkinter as tk
from tkinter import *
import serial
import serial.tools.list_ports
import time
import threading
import numpy as np

global meters_exists, meters_single, meters_cont, measurements

BAUD = 19200
launch_time = time.time()

root = tk.Tk()
root.geometry("200x200")
root.title("Power Measurement")

# TODO Add Global Measurement (Single & Continuous)
# TODO Implement Functionality to Remove Meters

def MeasureOnThread(COM, entry, idx):
    print("new thread on " + str(idx))
    global is_on
    ser = serial.Serial(COM, BAUD)
    start = time.time()
    while is_on[idx]:
        ser.write(b'v')
        output = ser.readline()

        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        # entry.insert(0, time.time()-start)  # for debugging!!!
        time.sleep(.1)
    print("done!")
    ser.close()


def TakeSingleMeasurement(COM, entry, idx):
    if not is_on[idx]:
        ser = serial.Serial(COM, BAUD)
        ser.write(b'v')
        output = ser.readline()
        print(idx)
        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        # entry.insert(0, time.time()-launch_time)  # for debugging!!!
        ser.close()


def TakeContMeasurement(COM, entry, this_button, idx):
    global is_on
    if not is_on[idx]:
        is_on[idx] = True
        this_button.config(fg="black", bg="yellow")
        t1 = threading.Thread(daemon=True, target=MeasureOnThread, args=(COM, entry, idx))
        print(COM)
        t1.start()
    else:
        is_on[idx] = False
        this_button.config(fg="black", bg="white")


def DisplayMeasurementGUI(COM, idx):
    print(COM)
    print(idx)
    global meters_single, meters_cont, measurements

    COM_title = tk.Label(text=COM, fg="black", bg="white")
    COM_title.pack()
    measurements[idx] = tk.Entry(justify="center")
    measurements[idx].insert(0, "dB")
    measurements[idx].pack()

    meters_single[idx] = tk.Button(text="Measure", command=lambda: TakeSingleMeasurement(COM, measurements[idx], idx),
                                   fg="black", bg="white")
    meters_single[idx].pack()

    meters_cont[idx] = tk.Button(text="Continuous Measure",
                                       command=lambda: TakeContMeasurement(COM, measurements[idx],
                                                                           meters_cont[idx], idx),
                                       fg="black", bg="white")
    meters_cont[idx].pack()


def RemoveMeasurementGUI(COM, idx):
    return


def UpdateMeters(checklist, varlist):
    global meters_exists
    for i in range(len(checklist)):
        com = checklist[i].cget('text')
        if varlist[i].get() == 1 and not meters_exists[i]:
            meters_exists[i] = True
            DisplayMeasurementGUI(com, i)
        elif varlist[i].get() == 0 and meters_exists[i]:
            RemoveMeasurementGUI(com, i)


# Here lies the actual code
ports = serial.tools.list_ports.comports()

checklist = np.empty(shape=(len(ports),), dtype=tk.Checkbutton)
varlist = np.empty(shape=(len(ports),), dtype=IntVar)

global is_on, meters_exists, meters_single, meters_cont, measurements
is_on = np.full_like(checklist, False)
meters_exists = np.full_like(checklist, False)
meters_single = np.empty_like(checklist, dtype=tk.Button)
meters_cont = np.empty_like(checklist, dtype=tk.Button)
measurements = np.empty_like(checklist, dtype=tk.Entry)

for i in range(len(checklist)):
    ID = ports[i][0]
    varlist[i] = IntVar()
    checklist[i] = tk.Checkbutton(root, text=ID, variable=varlist[i], onvalue=1, offvalue=0,
                                  command=lambda: UpdateMeters(checklist, varlist))
    checklist[i].pack()

root.mainloop()
is_on = False
