" trade off between aircraft range and take off distance "
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from stol import Mission
from gpkit.tools.autosweep import autosweep_1d
plt.rcParams.update({'font.size':19})

# pylint: disable=invalid-name, too-many-locals
def plot_torange(N, clmax, to=True):
    " plot trade studies of weight, range, and TO distance "

    model = Mission(sp=False)
    sto = np.linspace(50, 500, N)

    st = [":", "-.", "--", "-"]*5
    i = 0
    fig, ax = plt.subplots()
    for cl in clmax:
        if to:
            model.substitutions.update({"W_{pay}": cl})
        else:
            model.substitutions.update({"C_{L_{land}}": cl})
        Rknee = plot_wrange(model, sto, 10, plot=False)
        ax.plot(sto, Rknee, color="k", linestyle=st[i],
                label="$W_{pay} = %.1f$" % cl)
        i += 1

    ax.set_xlabel("Runway Distance [ft]")
    ax.set_ylabel("Range [nmi]")
    ax.set_ylim([0, 350])
    ax.grid()
    ax.legend(loc=4, fontsize=15)

    return fig, ax

def plot_wrange(model, sto, Nr, plot=True):
    model.cost = model.aircraft.topvar("W")

    Rmin = 25

    if plot:
        fig, ax = plt.subplots()
        figs, axs = plt.subplots()
        figv, axv = plt.subplots()

    st = [":", "-.", "--", "-"]*5
    i = 0
    Rknee = []

    for s in sto:
        model.substitutions.update({"S_{runway}": s})
        del model.substitutions["R"]
        model.cost = 1/model["R"]
        sol = model.solve("cvxopt")
        Rmax = sol("R").magnitude
        model.cost = model.aircraft.topvar("W")
        R = np.linspace(Rmin, Rmax-10, Nr)
        model.substitutions.update({"R": ("sweep", R)})
        sol = model.solve("cvxopt", skipsweepfailures=True)

        if plot:
            W = sol(model.aircraft.topvar("W"))
            ax.plot(R, W, color="k", linestyle=st[i],
                    label="$S_{runwawy} = %d [ft]$" % s)
            axv.plot(R, sol("W_{batt}")/sol(M.aircraft.topvar("W")), color="k", linestyle=st[i],
                    label="$S_{runwawy} = %d [ft]$" % s)
            lands = sol["sensitivities"]["constants"]["m_{fac}_Mission/LandingSimple"]
            axs.plot(R, lands, color="k", linestyle=st[i],
                     label="$S_{runway} = %d [ft]$" % s)
            i += 1
        # else:
        stosens = sol["sensitivities"]["constants"]["R"]
        f = interp1d(stosens, sol("R"), "cubic")
        fw = interp1d(stosens, sol(model.aircraft.topvar("W")), "cubic")
        fwf = interp1d(stosens, sol("W_{batt}")/sol(model.aircraft.topvar("W")), "cubic")
        if 1.0 > max(stosens):
            Rknee.extend([np.nan])
            wint = np.nan
            wbint = np.nan
        else:
            Rknee.extend([f(1.0)])
            wint = fw(1.0)
            wbint = fwf(1.0)

        if plot:
            ax.plot(Rknee[-1], wint, marker='o', color="k", markersize=5)
            axv.plot(Rknee[-1], wbint, marker='o', color="k", markersize=5)

    if plot:
        ax.set_ylabel("Max Takeoff Weight [lbf]")
        ax.set_xlabel("Range [nmi]")
        ax.legend(loc=4, fontsize=12)
        ax.grid()
        ax.set_ylim([0, 10000])
        axs.set_ylabel("Landing Sensitivity")
        axs.set_xlabel("Range [nmi]")
        axs.legend(loc=2, fontsize=12)
        axs.grid()
        axs.set_ylim([-0.1, 1])

    if plot:
        ret = [fig, figs, figv]
    else:
        ret = Rknee

    return ret

if __name__ == "__main__":
    M = Mission(sp=False)
    Figs = plot_wrange(M, [100], 20, plot=True)
    Figs[0].savefig("mtowrangew1200.pdf", bbox_inches="tight")
    Figs[1].savefig("landingsens.pdf", bbox_inches="tight")
    Figs[2].savefig("vrange.pdf", bbox_inches="tight")
    # Fig, _ = plot_torange(20, [400, 600, 800, 1000, 1200])
    # Fig.savefig("rangetodwpay.pdf", bbox_inches="tight")
    # Fig, _ = plot_torange(20, [3.5, 4.5, 5.5], to=False)
    # Fig.savefig("rangelandd.pdf", bbox_inches="tight")
