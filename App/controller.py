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
import sys
import os
import config as cf
assert cf
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.DataStructures import listiterator as it
from DISClib.ADT import list as lt
from App import model
import csv
from DISClib.ADT import queue as qe


"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________

def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________

def loadTrips(citibike):
    for filename in os.listdir(cf.data_dir):
        if filename.endswith('.csv'):
            print('Cargando archivo: ' + filename)
            loadServices(citibike, filename)
    return citibike

def loadServices(citibike, tripfile):
    tripfile = cf.data_dir + tripfile
    input_file = csv.DictReader(open(tripfile, encoding="utf-8"),
                                delimiter=",")
    for trip in input_file:
        model.addTrip(citibike, trip)
    return citibike

# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________

def totalStops(analyzer):
    """
    Total de paradas de autobus
    """
    return model.totalStops(analyzer)


def totalConnections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(analyzer)


def f3(analyzer,s1,s2):
    cola = qe.newQueue()
    qe.enqueue(cola, "Hay " + str(model.numSCC(analyzer)) + " clústeres en el grafo")
    if model.sameCC(analyzer,s1,s2)==False:
        qe.enqueue(cola, "Las dos estaciones NO pertenecen al mismo clúster")
    else:
        qe.enqueue(cola, "Las dos estaciones SI pertenecen al mismo clúster")
    return cola

def f4(cont,s1,tMIN,tMAX):
    cola = qe.newQueue()
    qe.enqueue(cola,"Nota: se parte del supuesto de que un turista toma 20 minutos conociendo los alrededores en cada parada.")
    listaCand = model.CandidatasCirculares(cont,s1)
    if lt.isEmpty(listaCand):
        qe.enqueue(cola,"No se encontraron rutas.")
        return cola
    listaFinal = model.buscarEstaciónesFinales(cont,s1,listaCand)
    if lt.isEmpty(listaFinal):
        qe.enqueue(cola,"No se encontraron rutas.")
        return cola
    qe.enqueue(cola,"Se encontraron las siguientes rutas: ")
    iterador = it.newIterator(listaFinal)
    C = True
    while C:
        dixx = it.next(iterador)
        llave = list(dixx.keys())[0]
        valor = list(dixx.values())[0]
        tupla = model.CostoMinimoCircular(cont,s1,llave,valor)
        if (tMIN*60)<tupla[1]<(tMAX*60):
            qe.enqueue(cola,(tupla[0] + " , duración esperada en minutos: " + str(round(tupla[1]/60)) ))
        if not it.hasNext(iterador):
            C = False
    return cola

def f5(cont):
    cola = qe.newQueue()
    Top3Salida = model.Top3Salida(cont)
    Top3Llegada = model.Top3Llegada(cont)
    Top3Total = model.Top3Total(cont)
    qe.enqueue(cola, "Las 3 estaciones principales de llegada (en orden) son: " + Top3Llegada[0] + " " + Top3Llegada[1] + " " + Top3Llegada[2])
    qe.enqueue(cola, "Las 3 estaciones principales de salida (en orden) son: " + Top3Salida[0] + " " + Top3Salida[1] + " " + Top3Salida[2])
    qe.enqueue(cola, "Las 3 estaciones menos usadas en total (en orden) son: " + Top3Total[1] + " " + Top3Total[2] + " " + Top3Total[3])
    return cola

def f6(cont, s1, tMAX):
    cola = qe.newQueue()
    listaDeListasDeTuplas = model.buscarEstacionesBFS(cont,s1,tMAX)
    for i in listaDeListasDeTuplas:
        for j in i:
            qe.enqueue(cola,  s1 + "-->" + str(j[0]) + ". La duración esperada de esta ruta es " + str(j[1]) + " minutos")
    return cola

def f7(cont,age):
    cola = qe.newQueue()
    qe.enqueue(cola,model.RutaEdad(cont,age))
    return cola

def f8(cont,lat1,lon1,lat2,lon2):
    cola = qe.newQueue()
    lista = model.RutaTuristica(cont,lat1,lon1,lat2,lon2)
    for i in lista:
        qe.enqueue(cola,i)
    return cola

def f9(cont,age):
    cola = qe.newQueue()
    qe.enqueue(cola,"Las estaciones adyacentes que más utilizan las personas de este grupo de edad, con suscripción de 3 días son: ")
    retorno = model.idEstPublicidad(cont,age)
    for i in retorno:
        qe.enqueue(cola,i)
    return cola