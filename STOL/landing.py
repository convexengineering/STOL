" Landing distance model "
import os
import pandas as pd
from gpkit import Variable, Model, SignomialsEnabled, units, SignomialEquality
from gpfit.fit_constraintset import FitCS
from gpkit.constraints.tight import Tight as TCS
from flightstate import FlightState
from gpkit.tools.tools import te_exp_minus1 as em1 
from stol_aircraft import testAircraft, HelioCourier

class Landing(Model):
    """
    Landing model
    http://www.dept.aoe.vt.edu/~lutze/AOE3104/takeoff&landing.pdf
    
    Landing_Margin is required additional distance for takeoff and landing operations (nominally 20%)
    """
    def setup(self, aircraft, sp=False):

        fs      = FlightState()

        A       = Variable("A", "m/s**2", "log fit equation helper 1")
        B       = Variable("B", "1/m", "log fit equation helper 2")

        g       = Variable("g", 9.81, "m/s**2", "gravitational constant")
        mu      = Variable("\\mu", 0.5, "-", "Braking coefficient of friction")
        T_rev   = Variable("T", "lbf", "Reverse thrust")
        cda     = Variable("CDA", 0.024, "-", "parasite drag coefficient")

        CLg     = Variable("C_{L_g}", "-", "ground lift coefficient")
        CDg     = Variable("C_{D_g}", "-", "grag ground coefficient")
        Kg      = Variable("K_g", 0.04, "-", "ground-effect induced drag parameter")
        #CLmax   = Variable("C_{L_{max}}", 2.5, "-", "max lift coefficient")
        Vstall  = Variable("V_{stall}", "m/s", "stall velocity")
        Sgr     = Variable("S_{gr}", "ft", "landing ground roll")
        Slnd    = Variable("S_{land}", "ft", "landing distance")
        etaprop = Variable("\\eta_{prop}", 0.01, "-", "propellor efficiency")
        lnd_mrg = Variable("Landing Margin", 1.2, "-", "Landing safety margin")

        CLmax   = aircraft["C_{L_{max, land}}"]
        constraints = [
            T_rev == aircraft["P_{shaft-max}"]*etaprop/fs["V"],
            #TCS([CDg >= cda + Kg*CLg**2]),
            CDg == Kg*CLg**2,
            CLg == CLmax/1.2**.5,
            Vstall == (2.*aircraft["W"]/fs["\\rho"]/aircraft["S"]/CLmax)**0.5,
            fs["V"] == 1.2*Vstall,
             #May be SP...
            Slnd == lnd_mrg * Sgr,
            ]
        if sp:
            with SignomialsEnabled():
                constraints.extend([
                    TCS([em1(Sgr*2*B,3) >= B*fs["V"]**2./A]),
                    #SignomialEquality(B*aircraft["W"]/g + 0.5*fs["\\rho"]*aircraft["S"]*mu * CLg,
                    # 0.5*fs["\\rho"]*aircraft["S"]*CDg),
                    B  <= g/aircraft["W"]*0.5*fs["\\rho"]*aircraft["S"]*CDg,
                    TCS([A/g <=  T_rev/aircraft["W"] + mu]),
                    ])

        else:
            constraints.extend([
                B >= g/aircraft["W"]*0.5*fs["\\rho"]*aircraft["S"]*CDg])

        return constraints, fs

if __name__ == "__main__":
    ac  = testAircraft()
    M   = Landing(ac, sp=True)
    M.cost = M["S_{land}"]
    sol = M.localsolve("mosek")
    #sol = M.debug("mosek")
    print sol.table()

    #hc = HelioCourier()
    #M  = Landing(hc)
    ##M.cost = 1/M["S_{land}"]
    #sol    = M.solve("mosek")
    #print sol.table()  
