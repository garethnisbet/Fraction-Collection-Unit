import numpy as np
class grid2gcode(object):
    """ create gcode from specified grid """
    def __init__(self,origin, shape, pitch, feedrate, depth, dwelltime):#
        self.origin = origin
        self.shape = shape
        self.pitch = pitch
        self.feedrate = feedrate
        self.depth = depth
        self.dwelltime = dwelltime
        self.orientation = 0
        self.xdata = []
        self.ydata = []

    def setOrientation(self, orientation):
        self.orientation = orientation
        
                                  
    def create(self):
        # Assuming pitch is +ve
        gcode = ['G1 X{:.2f} Y{:.2f} Z{:.2f} F{} \n'.format(self.origin[0],self.origin[1],self.origin[2],self.feedrate[0])]
        if self.orientation == 0:
            xstart = self.origin[0]
            xend = self.origin[0]+(self.pitch[0]*(self.shape[0]))
            xstep = self.pitch[0]
            self.xdata = list(np.arange(xstart,xend,xstep))
            
            ystart = self.origin[1]
            yend = self.origin[1]+(-self.pitch[1]*(self.shape[1]))
            ystep = -self.pitch[1]

            self.ydata = list(np.arange(ystart,yend,ystep))
            xdata = self.xdata

            for ii in list(range(len(self.ydata))):
                for iii in list(range(len(self.xdata))):
                    gcode += ['G1 X{:.2f} Y{:.2f} F{} \n'.format(xdata[iii],self.ydata[ii],self.feedrate[0])]
                    gcode += ['G1 Z{:.2f} F{} \n'.format(self.origin[2]+self.depth,self.feedrate[1])]
                    gcode += ['G4 S{:.2f} \n'.format(self.dwelltime)]
                    gcode += ['G1 Z{:.2f} F{} \n'.format(self.origin[2],self.feedrate[1])]
                xdata.reverse()
        elif self.orientation == 1:
            xstart = self.origin[0]
            xend = self.origin[0]+(-self.pitch[0]*(self.shape[1]))
            xstep = -self.pitch[0]
            self.xdata = list(np.arange(xstart,xend,xstep))
            
            ystart = self.origin[1]
            yend = self.origin[1]+(-self.pitch[1]*(self.shape[0]))
            ystep = -self.pitch[1]
            self.ydata = list(np.arange(ystart,yend,ystep))
            ydata = self.ydata

            for ii in list(range(len(self.xdata))):
                
                for iii in list(range(len(self.ydata))):
                    gcode += ['G1 X{:.2f} Y{:.2f} F{} \n'.format(self.xdata[ii],ydata[iii],self.feedrate[0])]
                    gcode += ['G1 Z{:.2f} F{} \n'.format(self.origin[2]+self.depth,self.feedrate[1])]
                    gcode += ['G4 S{:.2f} \n'.format(self.dwelltime)]
                    gcode += ['G1 Z{:.2f} F{} \n'.format(self.origin[2],self.feedrate[1])]
                ydata.reverse()
            
        return gcode
        


# origin, shape, pitch, feedrate, depth, dwelltime = [5,8,10], [12,8], [0.91, 0.91], [1000,500], -5, 1

# g2g = grid2gcode(origin, shape, pitch, feedrate, depth, dwelltime).create()
