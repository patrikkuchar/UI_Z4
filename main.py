import random
import math
import time
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image as img
import copy
import drawSvg as draw

class Node:
    def __init__(self, parent, left_node, right_node, value, depth, seq):
        self.parent = parent
        self.left_node = left_node
        self.right_node = right_node
        self.value = value
        self.depth = depth
        self.seq = seq

def create_GIF(numOfIterations, n):
    if not showGraphs:
        return

    path = "grafy/frame"
    frames = []
    path += str(n) + "_"

    for i in range(numOfIterations+1):
        frames.append(img.open(path + str(i) + ".png"))

    frames[0].save('gifko_' + str(n) + '.gif', format='GIF',
                   append_images=frames[1:],
                   save_all=True,
                   duration=700, loop=10)

def draw_dendogram(root_node):
    move_to_node(root_node, -1)
    d.setPixelScale(2)
    d.saveSvg('aglomerative_dendogram.svg')

d = draw.Drawing(200600, 40200, displayInline=False)
dend_position = [10,40190]
global_x_for_leafs = 10

def move_to_node(node, color):
    global dend_position, global_x_for_leafs
    colors = ["#0000ff","#556b2f","#ffff00","#191970","#ff4500","#00bfff","#ff1493","#00ff7f","#000000"]

    #if not leaf
    if node.value == None:

        if color == -1:
            new_color_l = 50
            new_color_r = 150
            color = 8
        elif color > 40:
            new_color_l = color // 5
            new_color_r = color // 5 + 10
            color = 8
        elif color >= 10:
            new_color_l = color // 5 - 2
            new_color_r = color // 5 - 1
            color = 8
        else:
            new_color_l = color
            new_color_r = color

        move_to_node(node.left_node, new_color_l)
        x1 = dend_position[0]
        #horizontalna čiara
        #if (node.left_node.value != None):
        #d.append(draw.Line(g_position[0], g_position[1], g_position[0] + (seq*10), g_position[1], stroke='red'))

        move_to_node(node.right_node, new_color_r)
        #if (node.left_node.value != None):
        x2 = dend_position[0]

        d.append(draw.Line(x1, dend_position[1], x2, dend_position[1], stroke=colors[color]))
        #d.append(draw.Line(g_position[0], g_position[1], g_position[0] - (seq*10), g_position[1], stroke='red'))

        dend_position[0] -= abs(x1-x2)/2
        if node.parent != None:
            d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], 40190 - node.parent.depth * 2 , stroke=colors[color]))
            dend_position[1] = 40190 - node.parent.depth*2
        else:
            d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], 0 , stroke="black"))

    #vertikalna čiara
    else: #leaf
        dend_position[1] = 40190
        dend_position[0] = global_x_for_leafs
        global_x_for_leafs += 10

        d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], dend_position[1] - node.parent.depth*2, stroke=colors[color]))

        dend_position[1] -= node.parent.depth*2






def find_medoid(cluster):
    ##vytvorím si zoznam
    lenOfCluster = len(cluster)

    arrayOfSums = np.zeros((lenOfCluster,), dtype=float)

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
    return math.sqrt(math.pow(point_A["x"] - point_B["x"],2) + math.pow(point_A["y"] - point_B["y"],2))

def calculate_time(seconds):
    milis = int(seconds * 1000 % 1000)
    seconds = int(seconds)

    minutes = seconds // 60
    seconds %= 60

    hours = minutes // 60
    minutes %= 60

    output = ""
    if hours != 0:
        output += str(hours) + "h "
    if minutes != 0:
        output += str(minutes) + "m "
    if seconds != 0:
        output += str(seconds) + "s "
    if milis != 0:
        output += str(milis) + "ms "

    return output


def divisive_clustering(Points, n, k):
    label = "Divízne zhlukovanie, kde stred je centroid; počet zhlukov: "
    clusters = [Points]
    centroids = [find_centroid(Points)]
    numOfClusters = 1
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

    end_time = time.time()
    print("Čas vykonávania Divízneho zhlukovania: " + calculate_time(round(end_time - start_time, 4)))

    global_file.write("\ndivisive: " + str(int(end_time-start_time)))

    create_GIF(counter, 4)



