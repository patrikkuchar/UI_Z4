import random
import math
import time
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image as img
import copy
import drawSvg as draw

##trieda pre vykreslenie dendogramu
class Node:
    def __init__(self, parent, left_node, right_node, value, depth, seq):
        self.parent = parent
        self.left_node = left_node
        self.right_node = right_node
        self.value = value
        self.depth = depth #aby som vedel ako vykreslovať po y-ovej -> každý uzol na vlastnej hĺbke (aby sa neprekrývali)
        self.seq = seq #aby som vedel ako sa pohybovať po x-ovej - nakoniec som nepoužil

##funkcia z uložených grafov vytvorí gif
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

##funkcia zavolá rekurziu, ktorá vykreslí dendogram a následne ho uloží
def draw_dendogram(root_node):
    move_to_node(root_node, -1)
    d.setPixelScale(2)
    d.saveSvg('aglomerative_dendogram.svg')

d = draw.Drawing(200600, 40200, displayInline=False)
dend_position = [10,40190] #pozícia vykreslenia listu
global_x_for_leafs = 10 #x-ova pozícia listu (aby listy mali od seba konšantnu vzdialenosť)

##rekurzívna funkcia, ktorá vykresľuje dendogram
def move_to_node(node, color):
    global dend_position, global_x_for_leafs
    colors = ["#0000ff","#556b2f","#ffff00","#191970","#ff4500","#00bfff","#ff1493","#00ff7f","#000000"]


    if node.value == None: #ak nie je list
        ##vykreslenie 8 farieb
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

        move_to_node(node.left_node, new_color_l) #volanie rekurzie pre ľavé dieťa
        x1 = dend_position[0] #x-ova pozícia, kde sa dostalo ľavé dieťa

        move_to_node(node.right_node, new_color_r) #volanie rekurzie pre pravé dieťa
        x2 = dend_position[0] #x-ova pozícia, kde sa dostalo pravé dieťa

        ##vykreslenie horizontálnej čiary medzi ľavým a pravým dieťaťom
        d.append(draw.Line(x1, dend_position[1], x2, dend_position[1], stroke=colors[color]))

        dend_position[0] -= abs(x1-x2)/2 # prejdenie do stredu tejto čiary
        if node.parent != None: #ak už nie sme pre rootu
            d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], 40190 - node.parent.depth * 2 , stroke=colors[color])) #vykreslenie vertikálnej čiary nodu
            dend_position[1] = 40190 - node.parent.depth*2 #posun y-ovej súradnice tam kde sa vertikálna čiara dostala
        else: #ak je to root
            d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], 0 , stroke="black")) #vykreslenie root do konca obrazovky (spodok)

    else: #list
        dend_position[1] = 40190 #vrch obrazovky
        dend_position[0] = global_x_for_leafs #x-ova pozícia kde má byť list
        global_x_for_leafs += 10 #posun x-ovej pozície pre nasledujúci list

        d.append(draw.Line(dend_position[0], dend_position[1], dend_position[0], dend_position[1] - node.parent.depth*2, stroke=colors[color])) #vykreslenie vertikálnej čiary listu

        dend_position[1] -= node.parent.depth*2 #posun y-ovej súradnice tam, kde sa vertikálna čiara dostala


##funkcia hľadá medoid
def find_medoid(cluster):
    ##vytvorím si zoznam
    lenOfCluster = len(cluster)

    arrayOfSums = np.zeros((lenOfCluster,), dtype=float)

    ##prechádzam hornú trojuholníkovú maticu, pričom zisťujem vzdialenosť bodov podľa indexov a pripočítavam do poľa arrayOfSums
    for A in range(lenOfCluster-1):
        for B in range(A+1, lenOfCluster):
            distance = calculate_distance(cluster[A], cluster[B])
            arrayOfSums[A] += distance
            arrayOfSums[B] += distance

    ##zistím index najmenšieho čísla v poli
    index = np.where(arrayOfSums == np.amin(arrayOfSums))[0][0]

    return cluster[index]

##funkcia prechádza všetky body a pri nich zisťuje vzdialenosť od každého centra klastru a podľa toho, ktorá je najmenšia tak priradí bod k tomu klastru
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

