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
import config
from App import controller
from DISClib.ADT import stack
import timeit
assert config
from DISClib.ADT import queue as qe

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________

recursionLimit = 20000

# ___________________________________________________
#  Funciones para imprimir la inforamación de
#  respuesta.  La vista solo interactua con
#  el controlador.
# ___________________________________________________

def ImprimirEnConsola(cola, DatosAdicionales=None):
    if qe.isEmpty(cola)==False: 
        Centinela = True
        print("-"*100)
        while Centinela==True:
            print("", end=" "*10)
            print("•" + qe.dequeue(cola))
            if qe.isEmpty(cola)==True: Centinela=False
        print("-"*100)
    else: print("No se encontrar peliculas para el criterio")
    if DatosAdicionales!=None:
        if qe.isEmpty(DatosAdicionales)==False:
            CentinelaAdicionales = True
            while CentinelaAdicionales==True:
                dato = qe.dequeue(DatosAdicionales)
                print(str(dato[0])+str(dato[1]))
                if qe.isEmpty(DatosAdicionales)==True: CentinelaAdicionales=False

# ___________________________________________________
#  Menu principal
# ___________________________________________________

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("0- Salir")
    print("1- Crear estructuras de datos")
    print("2- Cargar información de bicicletas en NY")
    print("3- Cantidad de clústeres de viajes (REQ1)")
    print("*******************************************")

def optionOne():
    global cont
    print("\nInicializando....")
    cont = controller.init()

def optionTwo():
    print("\nCargando información de bicicletas en NY ....")
    controller.loadTrips(cont)
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStops(cont)
    print('Numero de vertices: ' + str(numvertex))
    print('Numero de arcos: ' + str(numedges))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    print('El limite de recursion se ajusta a: ' + str(recursionLimit))

def optionThree():
    print("\nCargando información clústeres de viajes")
    controller.f3(cont,s1,s2)
    ImprimirEnConsola(controller.f3(cont,s1,s2))

"""
Menu principal
"""
while True:
    try:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n>')

        if int(inputs) == 0:
            print("\nHasta pronto!")
            break

        if int(inputs) == 1:
            executiontime = timeit.timeit(optionOne, number=1)
            print("Tiempo de ejecución: " + str(executiontime)+ " segundos")

        elif int(inputs) == 2:
            executiontime = timeit.timeit(optionTwo, number=1)
            print("Tiempo de ejecución: " + str(executiontime)+ " segundos")

        elif int(inputs) == 3:
            s1 = input("Por favor ingrese el identificador de la estación 1: ")
            s2 = input("Por favor ingrese el identificador de la estación 2: ")
            executiontime = timeit.timeit(optionThree, number=1)
            print("Tiempo de ejecución: " + str(executiontime) + " segundos")
    except:
        print("\nAlgo ocurrió mal, asegurese que todo esté bien e intente nuevamente: ")
sys.exit(0)