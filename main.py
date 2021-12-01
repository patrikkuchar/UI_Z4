import random
import math
import numpy as np
from matplotlib import pyplot as plt

def calculate_distance(point_A, point_B):
    return math.sqrt((point_A["x"] - point_B["x"])**2 + (point_A["y"] - point_B["y"])**2)

def kMeans_centroid(Points, k):
    centroids = []
    clusters = []

    for i in range(k):
        centroids.append({"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)})
        clusters.append([])

    for point in Points:
        ##vypočet najbližšieho bodu
        nearest_dist = 10000
        nearest_index = -1

        for i in range(k):
            distance = calculate_distance(centroids[i], point)
            if distance < nearest_dist:
                nearest_dist = distance
                nearest_index = i

        clusters[nearest_index].append(point)

    show_points_on_graph(clusters)



def show_points_on_graph(clusters):
    plt.title("Názov grafu")
    #plt.plot(points[0]["x"], points[0]["y"])

    for points in clusters:
        xPoints = []
        yPoints = []
        for point in points:
            xPoints.append(point["x"])
            yPoints.append(point["y"])
        plt.scatter(xPoints, yPoints)

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

    show_points_on_graph([Points])

    return Points



pointy = generate_dots(20, 20000)
kMeans_centroid(pointy, 8)