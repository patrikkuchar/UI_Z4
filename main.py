import random
import math
import time
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


def find_medoid(cluster):
    ##vytvorím si zoznam
    lenOfCluster = len(cluster)

    arrayOfSums = np.zeros((lenOfCluster,), dtype=int)

    for A in range(lenOfCluster-1):
        for B in range(A+1, lenOfCluster):
            distance = calculate_distance(cluster[A], cluster[B])
            arrayOfSums[A] += distance
            arrayOfSums[B] += distance


    index = np.where(arrayOfSums == np.amin(arrayOfSums))[0][0]

    return cluster[index]


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

def find_centroid(Points):
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

def find_biggest_cluster(clusters, centroids, sizes):
    ##nájde index zhluku, ktorý má najvzdialenejší bod od stredu
    ##zatiaľ so sizes nepočítam
    biggest = 0
    biggest_index = 0

    for i, cluster in enumerate(clusters):
        avgSize = calculate_avg_len(cluster, centroids[i])
        if avgSize > biggest:
            biggest = avgSize
            biggest_index = i

    return biggest_index


def calculate_avg_len(cluster, centroid):
    lenSum = 0
    counter = 0
    for point in cluster:
        lenSum += calculate_distance(point, centroid)
        counter += 1
    return lenSum / counter


def calculate_distance(point_A, point_B):
    return math.sqrt((point_A["x"] - point_B["x"])**2 + (point_A["y"] - point_B["y"])**2)

def divisive_clustering(Points, n, k):
    label = "Divízne zhlukovanie, kde stred je centroid; počet zhlukov: "
    clusters = [Points]
    centroids = [find_centroid(Points)]
    numOfClusters = 1
    numOfPoints = n
    start_time = time.time()

    show_points_on_graph(clusters, centroids, label + "1", "4_0")
    counter = 0
    while numOfClusters < k:
        counter += 1
        numOfClusters += 1

        biggestCluster_i = find_biggest_cluster(clusters, centroids, None)
        offset_x = random.randrange(-5,6)
        offset_y = random.randrange(-5,6)

        x = centroids[biggestCluster_i]["x"]
        y = centroids[biggestCluster_i]["y"]
        centroids.append({"x" : x + offset_x, "y" : y + offset_y})
        centroids.append({"x" : x - offset_x, "y" : y - offset_y})
        centroids.pop(biggestCluster_i)

        clusters = points_to_clusters(Points, centroids)

        show_points_on_graph(clusters, centroids, label + str(numOfClusters), "4_" + str(counter))

        while True:
            counter += 1
            new_centroids = []
            for j in range(numOfClusters):
                new_centroid = find_centroid(clusters[j])
                if new_centroid == None:
                    new_centroids.append(centroids[j])
                else:
                    new_centroids.append(new_centroid)

            ##vypočítam si najväčší posun centroidov
            biggest = 0
            for j in range(numOfClusters):
                distance = calculate_distance(centroids[j], new_centroids[j])
                if distance > biggest:
                    biggest = distance

            centroids = new_centroids
            clusters = points_to_clusters(Points, centroids)
            show_points_on_graph(clusters, centroids, label + str(numOfClusters), "4_" + str(counter))

            # prahova hodnota 2
            if biggest < 6:
                break

    create_GIF(counter, 4)



