import tkinter as tk
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.Log import *
from Phidget22.LogLevel import *
from Phidget22.Devices.Stepper import *
import traceback
import time

from matplotlib.pyplot import text

class StepperWrapper : 
    """
    Wrapper class for Phidget22.Devices.Stepper
    """
    def __init__(self) :
        self._s = Stepper()
        self.currentPosition: int = 0
        self.isEngaged:bool = False
        self.stepsPerMm:float = float('inf')
        self.stepsPerDegree:float = float("inf")
    # def __del__(self):
    #     return super().__del__()
    # Status
    def current_position(self) -> float :
        if self._s.getAttached() == 1 :
            return self._s.getPosition()
        else :
            return float(0)
    def target_position(self) -> float:
        if self._s.getAttached() == 1:
            return self._s.getTargetPosition()
        else :
            return float(10)
    
    # Movement
    def move(self, numsteps:int):
        """
        Rotates the stepper's shaft by the specified number of steps.
        @numsteps can be positive, negative or zero, although the latter is rather pointless.
        """
        self.currentPosition += numsteps
        self._s.setTargetPosition(self.currentPosition)
        self._s.setEngaged(True)
    def move_mm(self, distance:float):
        """
        Moves an object connected to the stepper by the amount specified.
        Errors: 
            property "stepsPerMm" is unset, zero, float('nan'), or float('inf') (raises ValueError)
        """
        if self.stepsPerMm == float("inf") or self.stepsPerMm == 0 or self.stepsPerMm == float('nan') :
            raise ValueError("stepsPerMm needs to be defined and nonzero")
        self.move(round(self.stepsPerMm*distance))
    def move_deg(self, rotation:float):
        """
        Moves the shaft of the stepper by a specified number of degrees
        Errors: 
            property "stepsPerDegree" is unset, zero, float('nan'), or float('inf') (raises ValueError)
        """
        if self.stepsPerDegree == float("inf") or self.stepsPerDegree == 0 or self.stepsPerDegree == float('nan') :
            raise ValueError("stepsPerMm needs to be defined and nonzero")
        self.move(round(self.stepsPerDegree*rotation))
    # Device Lifetime
    def _defaultAttachHandler(self) :
        print(f"{1}, Attach",self.getDeviceSerialNumber)
    def _defaultDetachHandler(self) :
        print(f"{1}, Detach", self.getDeviceSerialNumber)
    def attach(self, att_handler= lambda: StepperWrapper._defaultAttachHandler, det_handler = lambda: StepperWrapper._defaultDetachHandler, timeout:int = 5000):
        self._s.setOnAttachHandler(att_handler)
        self._s.setOnDetachHandler(det_handler)
        self._s.openWaitForAttachment(timeout)
    def detach(self) :
        self._s.close()

class Winder:
    """
    Serves as an intermediary between the hardware (StepperWrapper) and the gui.
    """
    def __init__(self) -> None:
        self.axes: dict[StepperWrapper] = {
            "X" : StepperWrapper(),
            "Y" : StepperWrapper(),
            "A" : StepperWrapper(),
            "B" : StepperWrapper(),
        }
        self.shape: list[(float,float)] = list()
        self.isStopState: bool = False
        self.currentRatio: float = 0.0
    def nextState(self)->bool:
        xp = self.getposition("X")
        
        return True
    def getposition(self, axis: str)->float:
        return self.axes[axis].current_position()

def test():
    try:
        Log.enable(LogLevel.PHIDGET_LOG_INFO, "phidgetlog.log")
        #Create your Phidget channels
        Winder = StepperWrapper() # Winder
        Topslide = StepperWrapper() # Top slide
        stepper2 = StepperWrapper() 
        stepper3 = StepperWrapper()
        Winder.attach()
        Topslide.attach()
        stepper2.attach()
        stepper3.attach()
        while 1: 
            i = input("stepper ")
            if i == "0" :
                print("0")
                Winder.move(1E6)
            elif i == "1" :
                print("1")
                Topslide.move(1000)
            elif i == "2" :
                print("2")
                stepper2.move(1000)
            elif i == "3" :
                print("3")
                stepper3.move(1000)

    

    except PhidgetException as ex:
        #We will catch Phidget Exceptions here, and print the error informaiton.
        traceback.print_exc()
        print("")
        print("PhidgetException " + str(ex.code) + " (" + ex.description + "): " + ex.details)

def lctestfn(state: tk.DoubleVar, delta):
    c = state.get()
    state.set(c+delta)
    print(state.get())
    
class LiveControls(tk.LabelFrame):
    def __init__(self, parent, state: Winder):
        tk.LabelFrame.__init__(self,parent,text="Live Controls")
        #current axes positions
        sx = tk.DoubleVar(value=state.axes["X"].current_position())
        sy = tk.DoubleVar(value=state.axes["Y"].current_position())
        sa = tk.DoubleVar(value=state.axes["A"].current_position())
        sb = tk.DoubleVar(value=state.axes["B"].current_position())
        #target axes positions
        gx = tk.DoubleVar(value=state.axes["X"].target_position())
        gy = tk.DoubleVar(value=state.axes["Y"].target_position())
        ga = tk.DoubleVar(value=state.axes["A"].target_position())
        gb = tk.DoubleVar(value=state.axes["B"].target_position())
        
        x = tk.Button(self, text="+X",command=lambda:lctestfn(sx,1)).grid(row=0,column=0)
        xr = tk.Button(self, text="-X",command=lambda:lctestfn(sx,-1)).grid(row=2,column=0)
        xc = tk.Label(self, textvariable=sx).grid(row=1,column=0)
        xt = tk.Label(self, textvariable=gx).grid(row=1,column=0)
        
        y = tk.Button(self, text="+Y").grid(row=0,column=1)
        yr = tk.Button(self, text="-Y").grid(row=2,column=1)
        yc = tk.Label(self, textvariable=sy).grid(row=1,column=1)
        yt = tk.Label(self, textvariable=gy).grid(row=1,column=1)
                
        a = tk.Button(self, text="+A").grid(row=0,column=2)
        ar = tk.Button(self,text="-A").grid(row=2,column=2)
        ac = tk.Label(self, textvariable=sa).grid(row=1,column=2)
        at = tk.Label(self, textvariable=ga).grid(row=1,column=2)
                
        b = tk.Button(self, text="+B").grid(row=0,column=3)
        br = tk.Button(self, text="-B").grid(row=2,column=3)
        bc = tk.Label(self, textvariable=sb).grid(row=1,column=3)
        bt = tk.Label(self, textvariable=gb).grid(row=1,column=3)
        
        

#test()
def main() :
    root = tk.Tk()
    w = Winder()
    LC = LiveControls(root, w).grid(row=0,column=0)
    
    
    #root.mainloop()
    
    while 1:
        root.update()
main()