def aglomerative_clustering(Points, n, k):
    label = "Aglomeratívne zhlukovanie, kde stred je centroid; počet zhlukov: "
    centroids = Points
    numOfClusters = n
    clusters = []
    nodes_array = []
    for i, point in enumerate(Points):
        clusters.append([point])
        nodes_array.append(Node(None, None, None, i, 0, 0))

    start_time = time.time()
    #vytvorím si maticu
    matrix = np.zeros(numOfClusters*numOfClusters, dtype=int).reshape(numOfClusters,numOfClusters)


    for A in range(numOfClusters-1):
        for B in range(A, numOfClusters):
            if A == B:
                matrix[A][A] = 15000
                continue
            distance = int(calculate_distance(centroids[A], centroids[B]))
            matrix[A][B] = distance
            matrix[B][A] = distance
    matrix[-1][-1] = 15000


    counter = 0
    while numOfClusters > 1:#k:
        counter += 1

        result = np.where(matrix == np.min(matrix))
        if len(result[0]) == 2:
            min_A = result[0][0]
            min_B = result[0][1]
        else:
            lowest = 15000
            for A in result[0]:
                for B in result[0]:
                    if matrix[A][B] < lowest:
                        lowest = matrix[A][B]
                        min_A = A
                        min_B = B

        numOfClusters -= 1

        ##aby sa odstranil väčší (nenastane posun)
        if min_B < min_A:
            min_A, min_B = min_B, min_A

        ##nodes pre vykreslenie
        seq = nodes_array[min_A].seq
        if nodes_array[min_B].seq > seq:
            seq = nodes_array[min_B].seq
        parent_node = Node(None, nodes_array[min_A], nodes_array[min_B],
                           None, counter, seq+1)
        nodes_array[min_A].parent = parent_node
        nodes_array[min_B].parent = parent_node

        nodes_array.pop(min_B)
        nodes_array[min_A] = parent_node

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

        if numOfClusters == k:
            show_points_on_graph(clusters, centroids, label + str(numOfClusters), "3")

    end_time = time.time()
    print("Čas vykonávania Aglomeratívneho zhlukovania: " + calculate_time(round(end_time-start_time, 4)))

    global_file.write("\naglomerative: " + str(int(end_time-start_time)))

    #draw_dendogram(nodes_array[0])

    #create_GIF(counter, 3)




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
    print("Čas vykonávania k-means - medoid: " + calculate_time(round(end_time-start_time, 4)))

    global_file.write("\nk-means-m: " + str(int(end_time-start_time)))

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
    print("Čas vykonávania k-means - centroid: " + calculate_time(round(end_time-start_time, 4)))

    global_file.write("\nk-means-c: " + str(int(end_time-start_time)))

    create_GIF(i, 1)





def show_points_on_graph(clusters, clustersCentres, label, saveLabel):
    if not showGraphs:
        return

    plt.title(label)
    #plt.plot(points[0]["x"], points[0]["y"])

    colors = ["#e6194B","#3cb44b","#ffe119","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#bfef45","#fabed4"
              ,"#469990","#dcbeff","#9A6324","#fffac8","#800000","#aaffc3","#808000","#ffd8b1","#000075","#a9a9a9"]


    centres = True
    if len(clustersCentres) == 0:
        centres = False

    if centres:
        p = []
        for x in range(-5000,5000,10):
            for y in range(-5000,5000,10):
                p.append({"x" : x, "y" : y})
        clust = points_to_clusters(p, clustersCentres)
        for i, points in enumerate(clust):
            xPoints = []
            yPoints = []
            for point in points:
                xPoints.append(point["x"])
                yPoints.append(point["y"])
            plt.scatter(xPoints,yPoints, marker="s", color=colors[i])



    x_centres = []
    y_centres = []

    xPoints = []
    yPoints = []

    for i, cluster in enumerate(clusters):
        for point in cluster:
            xPoints.append(point["x"])
            yPoints.append(point["y"])
        if centres:
            x_centres.append(clustersCentres[i]["x"])
            y_centres.append(clustersCentres[i]["y"])


    plt.scatter(xPoints,yPoints, color="k")
    if centres:
        plt.scatter(x_centres,y_centres, marker="x", color="#ffffff")



    if centres:
        biggest_cluster = 0
        for i, cluster in enumerate(clusters):
            sum_distance = 0
            counter = 0
            for point in cluster:
                counter += 1
                sum_distance += calculate_distance(point, clustersCentres[i])
            avg = int(sum_distance) // counter
            if avg > biggest_cluster:
                biggest_cluster = avg

        plt.xlabel("Najväčšia priemerna vzdialenosť od centra zhluku: " + str(biggest_cluster))


    #X, Y = np.meshgrid(x, y)

    #plt.scatter(0,0,marker="s",color="k")

    #plt.scatter(100,100,marker="s",color="k")



    plt.savefig("grafy/frame" + saveLabel + ".png")
    plt.show()
    plt.figure()
    plt.clf()

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


def create_centres(all_points, k):
    points = []
    l = len(all_points)
    for i in range(k):
        while True:
            point = all_points[random.randrange(l)]
            if point not in points:
                points.append(point)
                break
    #for i in range(k):
        #points.append({"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)})
    return points

showGraphs = False

global_file = open("vysledky.txt","w")

for i in range(3):
    numberOfClusters = 20
    dots = generate_dots(numberOfClusters, 20000)
    centerPoints = create_centres(dots, numberOfClusters)

    print("\n" + str(i+1) + ". testovanie\n\n")

    kMeans_centroid(copy.copy(dots), numberOfClusters, centerPoints)
    kMeans_medoid(copy.copy(dots), numberOfClusters, centerPoints)
    aglomerative_clustering(copy.copy(dots), len(dots), numberOfClusters)
    divisive_clustering(copy.copy(dots), len(dots), numberOfClusters)

global_file.close()