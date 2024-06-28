import tkinter as tk
import subprocess
import socket

root = tk.Tk()

def startBVConnector():
    BVConnectorPath = "C:\Users\experimentPC310\Documents\LSL\BrainAmpSeries\BrainAmpSeries.exe"
    BVConnectorConfig = "C:\Users\experimentPC310\Documents\LSL\BrainAmpSeries\config_128ch_good.cfg"
    subprocess.Popen([BVConnectorPath, "-c", BVConnectorConfig])

def startLabRecorder():
    LabRecorderPath = "C:\Users\experimentPC310\Documents\LSL\LabRecorder\LabRecorder.exe"
    LabRecorderConfig = "C:\Users\experimentPC310\Documents\LSL\LabRecorder\config_abdallah.cfg"
    subprocess.Popen([LabRecorderPath, "-c", LabRecorderConfig])

def startBVViewer():
    BVViewerPath = "C:\Program Files\BrainVision LSL Viewer\Python\python.exe"
    subprocess.Popen(BVViewerPath, shell=True)