import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
# consts
m = 225
I22 = 12.5
f1z1 = 20
f2z1 = 0
f3z1 = -20
fz3max = 4
T, L = 1, 1

#  решение управляемой системы в момент вр tk = 60 / T
#  (посчитал руками, тк не зависит от различий в возмущениях)
q = [0, 0, -32, -60 * fz3max * T * T / (m * L), 0, 0]


def vozmush(dM1z2, dM3z2, df1z1, df3z1):
    #  решение СДУ на 3-х промежутках времени
    #  1 - разгон, 2 - дрейф, 3 - торможение
    #  =====================================

    #  обезразмеривание:
    v1z1 = df1z1 * T * T / (m * L)
    v1z2 = dM1z2 * T * T / I22
    up1z1 = f1z1 * T * T / (m * L)
    v3z1 = df3z1 * T * T / (m * L)
    v3z2 = dM3z2 * T * T / I22
    up3z1 = f3z1 * T * T / (m * L)

    #  1 - разгон, 0 <= t <= 20 / T
    #  н.у.: x1(0) = 0, x3(0) = -20
    t = np.linspace(0, 20 / T, 1000)
    y0 = [0, 0, -20, 0, 0, 0]

    def f2(y, t):
        s1, s2, s3, s4, s5, s6 = y
        return [s2, v1z1, s4, -s5 * up1z1, s6, v1z2]

    solution1s = odeint(f2, y0, t)
    #  2 - дрейф, 20 / T <= t <= 40 / T
    #  н.у.: конечная точка для разгона
    t = np.linspace(20 / T, 40 / T, 1000)
    y0 = solution1s[-1]

    def f2(y, t):
        s1, s2, s3, s4, s5, s6 = y
        return [s2, 0, s4, 0, s6, 0]

    solution2s = odeint(f2, y0, t)
    #  3 - торможение, 40 / T <= t <= 60 / T
    #  н.у.: конечная точка для дрейфа
    t = np.linspace(40 / T, 60 / T, 1000)
    y0 = solution2s[-1]

    def f2(y, t):
        s1, s2, s3, s4, s5, s6 = y
        return [s2, v3z1, s4, -s5 * up3z1, s6, v3z2]

    solution3s = odeint(f2, y0, t)
    # возвращаю s1, s3
    return solution3s[-1][0], solution3s[-1][2]


#  функция нахождения расстояния от горизонтального отрезка до точки на пл-ти
#  xl, yl - левый конец конец отрезка
#  xr, yr - правый конец конец отрезка
#  x, y - точка
def d_line_dot(xl, yl, xr, yr, x, y):
    #  здесь конечно же заложено знание того факта, что отрезок горизонтален
    #  возвращается в таком формате (расстояние, X_point, Y_point, X_otrezok, Y_otrezok)
    if x > xr:
        dist = ((xr - x) ** 2 + (yr - y) ** 2) ** (1/2)
        return dist, xr, yr
    elif x < xl:
        dist = ((xl - x) ** 2 + (yl - y) ** 2) ** (1 / 2)
        return dist, xl, yl
    else:
        dist = abs(y - yl)  #  yl = yr
        return dist, x, yl


if __name__ == '__main__':
    point1 = vozmush(0.004, -0.005, 0, -0.2)
    point2 = vozmush(0.004, 0, 0, -0.5)
    point3 = vozmush(0.0042, 0, -0.03, 0)
    point4 = vozmush(0.0041, 0, 0, 0.2)
    #  координаты управляемой системы
    q1, q3 = q[0], q[2]

    #  Du отрезок
    xl, yl = - abs(q3), q1
    xr, yr = abs(q3), q1

    #  нахожу самую дальнюю точку
    dists = []
    for point in [point1, point2, point3, point4]:
        dists.append(d_line_dot(xl, yl, xr, yr, *point[::-1]))  #  [::-1] потому что коор-ты в порядке s1, s3

    #  параметры окружности
    R = max(dists, key=lambda x: x[0])[0]
    centre = [0, 0]
    for elem in dists:
        if elem[0] == R:
            centre = [elem[1], elem[2]]

    #  Изображение точек и окружности
    #  рисование точек
    plt.plot([point1[1], point2[1], point3[1], point4[1]], [point1[0], point2[0], point3[0], point4[0]], 'ro')
    i = 1
    for P in [point1, point2, point3, point4]:
        plt.annotate(str(i), (P[1] + 0.05, P[0]))
        i += 1

    # изображение дистанции до Du
    i = 0
    for P in [point1, point2, point3, point4]:
        plt.annotate(str(dists[i][0]), (P[1] - 0.05, P[0]))
        i += 1

    # изображение отрезков кратчайшего расстояния от точки до отрезка Du
    i = 0
    for P in [point1, point2, point3, point4]:
        plt.plot([dists[i][1:][0], P[1]], [dists[i][1:][1], P[0]])
        i += 1

    #  координаты точек
    print(f'point1 = {point1[1]}, {point1[0]}')
    print(f'point2 = {point2[1]}, {point2[0]}')
    print(f'point3 = {point3[1]}, {point3[0]}')
    print(f'point4 = {point4[1]}, {point4[0]}')

    #  рисование отрезка
    plt.plot([xl, xr], [0, 0], color='green')

    #  рисование круга
    plt.annotate('.O', centre)
    circle = plt.Circle(xy=centre, radius=R, color='b', fill=False)
    ax = plt.gca()
    ax.grid()
    ax.add_patch(circle)
    plt.title('Поиск седловой точки')
    plt.savefig('result.png')
