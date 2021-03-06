" short take off and landing aircraft model "
from numpy import pi
from gpkit import Variable, Model
from takeoff import TakeOff
from flightstate import FlightState

# pylint: disable=too-many-locals, invalid-name, unused-variable
class testAircraft(Model):
    def setup(self):
        W             = Variable("W", 2540, "lbf", "aircraft weight")
        S             = Variable("S", 55.17,"ft**2", "wing planform area")
        CL_max        = Variable("C_{L_{max, land}}", 2.5,"-", "Landing CL_max")
        Pshaftmax     = Variable("P_{shaft-max}", 200., "hp", "Maximum shaft power")
        AR            = Variable("AR", 10, "-", "Aspect ratio")
        e             = Variable("e", 1, "-", "Span efficiency")
        

        return []

class HelioCourier(Model):
    def setup(self):
        W           = Variable("W", 3400, "lbf", "aircraft weight")
        S           = Variable("S", 220,"ft**2", "wing planform area")
        CL_max      = Variable("C_{L_{max, land}}", 3.5,"-", "Landing CL_max")
        Pshaftmax   = Variable("P_{shaft-max}", 350., "hp", "Maximum shaft power")
        return []

class simpleAircraft(Model):
    " thing that we want to build "
    def setup(self):
        W           = Variable("W", "lbf", "aircraft weight")
        Wpay        = Variable("W_{pay}", 500, "lbf", "payload weight")
        hbatt       = Variable("h_{batt}", 210, "W*hr/kg", "battery specific energy")
        etae        = Variable("\\eta_{e}", 0.9, "-", "total electrical efficiency")
        Wbatt       = Variable("W_{batt}", "lbf", "battery weight")
        AR          = Variable("AR", 10, "-", "wing aspect ratio")
        S           = Variable("S", "ft**2", "wing planform area")
        WS          = Variable("(W/S)", 2.5, "lbf/ft**2",
                      "wing weight scaling factor")
        Wwing       = Variable("W_{wing}", "lbf", "wing weight")
        Pshaftmax   = Variable("P_{shaft-max}", "W", "max shaft power")
        #PW = Variable("(P/W)", 0.2, "hp/lbf", "power to weight ratio")
        sp_motor 	= Variable("sp_motor", 7./9.81, "kW/N", 'Motor specific power')
        Wmotor      = Variable("W_{motor}", "lbf", "motor weight")
        fstruct     = Variable("f_{struct}", 0.5, "-",
                           "structural weight fraction")
        Wstruct     = Variable("W_{struct}", "lbf", "structural weight")
        b 			= Variable("b", "ft", "Wing span")
        CL_max      = Variable("C_{L_{max, land}}", 3.5,"-", "Landing CL_max")
        constraints = [W >= Wbatt + Wpay + Wwing + Wmotor + Wstruct,
                       Wstruct >= fstruct*W,
                       Wwing >= WS*S,
                       Wmotor >= Pshaftmax/sp_motor,
                       AR == b**2/S,
                       ]

        return constraints

    def flight_model(self):
        " what happens during flight "
        return AircraftPerf(self)
class AircraftPerf(Model):
    " simple drag model "
    def setup(self, aircraft):

        CL = Variable("C_L", "-", "lift coefficient")
        CD = Variable("C_D", "-", "drag coefficient")
        cda = Variable("CDA", 0.024, "-", "non-lifting drag coefficient")
        e = Variable("e", 0.8, "-", "span efficiency")

        constraints = [CD >= cda + CL**2/pi/e/aircraft["AR"]]

        return constraints
