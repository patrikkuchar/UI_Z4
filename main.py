import random

import numpy as np
from matplotlib import pyplot as plt

def show_points_on_graph(points):
    plt.title("Selekcia: ")
    plt.xlabel("Generacie")
    plt.ylabel("Fitness")
    #plt.plot(points[0]["x"], points[0]["y"])
    plt.scatter(points[0]["x"], points[0]["y"])

    plt.scatter(points[1]["x"], points[1]["y"])
    plt.scatter(points[3]["x"], points[3]["y"])
    plt.scatter(points[4]["x"], points[4]["y"])
    plt.scatter(points[5]["x"], points[5]["y"])
    plt.show()

def generate_dots(numOnStart, numOfAll):
    Points = []

    count = 0
    while count < numOnStart:
        point = {"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)}

        if point not in Points:
            Points.append(point)
            count += 1


    length = numOnStart
    for i in range(numOfAll):
        selected_point = Points[random.randrange(length)]

        off_x1 = -100
        off_x2 = 101
        off_y1 = -100
        off_y2 = 101

        if selected_point["x"] < -4900:
            off_x1 = -5000 - selected_point["x"]
        elif selected_point["x"] > 4900:
            off_x2 = 5001 - selected_point["x"]
        if selected_point["y"] < -4900:
            off_y1 = -5000 - selected_point["y"]
        elif selected_point["y"] > 4900:
            off_y2 = 5001 - selected_point["y"]

        new_point = {"x" : selected_point["x"] + random.randrange(off_x1,off_x2),
                     "y" : selected_point["y"] + random.randrange(off_y1,off_y2)}

        Points.append(new_point)
        length += 1

    show_points_on_graph(Points)



generate_dots(20, 10)