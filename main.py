import random
import math
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image as img

def create_GIF(numOfIterations, n):
    path = "grafy/frame"
    frames = [img.open(path + "0.png")]
    path += str(n) + "_"

    for i in range(numOfIterations+1):
        frames.append(img.open(path + str(i) + ".png"))

    frames[0].save('gifko_' + str(n) + '.gif', format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=750, loop=10)




def points_to_clusters(Points, clustersCentres):
    clusters = []
    k = len(clustersCentres)
    for i in range(k):
        clusters.append([])

    for point in Points:
        ##vypočet najbližšieho bodu
        nearest_dist = 10000
        nearest_index = -1

        for i in range(k):
            distance = calculate_distance(clustersCentres[i], point)
            if distance < nearest_dist:
                nearest_dist = distance
                nearest_index = i

        clusters[nearest_index].append(point)

    return clusters

def calculate_average(Points):
    counter = 0
    sum_x = 0
    sum_y = 0
    for point in Points:
        counter += 1
        sum_x += point["x"]
        sum_y += point["y"]

    if counter == 0:
        return None
    return {"x" : sum_x//counter, "y" : sum_y//counter}



def calculate_distance(point_A, point_B):
    return math.sqrt((point_A["x"] - point_B["x"])**2 + (point_A["y"] - point_B["y"])**2)

def kMeans_centroid(Points, k):
    label = "k-means, kde stred je centroid; "

    centroids = []

    for i in range(k):
        centroids.append({"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)})

    clusters = points_to_clusters(Points, centroids)

    show_points_on_graph(clusters, centroids, label + "0. iterácia", "1_0")

    i = 0
    while True:
        i += 1
        new_centroids = []
        for j in range(k):
            new_centroid = calculate_average(clusters[j])
            if new_centroid == None:
                new_centroids.append(centroids[j])
            else:
                new_centroids.append(new_centroid)

        ##vypočítam si najväčší posun centroidov
        biggest = 0
        for j in range(k):
            distance = calculate_distance(centroids[j], new_centroids[j])
            if distance > biggest:
                biggest = distance


        centroids = new_centroids
        clusters = points_to_clusters(Points, centroids)
        show_points_on_graph(clusters, centroids, label + str(i) + ". iterácia", "1_" + str(i))

        #prahova hodnota 2
        if biggest < 2:
            break

    create_GIF(i, 1)





def show_points_on_graph(clusters, clustersCentres, label, saveLabel):
    plt.title(label)
    #plt.plot(points[0]["x"], points[0]["y"])

    for points in clusters:
        xPoints = []
        yPoints = []
        for point in points:
            xPoints.append(point["x"])
            yPoints.append(point["y"])
        plt.scatter(xPoints, yPoints)

    for center in clustersCentres:
        plt.scatter(center["x"], center["y"], marker="x", color="k")


    plt.savefig("grafy/frame" + saveLabel + ".png")
    plt.figure()
    #plt.show()

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

    show_points_on_graph([Points], [], "Základny graf", "0")

    return Points



pointy = generate_dots(10, 20000)
kMeans_centroid(pointy, 10)

