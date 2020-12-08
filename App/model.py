"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """
import config
import copy
from DISClib.ADT.graph import gr
from DISClib.DataStructures import adjlist as g
from DISClib.ADT import map as m
from DISClib.ADT import indexminpq as iminpq
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.ADT import queue as qe
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import dfs
from DISClib.Algorithms.Graphs import bfs
from math import radians, cos, sin, asin, sqrt 
from scipy import stats as statistics
import datetime
from DISClib.Utils import error 
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'graph': None,
                    'rutas': None,
                    'EstacionesDeSalida': None,
                    'EstacionesDeLlegada': None,
                    'EstacionesDeSalidaEdad': {"0":[],"11":[],"21":[],"31":[],"41":[],"51":[],"61":[]},
                    'EstacionesDeLlegadaEdad': {"0":[],"11":[],"21":[],"31":[],"41":[],"51":[],"61":[]},
                    'EstacionesTotalEdad': {"0":[],"11":[],"21":[],"31":[],"41":[],"51":[],"61":[]},
                    'EstacionesTotal': None,
                    'ListaEstaciones': None
                   }
        analyzer['graph'] = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=True,
                                            size=20000,
                                            comparefunction=compareStations)
        analyzer['rutas'] = m.newMap(numelements=14000,
                                            maptype='PROBING',
                                            comparefunction=compareRutas)
        analyzer['EstacionesDeSalida'] = iminpq.newIndexMinPQ(cmpfunction=compareRutas)
        analyzer['EstacionesDeLlegada'] = iminpq.newIndexMinPQ(cmpfunction=compareRutas)
        analyzer['EstacionesTotal'] = iminpq.newIndexMinPQ(cmpfunction=compareRutas)
        analyzer['ListaEstaciones'] = lt.newList(cmpfunction=compareRecordIds)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# ===========================================
# Funciones para agregar informacion al grafo
# ===========================================

def addTrip(citibike, trip):
    origin = trip['start station id']
    latitudeOrigin = float(trip['start station latitude'])
    longitudeOrigin = float(trip['start station longitude'])
    destination = trip['end station id']
    latitudeDestination = float(trip['end station latitude'])
    longitudeDestination = float(trip['end station longitude'])
    OyD = str(origin) + "-->" + str(destination)
    age = datetime.datetime.today().year - int(trip['birth year'])
    usertype = trip['usertype']
    llaveEdadU = intervaloEdad(age)
    if origin!=destination:
        citibike["EstacionesDeSalidaEdad"][llaveEdadU].append(origin)
        citibike["EstacionesDeLlegadaEdad"][llaveEdadU].append(destination)
        if usertype=="Customer":
            citibike["EstacionesTotalEdad"][llaveEdadU].append(OyD)
        duration = int(trip['tripduration'])
        addStation(citibike, origin, "EstacionesDeSalida", latitudeOrigin, longitudeOrigin)
        addStation(citibike, destination, "EstacionesDeLlegada", latitudeDestination, longitudeDestination)
        addConnection(citibike, origin, destination, duration)

def addStation(citibike, stationid, tipo1, latitude, longitude):
    """
    Adiciona una estación como un vertice del grafo
    """
    if not gr.containsVertex(citibike["graph"], stationid):
            gr.insertVertex(citibike["graph"], stationid)
    if not iminpq.contains(citibike[tipo1],stationid):
            iminpq.insert(citibike[tipo1],stationid,1000000)
    else: 
            val = m.get(citibike[tipo1]['qpMap'], stationid)
            valor = lt.getElement(citibike[tipo1]['elements'], val['value'])["index"]-1
            iminpq.decreaseKey(citibike[tipo1],stationid,valor)
    if not iminpq.contains(citibike["EstacionesTotal"],stationid):
            iminpq.insert(citibike["EstacionesTotal"],stationid,-1000000)
    else:            
            val = m.get(citibike["EstacionesTotal"]['qpMap'], stationid)
            valor = lt.getElement(citibike["EstacionesTotal"]['elements'], val['value'])["index"]+1
            iminpq.insert(citibike["EstacionesTotal"],stationid,valor)
    if citibike['ListaEstaciones']["size"]==0: lt.addLast(citibike['ListaEstaciones'],(stationid,latitude,longitude))
    elif lt.isPresent(citibike['ListaEstaciones'],(stationid,latitude,longitude))==0: lt.addLast(citibike['ListaEstaciones'],(stationid,latitude,longitude))
    return citibike

