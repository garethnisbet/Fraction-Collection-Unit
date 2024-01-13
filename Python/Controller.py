#Creality 3d printer controller
import serial
import numpy as np
from time import sleep


class Controller(object):
    """ Class for controling the Creality 3d printer over a USB serial connection """
    def __init__(self,port,baudrate):#
        self.port = port
        self.baudrate = baudrate
                                  
    def connect(self):
        self.s = serial.Serial(self.port,self.baudrate)
        
    def disconnect(self):
        self.s.close()
        
    def getPos(self):
        posstatus = self.s.write('M114\n'.encode())
        gotposition = 0
        while not gotposition:
            current_position = self.s.readline().decode().strip()
            if current_position == 'ok':
                gotposition = 0
            elif not current_position.find('busy') == -1:
                gotposition = 0
            else:
                gotposition = 1
        if gotposition:
            xval = float(current_position[current_position.find('X')+2:current_position.find('Y')-1])
            yval = float(current_position[current_position.find('Y')+2:current_position.find('Z')-1])
            zval = float(current_position[current_position.find('Z')+2:current_position.find('E')-1])
        else:
            xval = np.nan
            yval = np.nan
            zval = np.nan
        return xval, yval, zval

    def setPos(self,x_val,y_val,z_val,feedrate = 500):
        self.x_val = x_val
        self.y_val = y_val
        self.z_val = z_val
        gcode = 'G1X'+str(x_val)+'Y'+str(y_val)+'Z'+str(z_val)+'F'+str(feedrate)+'\n'
        self.s.write(gcode.encode())

    def sendGCODE(self,gcode):
        self.s.write(gcode.encode())
        sleep(0.1)

    def rmove(self, axis, step, direction,feedrate = 500):
        gcode = 'G91 \nG1'+axis+str(step*direction)+' F'+str(feedrate)+'\nG90\n'
        self.s.write(gcode.encode())
        
    def enable(self):
        gcode = 'M22 \nM21\n'
        self.s.write(gcode.encode())
        
    def home(self):
        self.s.write('G28\n'.encode())
        print('Homed')
        
    def stop(self):
        self.s.write('M410\n'.encode())
    
    def readline(self):
        return self.s.readline().decode().strip()
  

        