##funkcia spriemeruje súradnice všetkých bodov v parametri a tým získa centroid
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

##nájde index zhluku, ktorý má najvzdialenejší priemer bodov od stredu
def find_biggest_cluster(clusters, centroids):
    biggest = 0
    biggest_index = 0

    for i, cluster in enumerate(clusters):
        avgSize = calculate_avg_len(cluster, centroids[i])
        if avgSize > biggest:
            biggest = avgSize
            biggest_index = i

    return biggest_index

##funkcia vypočíta priemernu vzdialenosť všetkých bodov od centroidu = úspešnosť
def calculate_avg_len(cluster, centroid):
    lenSum = 0
    counter = 0
    for point in cluster:
        lenSum += calculate_distance(point, centroid)
        counter += 1
    return lenSum / counter

##funkcia pomocou pytagorovej vety vypočíta vzdialenosť dvoch bodov
def calculate_distance(point_A, point_B):
    return math.sqrt(math.pow(point_A["x"] - point_B["x"],2) + math.pow(point_A["y"] - point_B["y"],2))

##funkcia prepočíta sekundy na hodiny-minúty-sekundy-miliseknudy
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


def divisive_clustering(Points, k):
    label = "Divízne zhlukovanie, kde stred je centroid; počet zhlukov: "
    clusters = [Points] #jeden klaster, kde sú všetky body
    centroids = [find_centroid(Points)] #nájdenie jedného centroidu
    start_time = time.time()

    show_points_on_graph(clusters, centroids, label + "1", "4_0")

    numOfClusters = 1
    counter = 0
    while numOfClusters < k:
        counter += 1
        numOfClusters += 1

        ## nájdem najväčší klaster a vygenerujem okolo jeho centroidu 2 nové centroidy
        biggestCluster_i = find_biggest_cluster(clusters, centroids)
        offset_x = random.randrange(-5,6)
        offset_y = random.randrange(-5,6)

        x = centroids[biggestCluster_i]["x"]
        y = centroids[biggestCluster_i]["y"]
        ##priradím nové centroidy
        centroids.append({"x" : x + offset_x, "y" : y + offset_y})
        centroids.append({"x" : x - offset_x, "y" : y - offset_y})
        centroids.pop(biggestCluster_i) #odstraním starý centroid

        clusters = points_to_clusters(Points, centroids) #priraddím body k novým centroidom

        show_points_on_graph(clusters, centroids, label + str(numOfClusters), "4_" + str(counter))

        ##v cykle posúvam centroidy - rovnako ako pri k-means centroid
        while True:
            counter += 1
            new_centroids = []
            ##nájdem nový centroid
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

            ##priradím body do klastrov na základe nového centroidu
            centroids = new_centroids
            clusters = points_to_clusters(Points, centroids)
            show_points_on_graph(clusters, centroids, label + str(numOfClusters), "4_" + str(counter))

            # prahova hodnota 6 - aby nebolo zbytočne príliš veľa iterácií
            if biggest < 6:
                break

    end_time = time.time()
    print("Čas vykonávania Divízneho zhlukovania: " + calculate_time(round(end_time - start_time, 4)))


    create_GIF(counter, 4)