def addConnection(citibike, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    N=addNRutas(citibike["rutas"],origin,destination)
    edge = gr.getEdge(citibike["graph"], origin, destination)
    if edge is None:
        gr.addEdge(citibike["graph"], origin, destination, duration)
    else:
        EdgeWeightPonderado=edge["weight"]*(N-1)
        promedio = (EdgeWeightPonderado+duration)/N
        edge["weight"]=promedio
    return citibike

def addNRutas(citibike,origin,destination):
    string = str(origin) + "//" + str(destination)
    booleano = m.contains(citibike,string)
    if booleano:
        N = m.get(citibike,string)["value"]+1
        m.put(citibike,string,N)
        return N
    else: 
        m.put(citibike,string,1)
        return 1
# ==============================
# Funciones de consulta
# ==============================

def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['graph'])

def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['graph'])

def numSCC(graph):
    sc = scc.KosarajuSCC(graph["graph"])
    return scc.connectedComponents(sc)

def sameCC(graph, station1, station2):
    sc = scc.KosarajuSCC(graph["graph"])
    return scc.stronglyConnected(sc, station1, station2)

def Top3Salida(graph):
    return Top3(graph["EstacionesDeSalida"])

def Top3Llegada(graph):
    return Top3(graph["EstacionesDeLlegada"])

def Top3Total(graph):
    return Top3(graph["EstacionesTotal"])

def Top3(mapa):
    citibike = copy.deepcopy(mapa)
    top = []
    k = 1
    while k<=4:
        top.append(iminpq.delMin(citibike))
        k += 1
    return top

def CostoMinimoCircular(graph,s1,sF,CE):
    search = djk.Dijkstra(graph["graph"],s1)
    costoAsociado = djk.distTo(search,sF)
    ruta = djk.pathTo(search,sF)
    costoAsociado += (CE + 20*60*ruta["size"])
    iterador = it.newIterator(ruta)
    strRuta = ""
    C = True
    while C:
        DIXX = it.next(iterador)
        if strRuta!="": strRuta += ","
        strRuta += DIXX["vertexA"] + "-->" + DIXX["vertexB"]
        if it.hasNext(iterador)==False:
            strRuta += "," + DIXX["vertexB"] + "-->" + s1
            C = False
    rutacosto = (strRuta,costoAsociado)
    return rutacosto

def RutaEdad(graph, age):
    llaveEdadU = intervaloEdad(age)
    if len(graph["EstacionesDeSalidaEdad"][llaveEdadU])==0: return "No existe una ruta entre las estaciones más frecuentes de llegada y de salida para el rango de edad"
    modaSalida = statistics.mode(graph["EstacionesDeSalidaEdad"][llaveEdadU])[0][0]
    modaLlegada = statistics.mode(graph["EstacionesDeLlegadaEdad"][llaveEdadU])[0][0]
    search = djk.Dijkstra(graph["graph"],modaSalida)
    if djk.hasPathTo(search,modaLlegada):
        ruta = djk.pathTo(search,modaLlegada)
        iterador = it.newIterator(ruta)
        strRuta = ""
        C = True
        while C:
            DIXX = it.next(iterador)
            if strRuta!="": strRuta += ","
            strRuta += DIXX["vertexA"] + "-->" + DIXX["vertexB"]
            if it.hasNext(iterador)==False:
                C = False
        A = "La ruta sugerida es: " + strRuta
        return A
    else: return "No existe una ruta entre las estaciones más frecuentes de llegada y de salida para el rango de edad"

def RutaTuristica(graph,lat1,lon1,lat2,lon2):
    estacionDePartida = buscarEstaciónMásCercana(graph,lat1,lon1)
    estacionDeLlegada = buscarEstaciónMásCercana(graph,lat2,lon2)
    search = djk.Dijkstra(graph["graph"],estacionDePartida)
    retorno = []
    retorno.append("La estación más cercana a la ubicación inicial es la: " + str(estacionDePartida))
    retorno.append("La estación más cercana al sitio turístico que quiere visitar: " + str(estacionDeLlegada))
    if djk.hasPathTo(search,estacionDeLlegada):
        costoAsociado = djk.distTo(search,estacionDeLlegada)
        ruta = djk.pathTo(search,estacionDeLlegada)
        iterador = it.newIterator(ruta)
        strRuta = ""
        C = True
        while C:
            DIXX = it.next(iterador)
            if strRuta!="": strRuta += ","
            strRuta += DIXX["vertexA"] + "-->" + DIXX["vertexB"]
            if it.hasNext(iterador)==False:
                C = False
        retorno.append("La ruta sugerida es: " + strRuta)
        retorno.append("El tiempo estimado de esta ruta en minutos es de: " + str(round(costoAsociado/60)))
    else: retorno.append("No existe una ruta entre las estaciones")
    return retorno

