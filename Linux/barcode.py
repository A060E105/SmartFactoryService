import sys
import serial
import time
# import keyboard

# ser = serial.Serial('COM3', 115200, timeout=1)  # ttyACM1 for Arduino board
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # ttyACM1 for Arduino board


def show(data):
    print(f'read data is : {data}')

commandToSend = 'T\r\n'  # get the distance in mm
while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        
        # print("Writing: ",  commandToSend)
        # ser.write(str(commandToSend).encode())
        # time.sleep(1)
        print("Attempt to Read")
        readOut = ser.readline().decode('ascii')
        time.sleep(1)
        if not readOut == '':
            show(readOut)
        else:
            ser.flush()  # flush the buffer
            continue
        print("Reading: ", readOut)
        print("Restart")
        ser.flush()     # flush the buffer
    except KeyboardInterrupt:
        print("to be able to exit script gracefully")
        ser.close()
        sys.exit()

            
    
