class Thrust:

    def interpolate(self, x, x1, x2, y1, y2):
        return y1 + (((x - x1) / (x2 - x1)) * (y2 - y1))

    def __init__(self, path):
        self.datas = {}

        with open(path, 'r') as fin:
            datas = fin.readlines()
            fin.close()

        for line in datas[1:]:
            alt, mach, thrust = line.strip('\n').split(',')
            alt = float(alt)
            mach = float(mach)
            thrust = float(thrust)
            if alt in self.datas:
                self.datas[alt].append((mach, thrust))
            else:
                self.datas[alt] = [(mach, thrust)]

    def _getThrust(self, datas_col, mach):
        if mach < datas_col[0][0]:
            return datas_col[0][1]
        if mach > datas_col[len(datas_col) - 1][0]:
            return datas_col[len(datas_col) - 1][1]
        for i in range(len(datas_col[1:]) - 1):
            i_mach, i_thurst = datas_col[i]
            if mach == i_mach:
                return i_thurst
            i_mach_0, i_thurst_0 = datas_col[i - 1]
            if i_mach_0 <= mach and i_mach >= mach:
                return self.interpolate(mach, i_mach_0,
                                        i_mach, i_thurst_0, i_thurst)
        return None

    def get_data(self, mach: float, alt: float) -> tuple:
        """Return the TOGA Thrust for a given altitude and mach number
        Args:
            mach (float): the requested mach number [0.X]
            alt (float): the request altitude in meters

        Returns:
            tuple: tuple of 2 items : (Cl, Cd)
        """
        mach = round(mach, 3)
        alt = round(alt / 0.3048)
        alts = [alt for alt in self.datas.keys()]
        if alt in alts:
            return self._getThrust(self.datas[alt], mach)
        elif alt < alts[0]:
            return self._getThrust(self.datas[alts[0]], mach)
        elif alt > alts[len(alts) - 1]:
            return self._getThrust(self.datas[alts[len(alts) - 1]], mach)
        else:
            for i in range(len(alts[1:])):
                if alts[i - 1] <= alt and alts[i] >= alt:
                    thrust_0 = self._getThrust(self.datas[alts[i - 1]], mach)
                    thrust_1 = self._getThrust(self.datas[alts[i]], mach)
                    return self.interpolate(alt, alts[i - 1], alts[i],
                                            thrust_0, thrust_1)


if __name__ == "__main__":
    a319 = Thrust("./data/a319_thrust.csv")
    # print(a319.datas)
    print(a319.get_data(0.2955, 25000))
