from openap import WRAP, aero
import matplotlib.pyplot as plt
import simulation.performance as performance
from automation.autopilot import Autopilot


def main():
    # Debug output
    debug = open("./debug.log", 'w+')
    debug.write("altitude,vs,cas,tas,aoa,cl,cd,drag,lift,mass,thrust\n")
    debug.flush()
    # PID Setup
    a319 = performance.Performance("A319", False)
    a319_wrp = WRAP(ac="A319")
    autopilot = Autopilot()
    a319.mass = 60_000.00
    a319.pitch = 0.0
    a319.gear = True
    a319.flaps = 1
    a319.pitch_target = 0.0
    a319.pitch_rate_of_change = 3.0
    target_alt = 12_000
    # simulation varibale
    a319.phase = 0
    pitchs = []
    fd_pitchs = []
    alts = []
    vs = []
    cas = []
    times = []
    thrusts = []
    drags = []
    phases = []
    i = 0
    distance_0 = 0.0
    run = True
    # a319.run()
    while run and a319.altitude >= 0:
        a319.run()
        if a319.cas > a319_wrp.takeoff_speed()["default"] and a319.phase == 0:
            a319.phase = 1
            a319.pitch_target = 15.0
        # When passing 100ft RA, the gear is up
        if a319.gear and (a319.altitude / aero.ft) > 100.0:
            a319.gear = False

        if a319.flaps > 0 and (a319.cas / aero.kts) > 210.0:
            a319.flaps = 0

        if (a319.altitude / aero.ft) > 1500.0 and\
           (a319.altitude / aero.ft) < 1550.0 and a319.phase < 2:
            a319.thrust_lever = 1.
            a319.phase = 2

        if (a319.altitude / aero.ft) > 3000.0 and a319.phase < 4:
            if a319.phase != 3:
                a319.phase = 3
                autopilot.VerticalSpeedHold(1000.0 * aero.fpm, target_alt)

        if a319.flaps == 0 and round(a319.cas / aero.kts) > 250\
                and a319.altitude / aero.ft < target_alt:
            if a319.phase != 4:
                a319.phase = 4
                speed_target = 250 * aero.kts
                autopilot.SpeedHold(speed_target, target_alt)
        #     # speed_target = 320 * aero.kts
        #     # if a319.altitude / aero.ft < 10_000:
        #     #     speed_target = 250 * aero.kts
        #     # elif a319.altitude >= aero.crossover_alt(320 * aero.kts, 0.78):
        #     #     speed_target = aero.mach2cas(0.78, a319.altitude)
        #     #     a319.thrust_lever = 1.0
        #     # if autopilot.active_mode != Autopilot.speed_hold \
        #     #         or autopilot.target != speed_target:
        #         # autopilot.SpeedHold(speed_target, target_alt)

        if a319.altitude + (a319.v_y * 30) >= target_alt * aero.ft:
            if a319.phase != 5:
                a319.phase = 5
                autopilot.AltitudeAquire(target_alt)
        if a319.altitude / aero.ft > target_alt + 200:
            if a319.phase != 7:
                a319.phase = 7
                autopilot.VerticalSpeedHold(-1000 * aero.fpm, target_alt)
                a319.thrust_lever = 0.0

        if target_alt - 200 <= a319.altitude / aero.ft <= target_alt + 200:
            if a319.phase != 6:
                a319.phase = 6
                autopilot.AltitudeHold(target_alt)
                if distance_0 == 0.0:
                    distance_0 = a319.distance_x
            if (a319.distance_x - distance_0) / aero.nm >= 10.0:
                run = False
        #     run = False
        #     continue
        if a319.cas / aero.kts >= 320:
            a319.tas = aero.cas2tas(320 * aero.kts, a319.altitude)
            # if a319.phase != 6:

        #     if a319.tas > aero.mach2tas(0.78, a319.altitude)\
        #             and autopilot.active_mode != Autopilot.mach_hold:
        #         autopilot.MachHold(0.78, target_alt)

        if a319.phase >= 0:
            if (a319.pitch > 0 or a319.altitude > 0) \
                    and (round((a319.altitude / aero.ft) / 10) * 10) \
                    % 5000 == 0:
                debug.write(f"{a319.altitude / aero.ft},{a319.vs},"
                            f"{a319.cas / aero.kts},{a319.tas/ aero.kts},"
                            f"{a319.aoa},{a319.cl},{a319.cd},{a319.drag},"
                            f"{a319.lift},{a319.mass},{a319.thrust}\n")
                debug.flush()

            if a319.phase < 7 and a319.altitude > 10_000 * aero.ft:
                a319.thrust_lever = 1.0
            if a319.phase == 7:
                a319.thrust_lever = 0.0
            mach = aero.tas2mach(a319.tas, a319.altitude)
            if autopilot.active_mode is not None:
                a319.pitch_target = autopilot.run(a319.cas,
                                                  a319.v_y,
                                                  a319.altitude,
                                                  a319.pitch,
                                                  mach)
                a319.pitch = a319.pitch_target
            print(f"{a319.phase} : {a319.altitude / aero.ft:02f}",
                  f"- {a319.vs:02f} - {a319.cas / aero.kts:02f} - ",
                  f"{mach:0.3f} - {a319.aoa:0.2f} ",
                  f"{a319.pitch:02f} / {a319.pitch_target:02f} - ",
                  f"{a319.cl:04f} - {a319.cd:04f}")
            alts.append(int(round(a319.altitude / aero.ft)))
            vs.append(int(a319.vs))
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            fd_pitchs.append(a319.pitch_target)
            thrusts.append(a319.thrust)
            drags.append(a319.drag)
            phases.append(a319.phase)
            i += 1

    print(f"Cas End  = {max(cas)}")
    draw(times, vs, alts, cas, pitchs, fd_pitchs, thrusts, drags, phases)


def draw(times, vs, alts, cas, pitchs, fd_pitchs, thurst, drag, phases):
    # fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, sharex=True)
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.set(ylabel='CAS')
    ax3.plot(times, cas)
    # ax4.set(ylabel='X Forces')
    # ax4.plot(times, thurst)
    # ax4.plot(times, drag)
    # ax5.set(ylabel='Pitch')
    # ax5.plot(times, pitchs)
    # ax5.plot(times, fd_pitchs)
    # ax6.set(ylabel='Phase')
    # ax6.plot(times, phases)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
