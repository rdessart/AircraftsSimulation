from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance
from automation.autopilot import Autopilot


def main():
    # PID Setup
    a319 = performance.Performance("A319", False)
    a319_wrp = WRAP(ac="A319")
    autopilot = Autopilot()
    a319.mass = 66_000.00
    a319.pitch = 0.0
    a319.gear = True
    a319.flaps = 1
    a319.pitch_target = 0.0
    a319.pitch_rate_of_change = 3.0
    target_alt = 39_000
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
            a319.thrust_percent = 0.9  # Thrust reduction altitud
            # auto_thrust.thrust_reduction = True
            a319.phase = 2

        if (a319.altitude / aero.ft) > 3000.0 and a319.phase < 4:
            if a319.phase != 3:
                a319.phase = 3
                autopilot.VerticalSpeedHold(1000.0 * aero.fpm, target_alt)

        if a319.flaps == 0 and round(a319.cas / aero.kts) > 250\
                and a319.altitude / aero.ft < target_alt:
            if a319.phase != 4:
                a319.phase = 4
            speed_target = 320 * aero.kts

            if a319.altitude / aero.ft < 10_000:
                speed_target = 250 * aero.kts
            elif a319.altitude >= aero.crossover_alt(320 * aero.kts, 0.78):
                # if not a319.cruise_thrust:
                #     a319.cruise_thrust = True
                # a319.thrust_percent = 1.0
                speed_target = aero.mach2cas(0.78, a319.altitude)
            if autopilot.active_mode != Autopilot.speed_hold \
                    or autopilot.target != speed_target:
                autopilot.SpeedHold(speed_target, target_alt)

        if a319.altitude + (a319.v_y * 30) >= target_alt * aero.ft:
            if a319.phase != 5:
                a319.phase = 5
        if a319.altitude / aero.ft > target_alt + 200:
            if a319.phase != 7:
                a319.phase = 7
                autopilot.VerticalSpeedHold(-1000 * aero.fpm, target_alt)
                a319.thrust_percent = 0.0

        if target_alt - 200 <= a319.altitude / aero.ft <= target_alt + 200:
            if a319.phase != 6:
                a319.phase = 6
                if distance_0 == 0.0:
                    distance_0 = a319.distance_x
                autopilot.AltitudeHold(target_alt)
            if (a319.distance_x - distance_0) / aero.nm >= 20.0:
                run = False
            if a319.tas > aero.mach2tas(0.78, a319.altitude)\
                    and autopilot.active_mode != Autopilot.mach_hold:
                autopilot.MachHold(0.78, target_alt)

        if a319.phase >= 0:
            if a319.phase < 7:
                a319.thrust_percent = 1.0
            if a319.phase == 7:
                a319.thrust_percent = 0.0
            mach = aero.tas2mach(a319.tas, a319.altitude)
            # if a319.phase == 5 or a319.phase == 6:
            #     auto_thrust.SpeedHold(aero.mach2cas(0.78, a319.altitude))
            # if auto_thrust.active_mode is not None:
            #     a319.thrust_percent = auto_thrust.run(a319.cas)
            if autopilot.active_mode is not None:
                a319.pitch_target = autopilot.run(a319.cas,
                                                  a319.v_y,
                                                  a319.altitude,
                                                  a319.pitch,
                                                  mach)
            print(f"{a319.phase} : {a319.altitude / aero.ft:02f}",
                  f"- {a319.vs:02f} - {a319.cas / aero.kts:02f} - ",
                  f"{mach:0.3f} - {a319.aoa:0.2f} ",
                  f"{a319.pitch:02f} / {a319.pitch_target:02f}")
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

    print(f"Cas End  = {a319.cas / aero.kts}")
    draw(times, vs, alts, cas, pitchs, fd_pitchs, thrusts, drags, phases)


def draw(times, vs, alts, cas, pitchs, fd_pitchs, thurst, drag, phases):
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.set(ylabel='CAS')
    ax3.plot(times, cas)
    ax4.set(ylabel='X Forces')
    ax4.plot(times, thurst)
    ax4.plot(times, drag)
    ax5.set(ylabel='Pitch')
    ax5.plot(times, pitchs)
    ax5.plot(times, fd_pitchs)
    ax6.set(ylabel='Phase')
    ax6.plot(times, phases)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
    # from openap import Thrust, prop, Drag
    # aircraft_data = prop.aircraft("A319")
    # ac_thrust = Thrust("A319", eng=aircraft_data["engine"]["default"])
    # ac_drag = Drag(ac="A319")
    # thrust0 = []
    # thrust1 = []
    # drags0 = []
    # drags1 = []
    # a319 = performance.Performance("A319", False)
    # for alt in range(0, 390):
    #     alt_m = (alt * 100) * aero.ft
    #     spd = aero.cas2tas(320, alt_m)
    #     if alt_m * aero.ft > aero.crossover_alt(320, 0.78):
    #         spd = aero.mach2tas(0.78, alt_m)
    #     a319.altitude = alt_m
    #     a319.tas = spd
    #     a319.aoa = 0.0
    #     thrust0.append(ac_thrust.takeoff(tas=spd * aero.kts, alt=alt * 100))
    #     thrust1.append(ac_thrust.cruise(tas=spd * aero.kts, alt=alt * 100))
    #     drags0.append(ac_drag.clean(mass=60_000, tas=spd, alt=alt * 100))
    #     a319._Performance__get_Q()
    #     a319._Performance__calculate_drag()
    #     drags1.append(a319.drag)
    # fig, ax = plt.subplots()
    # ax.plot(range(0, 39000, 100), thrust0, label='thrust 0')
    # ax.plot(range(0, 39000, 100), thrust1, label='thrust 1')
    # ax.plot(range(0, 39000, 100), drags0, label='drag 0')
    # ax.plot(range(0, 39000, 100), drags1, label='drag 1')
    # plt.grid()
    # plt.legend()
    # plt.show()
