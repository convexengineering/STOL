from gpfit.fit import fit
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
plt.rcParams.update({'font.size':15})
GENERATE = True

def powerfit():
    ce_takeoff = [0.053946,0.105668,0.178928,0.275163,0.395264,
            0.539732,0.708790,0.902466,1.120647,1.363123,
            1.629615,1.919797,2.233313,2.569784,2.928823,
            3.310036,3.713028,4.137408,4.582789,5.048791,
            5.535040,6.041175,6.566841,7.111693,7.675397,
            8.257629,8.858074,9.476427,10.112392,10.765684,
            11.436026,12.123149,12.826795,13.546712,14.282657,
            15.034394,15.801697,16.584343,17.382119,18.194818,19.022239]
    ce_land = [0.273832,0.429759,0.612525,0.819814,1.049818,1.301074,1.572364,1.862659,2.171069,2.496819,2.839224,3.197672,3.571614,3.960553,4.364035,4.781646,5.213004,5.657756,6.115574,6.586154,7.069211,7.564477,8.071702,8.590650,9.121098,9.662835,10.215660,10.779384,11.353827,11.938815,12.534186,13.139782,13.755454,14.381056,15.016452,15.661508,16.316098,16.980100,17.653394,18.335867,19.027410]

    cl = np.arange(2., 10.2, .2)
    u_t = ce_takeoff
    w = cl


    x = np.log(u_t)
    y = np.log(w)

    cn_takeoff, err = fit(x, y, 3 , "SMA")
    rm = err
    print "RMS error: %.4f" % rm
    print cn_takeoff

    u_l = ce_land
    x = np.log(u_l)
    cn_land, err = fit(x, y, 2, "SMA")

    rm = err
    print "RMS error: %.4f" % rm
    #print cn_land
    yfit_takeoff = cn_takeoff.evaluate(x)
    yfit_land = cn_land.evaluate(x)
    df = cn_land.get_dataframe()
    # df = None
    fig, ax = plt.subplots()
    #ax.plot(u_t, w, lw=2)
    #ax.plot(u_t, np.exp(yfit_takeoff), "--", lw=3)
    ax.plot(u_l, w, lw=2)
    ax.plot(u_l, np.exp(yfit_land), "--", lw=3)
    ax.grid()
    ax.set_xlabel("$C_E$")
    ax.set_ylabel("$C_L$")

    return df, fig, ax

if __name__ == "__main__":

    df, fig, ax = powerfit()
    df.to_csv("power_fit.csv")
    fig.savefig("power.pdf", bbox_inches="tight")
