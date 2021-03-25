class LiftDrag:

    def interpolate(self, x, x1, x2, y1, y2):
        return y1 + (((x - x1) / (x2 - x1)) * (y2 - y1))

    def __init__(self, path):
        self.aoas = []
        self.coefficients = []

        with open(path, 'r') as fin:
            datas = fin.readlines()
            fin.close()

        for line in datas[1:]:
            aoa, cl, cd = line.strip('\n').split(',')
            aoa = float(aoa)
            cl = float(cl)
            cd = float(cd)
            self.aoas.append(aoa)
            self.coefficients.append((cl, cd))

    def get_data(self, aoa: float) -> tuple:
        """Return the Cl and Cd data for the selected Angle of Attack

        Args:
            aoa (float): requested angle of attack

        Returns:
            tuple: tuple of 2 items : (Cl, Cd)
        """
        aoa = round(aoa, 2)
        if aoa in self.aoas:
            index = self.aoas.index(aoa)
            return self.coefficients[index]

        for i in range(len(self.aoas) - 1):
            if self.aoas[i] >= aoa and self.aoas[i+1] <= aoa:
                cl = self.interpolate(aoa, self.aoas[i+1], self.aoas[i],
                                      self.coefficients[i+1][0],
                                      self.coefficients[i][0])
                cd = self.interpolate(aoa, self.aoas[i+1], self.aoas[i],
                                      self.coefficients[i+1][1],
                                      self.coefficients[i][1])
                return (cl, cd)
        if aoa > self.aoas[0]:
            return (self.coefficients[0][0], self.coefficients[0][1])
        index = len(self.aoas) - 1
        if aoa < self.aoas[index]:
            return (self.coefficients[index][0], self.coefficients[index][1])


if __name__ == "__main__":
    a319 = LiftDrag("./data/a319_ld.csv")
    print(a319.get_data(15.35))
