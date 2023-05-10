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
root.title("Power Measurement")


# Method to offload continuous polling of device to Daemon Thread
def MeasureOnThread(COM, entry, idx):
    global is_on

    ser = serial.Serial(COM, BAUD, timeout=.1)
    start = time.time()

    # While the continuous run button is still on, keep reading!
    while is_on[idx]:
        ser.write(b'v')
        output = ser.readline()
        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        # entry.insert(0, str(round((time.time()-start), 2)) + " dBm")  # for debugging!!!
        time.sleep(.1)
    ser.close()


# Method to take Single Measurement of selected meter
def TakeSingleMeasurement(COM, entry, idx):
    if not is_on[idx]:
        ser = serial.Serial(COM, BAUD, timeout=.1)
        ser.write(b'v')
        output = ser.readline()
        entry.delete(0, "end")
        entry.insert(0, output.decode() + " dB")
        # entry.insert(0, time.time()-launch_time)  # for debugging!!!
        ser.close()


# Method to start Continuous Measurement of selected meter
def TakeContMeasurement(COM, entry, this_button, idx, set_all):
    global is_on
    if not is_on[idx]:
        is_on[idx] = True
        this_button.config(fg="black", bg="yellow")

        # Why did I use a Daemon Thread?
        # Because it closes the serial connection upon closing the program.
        # Bad Programming Practice? Maybe.
        # Solves the problem? Also, maybe.
        t1 = threading.Thread(daemon=True, target=MeasureOnThread, args=(COM, entry, idx))
        t1.start()
    elif not set_all:
        is_on[idx] = False
        this_button.config(fg="black", bg="white")


# Method to stop Continuous Measurement of selected meter
def StopContMeasurement(this_button, idx):
    is_on[idx] = False
    this_button.config(fg="black", bg="white")


# Method to start Continuous Measurement of all active meters
def TakeContMeasurementAll(comlist):
    global meters_exists, measurements, meters_cont, is_on
    for idx in range(len(meters_exists)):
        if meters_exists[idx]:
            com = checklist[idx].cget('text')
            TakeContMeasurement(com, measurements[idx], meters_cont[idx], idx, True)


# Method to stop Continuous Measurement of all active meters
def StopContMeasurementAll(comlist):
    global meters_exists, measurements, meters_cont, is_on
    for idx in range(len(meters_exists)):
        if meters_exists[idx] and is_on[idx]:
            com = checklist[idx].cget('text')
            StopContMeasurement(meters_cont[idx], idx)


# Method to take Single Measurement of all active meters
def TakeSingleMeasurementAll(comlist):
    global meters_exists, measurements, meters_single
    for idx in range(len(meters_exists)):
        if meters_exists[idx]:
            com = checklist[idx].cget('text')
            TakeSingleMeasurement(com, measurements[idx], idx)


# Adds GUI objects when COM is checked
def DisplayMeasurementGUI(COM, idx):
    global meters_single, meters_cont, measurements

    # tk.Entry for measurement output
    measurements[idx] = tk.Entry(justify="center")
    measurements[idx].insert(0, "dB")
    measurements[idx].grid(row=idx, column=1)

    # tk.Button for single measure
    meters_single[idx] = tk.Button(text="Measure", command=lambda: TakeSingleMeasurement(COM, measurements[idx], idx),
                                   fg="black", bg="white")
    meters_single[idx].grid(row=idx, column=2)

    # tk.Button for continuous measure
    meters_cont[idx] = tk.Button(text="Continuous Measure",
                                       command=lambda: TakeContMeasurement(COM, measurements[idx],
                                                                           meters_cont[idx], idx, False),
                                       fg="black", bg="white")
    meters_cont[idx].grid(row=idx, column=3, padx=(5, 5), pady=(2, 2))
    root.geometry("")


# Removes GUI objects when COM is unchecked
def RemoveMeasurementGUI(COM, idx):
    meters_single[idx].grid_remove()
    meters_cont[idx].grid_remove()
    measurements[idx].grid_remove()
    return

# Whenever checklist is updated, go through and add/remove any buttons
def UpdateMeters(checklist, varlist):
    global meters_exists
    for i in range(len(checklist)):
        com = checklist[i].cget('text')
        if varlist[i].get() == 1 and not meters_exists[i]:
            meters_exists[i] = True
            DisplayMeasurementGUI(com, i)
        elif varlist[i].get() == 0 and meters_exists[i]:
            meters_exists[i] = False
            RemoveMeasurementGUI(com, i)


# Here lies the actual code
ports = serial.tools.list_ports.comports()  # get all COM ports

# for keeping track of selected COM ports
checklist = np.empty(shape=(len(ports),), dtype=tk.Checkbutton)
varlist = np.empty(shape=(len(ports),), dtype=IntVar)

# is_on - for all COM ports, if continuous read is on
# meters_exist - for all COM ports, if port is checked = True
# meters_single - np.array for single measure tk.Button
# meters_cont - np.array for continuous measure tk.Button
# measurements - np.array for measurement output tk.Entry
global is_on, meters_exists, meters_single, meters_cont, measurements
is_on = np.full_like(checklist, False)
meters_exists = np.full_like(checklist, False)
meters_single = np.empty_like(checklist, dtype=tk.Button)
meters_cont = np.empty_like(checklist, dtype=tk.Button)
measurements = np.empty_like(checklist, dtype=tk.Entry)
ports = sorted(ports)  # sort in increasing numeric order

# Placing all the widgets
for i in range(len(checklist)):
    ID = ports[i][0]
    varlist[i] = IntVar()
    checklist[i] = tk.Checkbutton(root, text=ID, variable=varlist[i], onvalue=1, offvalue=0,
                                  command=lambda: UpdateMeters(checklist, varlist))
    checklist[i].grid(row=i, column=0)

# Single Measure All
single_measureAllButton = tk.Button(text="Single Measure All", fg="black", bg="white",
                                    command=lambda: TakeSingleMeasurementAll(checklist))
single_measureAllButton.grid(row=len(checklist), column=0, padx=(5, 10), pady=(10, 10))

# Continuous Measure All start
cont_measureAllButton = tk.Button(text="Continuous Measure All", fg="black", bg="white",
                                  command=lambda: TakeContMeasurementAll(checklist))
cont_measureAllButton.grid(row=len(checklist), column=1, padx=(5, 10), pady=(10, 10))

# Continuous Measure All stop
cont_measureAllButton_stop = tk.Button(text="Stop Measure All", fg="black", bg="white",
                                  command=lambda: StopContMeasurementAll(checklist))
cont_measureAllButton_stop.grid(row=len(checklist), column=2, padx=(5, 10))

root.mainloop()
is_on = False
