#!/usr/bin/python
#----------------------------------------------------------------------#
                                               
         ########################################                                      
    #####################################################                               
    #####                                  ######################                       
     ###            ##                               ###############                    
     ####      ############                #########         #######                    
     ####    ################           ##############          ####                    
     ####   #####        #####         #######   #######        ####                    
     ####  #####          #####       #####         #####      ####                     
     ####  ####            ####      ####            ####      ####                     
     ####   ####           ####      ####            ####     ####                      
     ####    ######    ######         #####        #####      ####                      
     ####     ##############           ################      #####                      
     ####       ##########               ############        ####                       
     ####                                    ####            ####                       
     #####################                                   ####                       
      #####################                 ############### ####                        
                       ####                 ####################                        
                       ###                   ###                                        
                       ###                     ###   ##########                         
          #########    ###                     ###   #####  ####                        
          ##########   ###                      ###   ####  ####                        
          ##########   ###                      ####  #####  ####                       
          ####  ####   ###                       ##########  ####                       
          ####  ####   ###    KLiK Robotics      ########     ####                      
          ####  ##########                                     ####                     
          ####  +########+                        ###########  #####                    
          ####                                    ###########   #####                   
          ####   ########                          ####   ####   #####                  
          ####  ##########                          ####   ###    ####                  
         ####   ##########                ##############   ### ########                 
         ####   #### ###################################    ############                 
         ####   ####          ###############               ############                
         ####   ####                                                                    
         ###########                                                                    
         
#        GUI interface for fraction collection controller 

#------------------------ Import Libraries ----------------------------#
import json
import shutil
import pygame, sys, pygame.mixer, os
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(path_above)
import pygame.locals as pgl
from time import sleep, time
import pgt
import numpy as np
from Controller import Controller
from grid2gcode import grid2gcode

dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'

#-----------------------------------------------------------------------
#        Setup TTL for Raspberry PI 
#        Make sure a potential divider has been used
#        to step TTL 5V down to 3.3V otherwise you could 
#        damage the Raspberry PI!
#-----------------------------------------------------------------------
import RPi.GPIO as GPIO
PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)
TTL = 0
def TTLEventHandler(pin):
    global TTL
    TTL = 1
GPIO.add_event_detect(PIN,GPIO.RISING,callback=TTLEventHandler)
#-----------------------------------------------------------------------

def loadjson(filename):
    with open(filename,'r') as openfile:
        config = json.load(openfile)
    return json.loads(config)
    
    
def getGUI_events():
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
            print('Connection Closed')
            

config = loadjson('config.json')
stopmotion = 0

pitch1 = config["Pitch1"][0]
depth1 = config["Depth1"]
dwelltime1 = config["DwellTime1"]
dwelltime1I = config["DwellTime1I"]
feedrate1 = config["F1"][0]

pitch2 = config["Pitch2"][0]
depth2 = config["Depth2"]
dwelltime2 = config["DwellTime2"]
dwelltime2I = config["DwellTime2I"]
feedrate2 = config["F2"][0]
startwell = config["startwell"]
numwells = config["numwells"]
iterations = config["iterations"]
DwellTime1I = config['DwellTime1I']


try:
    pctrl = Controller('/dev/ttyUSB1',115200)
    sleep(2)
    pctrl.connect()
except:
    try:
        pctrl = Controller('/dev/ttyUSB0',115200)
        sleep(2)
        pctrl.connect()
    except:
        pctrl = Controller('/dev/ttyUSB3',115200)
        sleep(2)
        pctrl.connect()

#-----------------------------------------------------------------------
#   Function to check if input xy coordinate occur on a round image
#-----------------------------------------------------------------------
def in_cregion(xy,origin,radius):
    origin = np.array(origin)
    xy = np.array(xy)
    v = xy-origin
    if (v[0]**2+v[1]**2) <=  radius**2:
        state = 1
    else:
        state = 0
    return state

#-----------------------------------------------------------------------
#  Function to check if input xy coordinate occur on a rectangular image
#-----------------------------------------------------------------------
def in_rregion(xy,origin,dim):
    origin = np.array(origin)
    xy = np.array(xy)
    dim = np.array(dim)
    
    if xy[0]>=origin[0] and xy[0]<=origin[0]+dim[0] and xy[1]>=origin[1] and xy[1]<=origin[1]+dim[1]:
        state = 1
    else:
        state = 0
    return state
    