def aglomerative_clustering(Points, n, k):
    label = "Aglomeratívne zhlukovanie, kde stred je centroid; počet zhlukov: "
    centroids = Points # každý bod je na začiatku centroidom
    numOfClusters = n # počet klastrov je rovný počtu bodov
    clusters = []
    nodes_array = [] #pre vykreslenie dendogramu
    for i, point in enumerate(Points):
        clusters.append([point]) # vytvorenie klastrov
        nodes_array.append(Node(None, None, None, i, 0, 0)) #vytvorenie bodov v dendograme na hĺbke 1

    start_time = time.time()

    ## vytvorím si maticu
    matrix = np.zeros(numOfClusters*numOfClusters, dtype=int).reshape(numOfClusters,numOfClusters)

    ## vyplním maticu vzdialenosťami klastrov; po diagonale hodnota 15000 (väčšia ako najviac možná dosiahnuteľná)
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
    ## cyklus bude spájať klastre až kým nebudú všetky body v jednom klastri (kvôli dendogramu)
    while numOfClusters > 1:
        counter += 1

        ##nájdenie najmenšiej a jej indexov
        result = np.where(matrix == np.min(matrix))
        ##np.where() niekedy vyhodí viac hodnôt (neprišiel som na to prečo), tak ich musím vyfiltrovať aby som našiel správne hodnoty
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

        numOfClusters -= 1 # po každej iterácií cyklu je o 1 klaster menej

        ##aby sa odstranil väčší (nenastane posun)
        if min_B < min_A:
            min_A, min_B = min_B, min_A

        ##nodes pre vykreslenie dendogramu
        seq = nodes_array[min_A].seq #seq väčšieho dieťaťa sa inkrementuje
        if nodes_array[min_B].seq > seq:
            seq = nodes_array[min_B].seq
        parent_node = Node(None, nodes_array[min_A], nodes_array[min_B],
                           None, counter, seq+1)
        ##odkaz na rodičov
        nodes_array[min_A].parent = parent_node
        nodes_array[min_B].parent = parent_node

        nodes_array.pop(min_B) #odstranenie praveho dieťaťa
        nodes_array[min_A] = parent_node #zmena ľaveho dieťaťa na rodiča

        ##pridelím klasterB ku klastruA a odstraním klasterB
        deleted_cluster = clusters.pop(min_B)
        centroids.pop(min_B)
        for point in deleted_cluster:
            clusters[min_A].append(point)

        ##odstraním stĺpec a riadok B z matice
        matrix = np.delete(matrix, min_B, 0)
        matrix = np.delete(matrix, min_B, 1)

        ##zistím centroid pre A
        centroids[min_A] = find_centroid(clusters[min_A])

        ##upravím maticu v stĺpci a riadku A
        A = min_A
        for B in range(numOfClusters):
            if A == B:
                continue
            distance = calculate_distance(centroids[A], centroids[B])
            matrix[A][B] = distance
            matrix[B][A] = distance

        ## ak je počet klastrov taký ako chceme tak klastre vykreslím
        if numOfClusters == k:
            show_points_on_graph(clusters, centroids, label + str(numOfClusters), "3")

    end_time = time.time()
    print("Čas vykonávania Aglomeratívneho zhlukovania: " + calculate_time(round(end_time-start_time, 4)))

    draw_dendogram(nodes_array[0])


def kMeans_medoid(Points, k, centerPoints):
    label = "k-means, kde stred je medoid; "
    medoids = centerPoints #priradia sa vygenerované medoidy
    clusters = points_to_clusters(Points, medoids) #podľa medoidov sa pridelia body do klastrov
    show_points_on_graph(clusters, medoids, label + "0. iterácia", "2_0")

    start_time = time.time()
    i = 0
    while True:
        i += 1
        #nájdu sa nové medoidy
        new_medoids = []
        for j in range(k):
            if len(clusters[j]) == 0: #ak medoid nemá žiadne body, tak sa jeho pozícia zachová
                new_medoids.append(medoids[j])
                continue

            new_medoid = find_medoid(clusters[j])
            new_medoids.append(new_medoid)

        ##vypočítam si najväčší posun medoidov
        biggest = 0
        for j in range(k):
            distance = calculate_distance(medoids[j], new_medoids[j])
            if distance > biggest:
                biggest = distance

        ## priradím body do klastrov pomocou nových centroidov
        medoids = new_medoids
        clusters = points_to_clusters(Points, medoids)
        show_points_on_graph(clusters, medoids, label + str(i) + ". iterácia", "2_" + str(i))

        ## prahová hodnota 2
        if biggest < 2:
            break

    end_time = time.time()
    print("Čas vykonávania k-means - medoid: " + calculate_time(round(end_time-start_time, 4)))


    create_GIF(i, 2)

