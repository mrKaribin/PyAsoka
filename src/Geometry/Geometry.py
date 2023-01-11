from PyAsoka.src.Geometry.Straight import Straight


class Geometry:

    @staticmethod
    def linearApproximation2D(points: list):
        X, Y = [], []
        for point in points:
            if point is not None:
                X.append(point.x)
                Y.append(point.y)

        n = len(X)
        sigma_P = 0
        for i in range(n):
            sigma_P += X[i] * Y[i]

        sigma_X = sum(X)
        sigma_Y = sum(Y)

        sigma_X2 = 0
        for i in range(n):
            sigma_X2 += X[i] * X[i]

        a = (n * sigma_P - sigma_X * sigma_Y) / (n * sigma_X2 - (pow(sigma_X, 2)))
        c = (sigma_Y - a * sigma_X) / n
        b = -1
        return Straight(a, b, c)