homed_condition_1 = 0
Page = 1

#-------------- Define some colors for displayed text ------------------

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')
RED = pygame.Color('red')
pygame.init()

#------- Set the width and height of the screen (width, height) -------#
#screen = pygame.display.set_mode((800, 480))
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)

#--------------------   Load Artwork  ---------------------------------#

bg = pygame.image.load(dirpath+'/BG.png')
bg2 = pygame.image.load(dirpath+'/BG2.png')
bg3 = pygame.image.load(dirpath+'/BG3.png')
bg4 = pygame.image.load(dirpath+'/BG4.png')
bg5 = pygame.image.load(dirpath+'/BG5.png')
go = pygame.image.load(dirpath+'/Go.png')
Larrow = pygame.image.load(dirpath+'/LeftArrow.png')
Rarrow = pygame.image.load(dirpath+'/RightArrow.png')
Darrow = pygame.image.load(dirpath+'/DownArrow.png')
Uarrow = pygame.image.load(dirpath+'/UpArrow.png')
Stop = pygame.image.load(dirpath+'/Stop.png')
Pause = pygame.image.load(dirpath+'/Pause.png')
Home = pygame.image.load(dirpath+'/Home.png')
Zero = pygame.image.load(dirpath+'/Zero.png')
BLsquare = pygame.image.load(dirpath+'/BLSquare.png')
TRsquare = pygame.image.load(dirpath+'/TRSquare.png')
TLsquare = pygame.image.load(dirpath+'/TLSquare.png')
Play = pygame.image.load(dirpath+'/PlaySquare.png')
Blank = pygame.image.load(dirpath+'/Blank.png')
Zero = pygame.image.load(dirpath+'/Zero.png')
Settings = pygame.image.load(dirpath+'/Settings.png')
SaveP1 = pygame.image.load(dirpath+'/SaveP1.png')
SaveP2 = pygame.image.load(dirpath+'/SaveP1.png')
Trigger = pygame.image.load(dirpath+'/Trigger.png')
ProgExit = pygame.image.load(dirpath+'/ProgExit.png')
WellType1 = pygame.image.load(dirpath+'/WellType1.png')
WellType2 = pygame.image.load(dirpath+'/WellType2.png')
Return = pygame.image.load(dirpath+'/Return.png')
MotorEnable = pygame.image.load(dirpath+'/MotorEnable.png')
MinusBlue = pygame.image.load(dirpath+'/Minus.png')
PlusBlue = pygame.image.load(dirpath+'/Plus.png')
FactoryReset = pygame.image.load(dirpath+'/FactoryReset.png')
Plan = pygame.image.load(dirpath+'/Plan.png')
pygame.display.set_caption("Fraction Collection Unit")

#---------- Loop until the user clicks the close button ---------------#
done = False

#---------- Used to manage how fast the screen updates  ---------------#

clock = pygame.time.Clock()

#------------------ Initialize the joysticks  -------------------------#

pygame.joystick.init()

#-----------------------  Print to Window -----------------------------#

textPrint = pgt.TextPrint(WHITE)
welltypeset = 1

# ---------------------- Main Program Loop ----------------------------#
clock = pygame.time.Clock()
clock.tick(30)
last = pygame.time.get_ticks()