def aglomerative_clustering(Points, n, k):
    label = "Aglomeratívne zhlukovanie, kde stred je centroid; počet zhlukov: "
    centroids = Points
    numOfClusters = n
    clusters = []
    for point in Points:
        clusters.append([point])
    start_time = time.time()
    #vytvorím si maticu
    matrix = np.zeros(numOfClusters*numOfClusters).reshape(numOfClusters,numOfClusters)

    for A in range(numOfClusters-1):
        for B in range(A+1, numOfClusters):
            if A == B:
                continue
            distance = calculate_distance(centroids[A], centroids[B])
            matrix[A][B] = distance
            matrix[B][A] = distance

    end_time = time.time()
    print("trvalo to " + str(end_time-start_time) + " sekúnd")
    start_time = time.time()

    show_points_on_graph(clusters, centroids, label + str(numOfClusters), "3_0")

    end_time = time.time()
    print("trvalo to " + str(end_time-start_time) + " sekúnd")

    counter = 0
    while numOfClusters > k:
        counter += 1

        print(counter)

        #najdeme najbližšie 2 zhluky
        min_A = 0
        min_B = 1
        min_distance = matrix[min_A][min_B]
        for A in range(numOfClusters - 1):
            for B in range(A + 1, numOfClusters):
                if matrix[A][B] < min_distance:
                    min_distance = matrix[A][B]
                    min_A = A
                    min_B = B

        numOfClusters -= 1

        #pridelím clusterB ku clustruA a odstraním clusterB
        deleted_cluster = clusters.pop(min_B)
        centroids.pop(min_B)
        for point in deleted_cluster:
            clusters[min_A].append(point)


        #odstraním stĺpec a riadok B z matice
        matrix = np.delete(matrix, min_B, 0)
        matrix = np.delete(matrix, min_B, 1)

        #zistím centroid pre A
        centroids[min_A] = find_centroid(clusters[min_A])

        #upravím maticu v stĺpci a riadku A
        A = min_A
        for B in range(numOfClusters):
            if A == B:
                continue
            distance = calculate_distance(centroids[A], centroids[B])
            matrix[A][B] = distance
            matrix[B][A] = distance

        show_points_on_graph(clusters, centroids, label + str(numOfClusters), "3_" + str(counter))
    #show_points_on_graph(clusters, centroids, label + str(numOfClusters), "3_" + str(counter))
    create_GIF(counter, 3)
    print("hotofko")




def kMeans_medoid(Points, k, centerPoints):
    label = "k-means, kde stred je medoid; "
    medoids = centerPoints
    clusters = points_to_clusters(Points, medoids)
    show_points_on_graph(clusters, medoids, label + "0. iterácia", "2_0")

    start_time = time.time()
    i = 0
    while True:
        i += 1
        new_medoids = []
        for j in range(k):
            if len(clusters[j]) == 0:
                new_medoids.append(medoids[j])
                continue

            new_medoid = find_medoid(clusters[j])
            new_medoids.append(new_medoid)

        ##vypočítam si najväčší posun centroidov
        biggest = 0
        for j in range(k):
            distance = calculate_distance(medoids[j], new_medoids[j])
            if distance > biggest:
                biggest = distance

        medoids = new_medoids
        clusters = points_to_clusters(Points, medoids)
        show_points_on_graph(clusters, medoids, label + str(i) + ". iterácia", "2_" + str(i))

        if biggest < 2:
            break

    end_time = time.time()
    print("Čas vykonávania k-means - medoid: " + str(round(end_time-start_time, 4)) + "s")

    create_GIF(i, 2)

def kMeans_centroid(Points, k, centerPoints):
    label = "k-means, kde stred je centroid; "
    centroids = centerPoints
    clusters = points_to_clusters(Points, centroids)
    show_points_on_graph(clusters, centroids, label + "0. iterácia", "1_0")

    start_time = time.time()
    i = 0
    while True:
        i += 1
        new_centroids = []
        for j in range(k):
            new_centroid = find_centroid(clusters[j])
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


    end_time = time.time()
    print("Čas vykonávania k-means - centroid: " + str(round(end_time-start_time, 4)) + "s")

    create_GIF(i, 1)





def show_points_on_graph(clusters, clustersCentres, label, saveLabel):
    plt.title(label)
    #plt.plot(points[0]["x"], points[0]["y"])

    for i, points in enumerate(clusters):
        counter = 0
        xPoints = []
        yPoints = []
        for point in points:
            counter += 1
            xPoints.append(point["x"])
            yPoints.append(point["y"])
        if counter == 1:
            plt.scatter(xPoints, yPoints, color="k")
        else:
            plt.scatter(xPoints, yPoints)

        if counter > 5 and clustersCentres != []:
            plt.scatter(clustersCentres[i]["x"], clustersCentres[i]["y"], marker="x", color="k")

    plt.savefig("grafy/frame" + saveLabel + ".png")
    plt.figure()
    plt.clf()
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


def create_centres(k):
    points = []
    for i in range(k):
        points.append({"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)})
    return points

numberOfClusters = 10
dots = generate_dots(numberOfClusters, 500)
centerPoints = create_centres(numberOfClusters)
#kMeans_centroid(dots, numberOfClusters, centerPoints)
#kMeans_medoid(dots, numberOfClusters, centerPoints)
#aglomerative_clustering(dots, len(dots), numberOfClusters)
divisive_clustering(dots, len(dots), numberOfClusters)

