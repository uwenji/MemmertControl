import io
import sys
import fcntl
import time
import copy
import string
import os
import csv
from AtlasI2C import (
     AtlasI2C
)

def print_devices(device_list, device):
    for i in device_list:
        if(i == device):
            print("--> " + i.get_device_info())
        else:
            print(" - " + i.get_device_info())
    #print("")
    
def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []
    
    for i in device_address_list:
        device.set_i2c_address(i)
        response = device.query("I")
        try:
            moduletype = response.split(",")[1] 
            response = device.query("name,?").split(",")[1]
        except IndexError:
            print(">> WARNING: device at I2C address " + str(i) + " has not been identified as an EZO device, and will not be queried") 
            continue
        device_list.append(AtlasI2C(address = i, moduletype = moduletype, name = response))
    return device_list 
def saveCSV(file_Path, Data):
    second = time.time()
    local_time =time.ctime(second)
    new_titles = [
        ["Time","Local Time","electronphoresis","reservoir","pH_level"],
        ]
    csv_file = file_Path
    
    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(new_titles)
    
    else:
        with open(csv_file, mode='a', newline='') as file:
            local_time = time.ctime(second)
            #ppm = read_USB()
            #o2_ppm = read_ser()
            new_data = []
            express = []
            express.append(str(second))
            express.append(local_time)
            for d in Data:
                express.append(d + "\n")
            #express.append(str(ppm) + "\n")
            #express.append(str(o2_ppm) + "\n")
            new_data.append(express)
            writer = csv.writer(file)
            writer.writerows(new_data)
            print(express)
        
def main():
    
    device_list = get_devices()
    #register atlas devices
    chamber01 = AtlasI2C() #electrophoresis
    chamber02 = AtlasI2C() #reservoir
    pH_sensor = AtlasI2C()
    pump1 = AtlasI2C()
    pump2 = AtlasI2C()
     #editting the case device & number 
    for dev in device_list:
        #print_devices(device_list,dev)
        name = dev.moduletype + "_" + str(dev.address)
        print(name)
        """    
        dev.write("R")
        time.sleep(2)
        responce = dev.read()
        print(responce)"""
        match name:
            case "RTD_68":
                chamber01 = dev
                print("electrophoresis check")
            case "RTD_69":
                chamber02 = dev
                print("reservoir check")
            case "pH_99":
                pH_sensor = dev
                print("PH sensor check")
            case "PMP_113":
                pump1 = dev
                print("Pump1 check")
            case "PMP_115":
                pump2 = dev
                print("Pump2 check")
    #reading sensor values
    data = []
    chamber01.write("R")
    time.sleep(2)
    chamber_value = "".join(chamber01.read().split(": ")[1].split('\x00'))
    data.append(chamber_value)
    print(chamber_value + " celsius")
    chamber02.write("R")
    time.sleep(2)
    reservoir_value = "".join(chamber02.read().split(": ")[1].split('\x00'))
    data.append(reservoir_value)
    print(reservoir_value + " celsius")
    
    pH_sensor.write("R")
    time.sleep(2)
    pH_level = "".join(pH_sensor.read().split(": ")[1].split('\x00'))
    data.append(pH_level)
    print(pH_level)

     #save csv file location
    saveCSV("/home/pi/Desktop/BiolabSensors/CSV/electronphoresis_data2.csv",data)
    #control pump
    if float(chamber_value) > 20.0 or float(pH_level) < 6 or float(pH_level) > 8:
        pump1.write("D,50")
        pump2.write("D,50")
        time.sleep(1.0)
        responce1 = pump1.read()
        responce2 = pump2.read()
        print(responce1 + "," + responce2)
        
if __name__ == '__main__':
    main()