def idEstPublicidad(graph,age):
    llaveEdadU = intervaloEdad(age)
    if len(graph["EstacionesTotalEdad"][llaveEdadU])==0: return "No hay estaciones adyacentes para ese grupo de edad, con suscripción de 3 días"
    modas = []
    maxRep = 0
    retorno = []
    for i in graph["EstacionesTotalEdad"][llaveEdadU]:
        N = 0
        for j in graph["EstacionesTotalEdad"][llaveEdadU]:
            if i == j: N+=1
        if N==maxRep: modas.append(i)
        elif N>maxRep: 
            modas = []
            modas.append(i)
            maxRep = N
    modas = list(dict.fromkeys(modas))
    for i in modas:
        retorno.append(i)
    retorno.append("Cada arco de los anteriores registró " + str(maxRep) + " viajes")
    return retorno

# ==============================
# Funciones Helper
# ==============================

def CandidatasCirculares(graph, station1):
    """
    Retorna caminos de rutas circulares para cierto grafo y su tiempo en minutos
    """
    SCCG = scc.KosarajuSCC(graph["graph"])['idscc']
    SCCL = SCCG["table"]
    SCCs1 = m.get(SCCG,station1)["value"]
    listaEstaciones = lt.newList()
    iterador = it.newIterator(SCCL)
    Centinela = True
    while Centinela:
        dixx = it.next(iterador)
        if dixx["value"]==SCCs1 and dixx["key"]!=station1:
            lt.addLast(listaEstaciones,dixx["key"])
        if not it.hasNext(iterador):
            Centinela = False
    return listaEstaciones

def buscarEstaciónesFinales(graph,s1,LE):
    iterador = it.newIterator(LE)
    finales = lt.newList()
    C = True
    while C:
        llegada = it.next(iterador)
        arco = gr.getEdge(graph["graph"],llegada,s1)
        if arco!=None:
            lt.addLast(finales,{llegada:arco["weight"]})
        if it.hasNext(iterador) == False: C = False
    return finales

def buscarEstacionesBFS(graph,s1,tMAX):
    BFS = bfs.BreadhtFisrtSearch(graph["graph"],s1)["visited"]["table"]
    edgeToN = {}
    search = djk.Dijkstra(graph["graph"],s1)
    N = 1
    K = True
    while K:
        C = True
        iterador = it.newIterator(BFS)
        while C:
            elemento = it.next(iterador)
            if N>1:
                llave = str(N-1)
            if (elemento["key"]!=None and elemento["value"]["distTo"]==N and (djk.distTo(search,elemento["key"])<tMAX*60)) and (N==1 or (elemento["value"]["edgeTo"] in edgeToN[llave])):
                if not str(N) in edgeToN:
                    edgeToN[str(N)]=[]
                edgeToN[str(N)].append((elemento["key"],round(djk.distTo(search,elemento["key"])/60)))
            if not it.hasNext(iterador):
                if not str(N) in edgeToN:
                    K = False
                C = False
        N+=1
    return list(edgeToN.values())

def intervaloEdad(age): 
    if 0<=age<=10: llaveEdadU = "0"
    elif 11<=age<=20: llaveEdadU = "11"
    elif 21<=age<=30: llaveEdadU = "21"
    elif 31<=age<=40: llaveEdadU = "31"
    elif 41<=age<=50: llaveEdadU = "41"
    elif 51<=age<=60: llaveEdadU = "51"
    elif 61<=age: llaveEdadU = "61"
    return llaveEdadU

def distance(lat1, lon1, lat2, lon2): 
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 
    # Haversine formula  
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))  
    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371
    # calculate the result 
    return(c * r) 

def buscarEstaciónMásCercana(graph,lat1,lon1):
    iterador = it.newIterator(graph['ListaEstaciones'])
    Min = 10000.0
    estMasCercana = None
    C = True
    while C:
        tupla = it.next(iterador)
        if distance(lat1,lon1,tupla[1],tupla[2])<Min:
            Min = distance(lat1,lon1,tupla[1],tupla[2])
            estMasCercana = tupla[0]
        if it.hasNext(iterador)==False: C = False
    return estMasCercana

# ==============================
# Funciones de Comparacion
# ==============================

def compareRutas(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compareStations(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1

def compareRecordIds (A, B):
    if A == B:
        return 0
    elif A > B:
        return 1
    return -1