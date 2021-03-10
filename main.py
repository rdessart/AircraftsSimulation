import performance
from openap import WRAP, aero

def main():
    a319 = performance.Performance("A319")
    a319_wrp = WRAP(ac="A319")
    a319.cas = a319_wrp.takeoff_speed()["default"]
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 15.0
    a319.gear = False
    a319.flaps = 1
    a319.output.write(str(a319))
    a319.output.flush()
    print("Starting")
    while a319.takeoff_climb():
        #When passing 100ft RA, the gear is up
        if (a319.altitude / aero.ft) > 100.0:
            a319.gear = False
        continue
    print("Finished")
    

if __name__ == "__main__":
    main()