while not done:
    try:
        xyz = pctrl.getPos()
        homed_condition_2 = 1
    except:
        xyz = 'NA, NA, NA'
        homed_condition_2 = 0
    
        
    if Page == 1:
        screen.blit(bg, [0, 0])
    elif Page == 2:
        screen.blit(bg2, [0, 0])
    if welltypeset == 1:
        screen.blit(WellType1, [17,269])
    elif welltypeset == 2:
        screen.blit(WellType2, [17,269])
        
    getGUI_events()

    textPrint.reset()   
    keys = pygame.key.get_pressed()

    if keys[pgl.K_q]:
        try:
           pctrl.disconnect()
        except:
            pass
        pygame.quit()
        sys.exit()       
           
    #------------------------------------------------------------------#
    #                      Get Mouse Position
    #------------------------------------------------------------------#                   
    mx,my = pygame.mouse.get_pos()
    c1, c2, c3 =  pygame.mouse.get_pressed()
    
    #------------------------------------------------------------------#
    #                Set coordinated for buttons
    #------------------------------------------------------------------#
    
    xminus = [269+26,212+26]
    xplus = [486+26,212+26]
    yplus = [378+26,103+26]
    yminus = [378+26,320+26]
    zplus = [681+26,103+26]
    zminus = [681+26,320+26]
    stop = [355+49, 189+49]
    stop_p3 = [226+49, 191+49]
    pause_p3 = [476+49, 191+49]
    play = [489,322]
    tlsquare = [249,74]
    trsquare = [508,74]
    blsquare = [249,324]
    blank = [15,222]
    home = [49,42]
    zero = [658+49,191+49]
    save = [230,322]
    settings = [489,72]
    trigger = [230,72]
    savep1 = [230,322]
    savep2 = [673,355]
    factoryreset = [673,227]
    progexit = [755,14]
    welltype = [17,269]
    _return = [10,10]
    plan = [673,99]
    
    pitchm = [239+34,30+34]
    pitchp = [521+34,30+34]
    depthm = [239+34,118+34]
    depthp = [521+34,118+34]
    dwelltimem = [239+34,206+34]
    dwelltimep = [521+34,206+34]
    dwelltimemI = [239+34,294+34]
    dwelltimepI = [521+34,294+34]
    feedratem = [239+34,382+34]
    feedratep = [521+34,382+34]

    startwellm = [239+34,118+34]
    startwellp = [521+34,118+34]
    
    numwellsm = [239+34,206+34]
    numwellsp = [521+34,206+34]
    
    iterationsm = [239+34,294+34]
    iterationsp = [521+34,294+34]
    
    dwelltimeSweepBackm = [239+34,382+34]
    dwelltimeSweepBackp = [521+34,382+34]
    
    #------------------------------------------------------------------#
    #             Check for mouse click on buttons
    #------------------------------------------------------------------#
    
    if in_cregion([mx,my],[xplus[0],xplus[1]],26) and c1 and Page == 1:
        screen.blit(Rarrow, [xplus[0]-52,xplus[1]-39])
        pctrl.rmove('X',0.4,1)
        
               
    if in_cregion([mx,my],[xminus[0],xminus[1]],26) and c1 and Page == 1:
        screen.blit(Larrow, [xminus[0]-65,xminus[1]-39])
        pctrl.rmove('X',0.4,-1)    

    if in_cregion([mx,my],[yplus[0],yplus[1]],26) and c1 and Page == 1:
        screen.blit(Uarrow, [yplus[0]-39,yplus[1]-64])
        pctrl.rmove('Y',0.4,1) 
               
    if in_cregion([mx,my],[yminus[0],yminus[1]],26) and c1 and Page == 1:
        screen.blit(Darrow, [yminus[0]-39,yminus[1]-52])
        pctrl.rmove('Y',0.4,-1)  

    if in_cregion([mx,my],[zplus[0],zplus[1]],26) and c1 and Page == 1:
        screen.blit(Uarrow, [zplus[0]-38,zplus[1]-66])
        pctrl.rmove('Z',0.5,1)
               
    if in_cregion([mx,my],[zminus[0],zminus[1]],26) and c1 and Page == 1:
        screen.blit(Darrow, [zminus[0]-39,zminus[1]-52])
        pctrl.rmove('Z',0.5,-1)     

    if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
        screen.blit(Stop, [stop[0]-49,stop[1]-49])
        pctrl.stop()

    if in_cregion([mx,my],[zero[0],zero[1]],49) and c1 and Page == 1:
        screen.blit(Zero, [zero[0]-49,zero[1]-49])
        if welltypeset == 1:

            pctrl.setPos(config['X1'],config['Y1'],config['Z1'],config['F1'])
        elif welltypeset == 2:
            pctrl.setPos(config['X2'],config['Y2'],config['Z2'],config['F2'])
            

    #-------------------------------------------------------------------
    #                     Play grid loop using trigger
    #-------------------------------------------------------------------
    
    if in_rregion([mx,my],[trigger[0],trigger[1]],[88, 88]) and c1 and Page == 1:
        screen.blit(Trigger, [trigger[0],trigger[1]])
        #---------------------------------------------------------------
        #          GPIO event loop checking for TTL
        #---------------------------------------------------------------
        starttime = time()
        while TTL == 0:
            if welltypeset == 1:
                screen.blit(bg3, [0,0])
            elif welltypeset == 2:
                screen.blit(bg4, [0,0])
            textPrint.setfontsize(30)  
            lapsedtime = time()-starttime
            textPrint.abspos(screen, 'Waiting for trigger: Lapsed Time {:.2f} s'.format(lapsedtime),(220,20))

            for event in pygame.event.get(): # User did something.
                if event.type == pygame.QUIT: # If user clicked close.
                    done = True # Flag that we are done so we exit this loop.
            mx,my = pygame.mouse.get_pos()
            c1, c2, c3 =  pygame.mouse.get_pressed()
            if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
                screen.blit(Stop, [stop[0]-49,stop[1]-49])
                stopmotion = 1
            if stopmotion:
                stopmotion = 0
                break
            pygame.display.flip()
            
            #-----------------------------------------------------------

        if welltypeset == 1 and TTL:
            config = loadjson('config.json')
            g2g = grid2gcode([config['X1'],config['Y1'],config['Z1']], config['Shape1'], config['Pitch1'], config['F1'], config['Depth1'], config['DwellTime1'])
            g2g.orientation = 0
            gcode = g2g.create()

            # with open('GcodeCheck.txt', 'w') as fp:
                # fp.write(''.join(gcode))
            # fp.close()
            
            # for ii in list(range(len(gcode))):
            for iii in list(range(iterations)):

                zsafe = 'G1 Z{:.2f} F{} \n'.format(config['Z1'],config['F1'][1])
                pctrl.sendGCODE(zsafe)
                
                if iii > 0:
                    dwellstring = 'G4 S{:.2f} \n'.format(config['DwellTime1I'])
                    pctrl.sendGCODE(dwellstring)
                    
                
                for ii in list(range((startwell-1)*4,(startwell-1)*4+(4*(numwells)),1)):

                    #keep display interactive
                    screen.blit(bg3, [0,0])
                    
                    getGUI_events()

                    mx,my = pygame.mouse.get_pos()
                    c1, c2, c3 =  pygame.mouse.get_pressed()

                    if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
                        screen.blit(Stop, [stop[0]-49,stop[1]-49])
                        stopmotion = 1
                    
                    
                    if stopmotion != 1:
                        pctrl.sendGCODE(gcode[ii])
                        sleep(0.1)
                        xyz = pctrl.getPos()      
                        while pctrl.readline() != 'ok':
                            sleep(0.1)
                    else:
                        stopmotion = 0
                        TTL = 0
                        break

                    pygame.display.flip()
                    
            pctrl.sendGCODE(zsafe)
            TTL = 0





        elif welltypeset == 2 and TTL:
            
            config = loadjson('config.json')
            g2g = grid2gcode([config['X2'],config['Y2'],config['Z2']], config['Shape2'], config['Pitch2'], config['F2'], config['Depth2'], config['DwellTime2'])
            g2g.orientation = 1
            gcode = g2g.create()


            for iii in list(range(iterations)):

                zsafe = 'G1 Z{:.2f} F{} \n'.format(config['Z2'],config['F2'][1])
                pctrl.sendGCODE(zsafe)
                
                if iii > 0:
                    dwellstring = 'G4 S{:.2f} \n'.format(config['DwellTime1I'])
                    pctrl.sendGCODE(dwellstring)
                
                for ii in list(range((startwell-1)*4,(startwell-1)*4+(4*(numwells)),1)):

                    #keep display interactive
                    screen.blit(bg3, [0,0])
                    
                    getGUI_events()

                    
                    mx,my = pygame.mouse.get_pos()
                    c1, c2, c3 =  pygame.mouse.get_pressed()

                    
                    if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
                        screen.blit(Stop, [stop[0]-49,stop[1]-49])
                        stopmotion = 1
                    
                    
                    if stopmotion != 1:
                        pctrl.sendGCODE(gcode[ii])
                        sleep(0.1)
                        xyz = pctrl.getPos()         
                        while pctrl.readline() != 'ok':
                            sleep(0.1)
                    else:
                        stopmotion = 0
                        break

                    pygame.display.flip()
                    
            pctrl.sendGCODE(zsafe)
            TTL = 0


    #-------------------------------------------------------------------
    #                     Play grid loop
    #-------------------------------------------------------------------
    
    if in_rregion([mx,my],[play[0],play[1]],[87, 87]) and c1 and Page == 1:
        screen.blit(Play, [play[0],play[1]])

        
        if welltypeset == 1:
            config = loadjson('config.json')
            g2g = grid2gcode([config['X1'],config['Y1'],config['Z1']], config['Shape1'], config['Pitch1'], config['F1'], config['Depth1'], config['DwellTime1'])
            g2g.orientation = 0
            gcode = g2g.create()

            # with open('GcodeCheck.txt', 'w') as fp:
                # fp.write(''.join(gcode))
            # fp.close()
            
            # for ii in list(range(len(gcode))):
            for iii in list(range(iterations)):

                zsafe = 'G1 Z{:.2f} F{} \n'.format(config['Z1'],config['F1'][1])
                pctrl.sendGCODE(zsafe)
                
                if iii > 0:
                    dwellstring = 'G4 S{:.2f} \n'.format(config['DwellTime1I'])
                    pctrl.sendGCODE(dwellstring)
                    
                
                for ii in list(range((startwell-1)*4,(startwell-1)*4+(4*(numwells)),1)):

                    #keep display interactive
                    screen.blit(bg3, [0,0])
                    
                    getGUI_events()

                    mx,my = pygame.mouse.get_pos()
                    c1, c2, c3 =  pygame.mouse.get_pressed()

                    if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
                        screen.blit(Stop, [stop[0]-49,stop[1]-49])
                        stopmotion = 1
                    
                    
                    if stopmotion != 1:
                        pctrl.sendGCODE(gcode[ii])
                        sleep(0.1)
                        xyz = pctrl.getPos()      
                        while pctrl.readline() != 'ok':
                            sleep(0.1)
                    else:
                        stopmotion = 0
                        break

                    pygame.display.flip()
                    
            pctrl.sendGCODE(zsafe)

        elif welltypeset == 2:

            config = loadjson('config.json')
            g2g = grid2gcode([config['X2'],config['Y2'],config['Z2']], config['Shape2'], config['Pitch2'], config['F2'], config['Depth2'], config['DwellTime2'])
            g2g.orientation = 1
            gcode = g2g.create()


            for iii in list(range(iterations)):

                zsafe = 'G1 Z{:.2f} F{} \n'.format(config['Z2'],config['F2'][1])
                pctrl.sendGCODE(zsafe)
                
                if iii > 0:
                    dwellstring = 'G4 S{:.2f} \n'.format(config['DwellTime1I'])
                    pctrl.sendGCODE(dwellstring)
                
                for ii in list(range((startwell-1)*4,(startwell-1)*4+(4*(numwells)),1)):

                    #keep display interactive
                    screen.blit(bg3, [0,0])
                    
                    getGUI_events()

                    
                    mx,my = pygame.mouse.get_pos()
                    c1, c2, c3 =  pygame.mouse.get_pressed()

                    
                    if in_cregion([mx,my],[stop[0],stop[1]],49) and c1 and Page == 1:
                        screen.blit(Stop, [stop[0]-49,stop[1]-49])
                        stopmotion = 1
                    
                    
                    if stopmotion != 1:
                        pctrl.sendGCODE(gcode[ii])
                        sleep(0.1)
                        xyz = pctrl.getPos()         
                        while pctrl.readline() != 'ok':
                            sleep(0.1)
                    else:
                        stopmotion = 0
                        break

                    pygame.display.flip()
                    
            pctrl.sendGCODE(zsafe)
                
        
    if in_rregion([mx,my],[savep1[0],savep1[1]],[88, 88]) and c1 and Page == 1:
        screen.blit(SaveP1, [savep1[0],savep1[1]])
        if welltypeset == 1:

            config['X1']=xyz[0]
            config['Y1']=xyz[1]
            config['Z1']=xyz[2]
            config = json.dumps(config)           
            with open("config.json", "w") as outfile:
                json.dump(config, outfile)
            sleep(0.5)
            config = json.loads(config)

        elif welltypeset == 2:
            config['X2']=xyz[0]
            config['Y2']=xyz[1]
            config['Z2']=xyz[2]
            config = json.dumps(config)           
            with open("config.json", "w") as outfile:
                json.dump(config, outfile)
            sleep(0.5)
            config = json.loads(config)


    # Save settings from configuration page
    if in_rregion([mx,my],[savep2[0],savep2[1]],[88, 88]) and c1 and Page == 2:
        screen.blit(SaveP2, [savep2[0],savep2[1]])
        if welltypeset==1:
            config['Pitch1']=[pitch1, pitch1]
            config['Depth1']=depth1
            config['DwellTime1']=dwelltime1
            config['DwellTime1I']=dwelltime1I
            config['F1']=[feedrate1,feedrate1,feedrate1]
        elif welltypeset==2:
            config['Pitch2']=[pitch2,pitch2]
            config['Depth2']=depth2
            config['DwellTime2']=dwelltime2
            config['DwellTime2I']=dwelltime2I
            config['F2']=[feedrate2,feedrate2,feedrate2]
            
        config = json.dumps(config)
        with open("config.json", "w") as outfile:
            json.dump(config, outfile)
            sleep(0.5)
            config = json.loads(config)
            
            
    # Save settings from planning page
    if in_rregion([mx,my],[savep2[0],savep2[1]],[88, 88]) and c1 and Page == 3:
        screen.blit(SaveP2, [savep2[0],savep2[1]])
        config['startwell']=startwell
        config['numwells']=numwells
        config['iterations']=iterations
           
        config = json.dumps(config)
        with open("config.json", "w") as outfile:
            json.dump(config, outfile)
            sleep(0.5)
            config = json.loads(config)

    if in_rregion([mx,my],[factoryreset[0],factoryreset[1]],[88, 88]) and c1 and Page == 2:
        screen.blit(FactoryReset, [factoryreset[0],factoryreset[1]])
        shutil.copyfile('config_backup.json', 'config.json')
        config = loadjson('config.json')

        pitch1 = config["Pitch1"][0]
        depth1 = config["Depth1"]
        dwelltime1 = config["DwellTime1"]
        dwelltime1I = config["DwellTime1I"]
        feedrate1 = config["F1"][0]

        pitch2 = config["Pitch2"][0]
        depth2 = config["Depth2"]
        dwelltime2 = config["DwellTime2"]
        dwelltime2I = config["DwellTime2I"]
        feedrate2 = config["F2"][0]

    # Configuration Buttons Page 2
    if Page ==2:
        textPrint.setfontsize(22)
        textPrint.abspos(screen, 'Pitch',(pitchm[0]+65,pitchm[1]-45))
        textPrint.abspos(screen, 'Depth',(depthm[0]+65,depthm[1]-45))
        textPrint.abspos(screen, 'Dwell Time',(dwelltimem[0]+65,dwelltimem[1]-45))
        textPrint.abspos(screen, 'Dwell Time (Sweep)',(dwelltimemI[0]+65,dwelltimemI[1]-45))
        textPrint.abspos(screen, 'Speed',(feedratem[0]+65,feedratem[1]-45))

    
    if welltypeset==1:
        #pitch1
        if in_cregion([mx,my],[pitchm[0],pitchm[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [pitchm[0]-34,pitchm[1]-34])
            if pitch1 >= 0.2:
                pitch1 -= 0.1
        
        if in_cregion([mx,my],[pitchp[0],pitchp[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [pitchp[0]-34,pitchp[1]-34])
            pitch1 += 0.1
        
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(pitch1),(pitchm[0]+65,pitchm[1]-13))
    
        #depth1
        if in_cregion([mx,my],[depthm[0],depthm[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [depthm[0]-34,depthm[1]-34])
            depth1 -= 0.1
            
        if in_cregion([mx,my],[depthp[0],depthp[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [depthp[0]-34,depthp[1]-34])
            depth1 += 0.1
            
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(depth1),(depthm[0]+65,depthm[1]-13))

        #dwelltime1
        if in_cregion([mx,my],[dwelltimem[0],dwelltimem[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [dwelltimem[0]-34,dwelltimem[1]-34])
            if dwelltime1 >= 0.1:
                dwelltime1 -= 0.1
            else:
                dwelltime1 = 0
                
        if in_cregion([mx,my],[dwelltimep[0],dwelltimep[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [dwelltimep[0]-34,dwelltimep[1]-34])
            dwelltime1 += 0.1
            
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(dwelltime1),(dwelltimem[0]+65,dwelltimem[1]-13))        


        #dwelltime Initial Point
        if in_cregion([mx,my],[dwelltimemI[0],dwelltimemI[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [dwelltimemI[0]-34,dwelltimemI[1]-34])
            if dwelltime1I >= 0.1:
                dwelltime1I -= 0.1
            else:
                dwelltime1I = 0
                
        if in_cregion([mx,my],[dwelltimepI[0],dwelltimepI[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [dwelltimepI[0]-34,dwelltimepI[1]-34])
            dwelltime1I += 0.1
            
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(dwelltime1I),(dwelltimemI[0]+65,dwelltimemI[1]-13))
        
        #feedrate1
        if in_cregion([mx,my],[feedratem[0],feedratem[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [feedratem[0]-34,feedratem[1]-34])
            if feedrate1 >= 20:
                feedrate1 -= 10
        
        if in_cregion([mx,my],[feedratep[0],feedratep[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [feedratep[0]-34,feedratep[1]-34])
            if feedrate1 < 6000:
                feedrate1 += 10
        
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(feedrate1),(feedratem[0]+65,feedratem[1]-13))
            

    # Configuration Buttons Page 2
    elif welltypeset==2:
        #pitch2
        if in_cregion([mx,my],[pitchm[0],pitchm[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [pitchm[0]-34,pitchm[1]-34])
            if pitch2 >= 0.1:
                pitch2 -= 0.1
        
        if in_cregion([mx,my],[pitchp[0],pitchp[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [pitchp[0]-34,pitchp[1]-34])
            pitch2 += 0.1
        
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(pitch2),(pitchm[0]+65,pitchm[1]-13))
    
        #depth2
        if in_cregion([mx,my],[depthm[0],depthm[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [depthm[0]-34,depthm[1]-34])
            depth2 -= 0.1
        
        if in_cregion([mx,my],[depthp[0],depthp[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [depthp[0]-34,depthp[1]-34])
            depth2 += 0.1
        
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(depth2),(depthm[0]+65,depthm[1]-13))

        #dwelltime2
        if in_cregion([mx,my],[dwelltimem[0],dwelltimem[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [dwelltimem[0]-34,dwelltimem[1]-34])
            if dwelltime2 >= 0.1:
                dwelltime2 -= 0.1
            else:
                dwelltime2 = 0
                
        if in_cregion([mx,my],[dwelltimep[0],dwelltimep[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [dwelltimep[0]-34,dwelltimep[1]-34])
            dwelltime2 += 0.1
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(dwelltime2),(dwelltimem[0]+65,dwelltimem[1]-13))
            
            
        #dwelltime Initial Point
        if in_cregion([mx,my],[dwelltimemI[0],dwelltimemI[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [dwelltimemI[0]-34,dwelltimemI[1]-34])
            if dwelltime1I >= 0.1:
                dwelltime1I -= 0.1
            else:
                dwelltime1I = 0
                
        if in_cregion([mx,my],[dwelltimepI[0],dwelltimepI[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [dwelltimepI[0]-34,dwelltimepI[1]-34])
            dwelltime1I += 0.1
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(dwelltime1I),(dwelltimemI[0]+65,dwelltimemI[1]-13))
            
        #feedrate2
        if in_cregion([mx,my],[feedratem[0],feedratem[1]],34) and c1 and Page == 2:
            screen.blit(MinusBlue, [feedratem[0]-34,feedratem[1]-34])
            if feedrate2 >= 20:
                feedrate2 -= 10
        
        if in_cregion([mx,my],[feedratep[0],feedratep[1]],34) and c1 and Page == 2:
            screen.blit(PlusBlue, [feedratep[0]-34,feedratep[1]-34])
            if feedrate2 < 6000:
                feedrate2 += 10
        
        if Page == 2:
            textPrint.setfontsize(40)  
            textPrint.abspos(screen, '{:.2f}'.format(feedrate2),(feedratem[0]+65,feedratem[1]-13))


        
    if in_rregion([mx,my],[settings[0],settings[1]],[88, 88]) and c1 and Page == 1:
        screen.blit(Settings, [settings[0],settings[1]])
        Page = 2
        
    if in_rregion([mx,my],[_return[0],_return[1]],[38, 38]) and c1 and Page == 2:
        screen.blit(Return, [_return[0],_return[1]])
        Page = 1

    
    if in_rregion([mx,my],[plan[0],plan[1]],[88, 88]) and c1 and Page == 2:
        screen.blit(Plan, [plan[0],plan[1]])
        Page = 3


    if in_rregion([mx,my],[welltype[0],welltype[1]],[166, 166]) and c1:
        
        if welltypeset == 1:
            now = pygame.time.get_ticks()
            if now - last >= 300:
                screen.blit(WellType2, [welltype[0],welltype[1]])
                welltypeset = 2
                last = now
            

        elif welltypeset == 2:
            now = pygame.time.get_ticks()
            if now - last >= 300:
                screen.blit(WellType1, [welltype[0],welltype[1]])
                welltypeset = 1
                last = now


    if in_rregion([mx,my],[progexit[0],progexit[1]],[28, 28]) and c1:
        screen.blit(ProgExit, [progexit[0],progexit[1]])
        try:
           pctrl.disconnect()
        except:
            pass
        pygame.quit()
        sys.exit()
        
        
        
    if in_rregion([mx,my],[home[0],home[1]],[102, 98]) and c1  and Page == 1:
        screen.blit(Home, [home[0],home[1]])
        now = pygame.time.get_ticks()
        if now - last >= 300:
            pctrl.home()
            last = now
            homed_condition_1 = 1
    if homed_condition_1 and homed_condition_2 and Page == 1:
        screen.blit(Home, [home[0],home[1]])
        

    textPrint.setColour(WHITE)
    textPrint.setfontsize(25)   
    textPrint.abspos(screen, str(xyz),(24,180))
    textPrint.setColour(WHITE)
    textPrint.setfontsize(15)
    
        # Configuration Buttons Page 3
    
    if Page == 3:
        screen.blit(bg5, [0,0])
        textPrint.setfontsize(22)
        textPrint.abspos(screen, 'Starting Well',(startwellm[0]+65,startwellm[1]-45))
        textPrint.abspos(screen, 'Number of Wells',(numwellsm[0]+65,numwellsm[1]-45))
        textPrint.abspos(screen, 'Number of Iterations',(iterationsm[0]+65,iterationsm[1]-45))
        
        #---------------------------------------------------------------
        #                    Startwell
        #---------------------------------------------------------------
        if in_cregion([mx,my],[startwellm[0],startwellm[1]],34) and c1 and Page == 3:
            screen.blit(MinusBlue, [startwellm[0]-34,startwellm[1]-34])
            if startwell >= 2:
                startwell -= 1
        
        if in_cregion([mx,my],[startwellp[0],startwellp[1]],34) and c1 and Page == 3:
            screen.blit(PlusBlue, [startwellp[0]-34,startwellp[1]-34])
            startwell += 1
            
        textPrint.setfontsize(40)  
        textPrint.abspos(screen, '{:d}'.format(startwell),(startwellm[0]+65,startwellm[1]-13))
        
        #---------------------------------------------------------------
        #                    Number of wells
        #---------------------------------------------------------------
        if in_cregion([mx,my],[numwellsm[0],numwellsm[1]],34) and c1 and Page == 3:
            screen.blit(MinusBlue, [numwellsm[0]-34,numwellsm[1]-34])
            if numwells >= 2:
                numwells -= 1
        
        if in_cregion([mx,my],[numwellsp[0],numwellsp[1]],34) and c1 and Page == 3:
            screen.blit(PlusBlue, [numwellsp[0]-34,numwellsp[1]-34])
            numwells += 1
            
        textPrint.setfontsize(40)  
        textPrint.abspos(screen, '{:d}'.format(numwells),(numwellsm[0]+65,numwellsm[1]-13))

        #---------------------------------------------------------------
        #                    Number of iterations
        #---------------------------------------------------------------
        if in_cregion([mx,my],[iterationsm[0],iterationsm[1]],34) and c1 and Page == 3:
            screen.blit(MinusBlue, [iterationsm[0]-34,iterationsm[1]-34])
            if iterations >= 2:
                iterations -= 1
        
        if in_cregion([mx,my],[iterationsp[0],iterationsp[1]],34) and c1 and Page == 3:
            screen.blit(PlusBlue, [iterationsp[0]-34,iterationsp[1]-34])
            iterations += 1
            
        textPrint.setfontsize(40)  
        textPrint.abspos(screen, '{:d}'.format(iterations),(iterationsm[0]+65,iterationsm[1]-13))
        
            
        if in_rregion([mx,my],[_return[0],_return[1]],[38, 38]) and c1 and Page == 3:
            screen.blit(Return, [_return[0],_return[1]])
            Page = 2

    
#-----------------------   Send data to T-Bot   -----------------------#
        
    pygame.display.flip()
    # Limit to 20 frames per second.
    clock.tick(20)
    
# Close the window and quit.

pygame.quit()
