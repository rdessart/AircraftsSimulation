import performance
from openap import WRAP, aero

def main():
    a319 = performance.Performance("A319")
    a319_wrp = WRAP(ac="A319")
    # print(a319_wrp.takeoff_speed())
    cas_start = a319_wrp.takeoff_speed()["maximum"]
    a319.cas = a319_wrp.takeoff_speed()["maximum"]
    a319.mass = 60_000.00
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 15.0
    a319.gear = False
    a319.flaps = 1
    a319.pitch_target = 15.0
    print("Starting")
    while a319.altitude < 3000.0 * aero.ft:
        a319.run()
        print(a319.altitude / aero.ft)
        #When passing 100ft RA, the gear is up
        if (a319.altitude / aero.ft) > 100.0:
            a319.gear = False
        if (a319.altitude / aero.ft) > 1500.0:
            a319.thrust_percent = 0.8 # Thrust reduction altitude
        continue
    print(f"Cas Start  = {cas_start / aero.kts}")
    print(f"Cas End  = {a319.cas / aero.kts}")
    print("Finished")
    

if __name__ == "__main__":
    main()

# 92 -> 87 || 178.84 -> 169