def kMeans_centroid(Points, k, centerPoints):
    label = "k-means, kde stred je centroid; "
    centroids = centerPoints #priradia sa vygenerované centroidy
    clusters = points_to_clusters(Points, centroids) #podľa centroidov sa pridelia body do klastrov
    show_points_on_graph(clusters, centroids, label + "0. iterácia", "1_0") #vykreslí sa 0. iterácia


    start_time = time.time()
    i = 0
    while True:
        ## v cykle sa prechádzajú klastre a vypočítavajú sa ich nové centroidy
        i += 1
        new_centroids = []
        for j in range(k):
            new_centroid = find_centroid(clusters[j])
            if new_centroid == None: ## ak centroid nemá priradené žiadne body, tak sa jeho pozícia zachová
                new_centroids.append(centroids[j])
            else:
                new_centroids.append(new_centroid)

        ##vypočítam si najväčší posun centroidov
        biggest = 0
        for j in range(k):
            distance = calculate_distance(centroids[j], new_centroids[j])
            if distance > biggest:
                biggest = distance

        ## priradím body do klastrov pomocou nových centroidov
        centroids = new_centroids
        clusters = points_to_clusters(Points, centroids)
        show_points_on_graph(clusters, centroids, label + str(i) + ". iterácia", "1_" + str(i))

        ##prahova hodnota 2
        if biggest < 2:
            break


    end_time = time.time()
    print("Čas vykonávania k-means - centroid: " + calculate_time(round(end_time-start_time, 4)))


    create_GIF(i, 1)


##funckia vykresluje a ukladá body na grafe
def show_points_on_graph(clusters, clustersCentres, label, saveLabel):
    ##ak nechceme vykresliť tak ukončime funkciu
    if not showGraphs:
        return

    plt.title(label)

    colors = ["#e6194B","#3cb44b","#ffe119","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#bfef45","#fabed4"
              ,"#469990","#dcbeff","#9A6324","#fffac8","#800000","#aaffc3","#808000","#ffd8b1","#000075","#a9a9a9"]


    centres = True
    if len(clustersCentres) == 0:
        centres = False

    ##v cykle sa vytvoria body po celom grafe a pridelia sa do jednotlivých klastrov - farebné ohraničenia klasatrov
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
    ##v cykloch sa pridelia do x-ovych a y-ovych polí body a centra klastrov aby sa mohli vykresliť na grafe
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

    ##v cykle sa prechádzajú klastre a vypočítava sa priemerna vzdialenosť od centra klastra = úspešnosť, pričom sa zapamätáva najväčšia hodnota
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


    plt.savefig("grafy/frame" + saveLabel + ".png")
    plt.show()
    plt.figure()
    plt.clf()

## funkcia vygeneruje n bodov okolo k základných bodov
def generate_dots(numOnStart, numOfAll):
    Points = []

    ## vygenerujeme si k základných bodov
    count = 0
    while count < numOnStart:
        point = {"x" : random.randrange(-5000, 5001), "y" : random.randrange(-5000, 5001)}

        if point not in Points:
            Points.append(point)
            count += 1

    ##vygenerujeme si n bodov okolo k základných bodov - v rádiuse 100 (ak môže byť mimo mapu - x/y rádius sa zmenší
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

    show_points_on_graph([Points], [], "Základny graf", "0") #vykreslenie vygenerovaných bodov

    return Points

##funkcia vyberie k náhodných bodov zo všetkých pre k-means algoritmy, tak aby žiaden z nich nebol rovnaký
def create_centres(all_points, k):
    points = []
    l = len(all_points)
    for i in range(k):
        while True:
            point = all_points[random.randrange(l)]
            if point not in points:
                points.append(point)
                break
    return points

showGraphs = False #či chceme vykreslovať grafy


numberOfClusters = 20 #počet začiatočných bodov pomocou, ktorých sa vygeneruju klastre; určuje taktiež počet klastrov, ktorý chceme mať
dots = generate_dots(numberOfClusters, 20000) #vygenerovanie bodov
centerPoints = create_centres(dots, numberOfClusters) #náhodný výber n centroidov/medoidov - pre K-means zhlukovače

kMeans_centroid(copy.copy(dots), numberOfClusters, centerPoints)
kMeans_medoid(copy.copy(dots), numberOfClusters, centerPoints)
aglomerative_clustering(copy.copy(dots), len(dots), numberOfClusters)
divisive_clustering(copy.copy(dots), numberOfClusters)
