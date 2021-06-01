import math
import time

import os

import processing
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import sys
import os

def getVersion():
    version=Qgis.QGIS_VERSION.split(".")
    if float(version[0])==3 and float(version[1])>=16:
        return 1
    return 0
def AnadirLayerQGIS(url,nombre,tipoCapa,layer=0):
    if (layer==0):
        if (tipoCapa=="WMS"):
            auxLayer = QgsRasterLayer(url, nombre, tipoCapa)
        elif(tipoCapa=="WFS"):
            auxLayer = QgsVectorLayer(url, nombre, tipoCapa)
    else :
        auxLayer=url
        for layer in QgsProject.instance().mapLayers().values():
            if(layer.name()==auxLayer.name()):
                QgsProject.instance().removeMapLayer(layer)
        return -1
            
    for layer in QgsProject.instance().mapLayers().values():
        if(layer.source()==auxLayer.source()):
            QgsProject.instance().removeMapLayer(layer)
            break
    return auxLayer

def LeerUrl():
    basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
    with open(basepath + 'url.txt') as f:
        lines = f.readlines()
        lista_url_capas250=[]
        for url in lines:
            lista_url_capas250.append(url.replace('\n',''))
    return lista_url_capas250
def ActualizarUrl(lista_url_capas250):
    basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
    with open(basepath + 'url.txt','w') as f:
        f.writelines('\n'.join(lista_url_capas250))
def ComprobarCambiosGridTXT(lista_url_capas250):#Devuelve 1 si se ha cambiado la fuente de alguna de las capas grid
    fichero=LeerUrl()
    #len()-1 porque el nombre del buffer, que es el ultimo, no afecta
    # y el range empieza en 2, porque la capa ortofoto y municipios tampoco afectan.
    for i in range(2,len(lista_url_capas250)-1):
    
        if lista_url_capas250[i]!=fichero[i]:
            return 1
    return 0
def EliminarTablaCSV():
    basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
    os.remove(basepath + 'tabla.csv')
def calcularPuntoXY(Tipo,tLayer,lista_url_capas250):
    condTasa="Sevilla"#Default value
    Layer=AnadirLayerQGIS(url=lista_url_capas250[1],nombre="Capa limites municipales", tipoCapa="WFS")
    vLayer=QgsVectorLayer("Polygon", "buffer", "memory")
    vLayer.setCrs(QgsCoordinateReferenceSystem(25830))
    for tfeat in tLayer.getFeatures():
            geom = tfeat.geometry()
            buffer = geom.buffer(1, 5)
            feat_vista=tfeat
            tfeat.setGeometry(buffer)
            vLayer.dataProvider().addFeatures([tfeat])
            
    interseccion=processing.run("qgis:extractbylocation", 
    {'INPUT':Layer, 
    'PREDICATE':0,
    'INTERSECT':vLayer,
    'OUTPUT':'TEMPORARY_OUTPUT'})
                
    zLayer=interseccion['OUTPUT']
    try:
        f=next(zLayer.getFeatures())
        if Tipo==1:
            condTasa=f["provincia"]
        elif Tipo==2:
            condTasa=f["nombre"]
    except:
        print("Error: punto XY fuera de Andalucia")
    return condTasa
def calcularValorReferencia(Tipo, Tasa, condTasa, condicionTabla=[], DatosCondTabla=[]):
    #Se tienen en cuenta solo los valores que cumplen las condiciones impuestas (100<poblacion<400)
    if len(condicionTabla)>0 and len(DatosCondTabla)>0:
        for i in range(len(condicionTabla)):
            Tasa=Tasa[(DatosCondTabla.columns[condicionTabla[i][0]] >= condicionTabla[i][1]) & (DatosCondTabla.columns[condicionTabla[i][0]] <= condicionTabla[i][2])]
        
    if Tipo==0:#Andalucia
        pass
    elif Tipo==1:#Provincia
        if condTasa=="PuntoXY":#Por defecto se escoge Sevilla en caso de que hubiese un problema
            limiteInf=41000
        if condTasa=="Almería":#Almeria
            limiteInf=4000
        elif condTasa=="Cádiz":#Cádiz
            limiteInf=11000
        elif condTasa=="Córdoba":#Córdoba
            limiteInf=14000
        elif condTasa=="Granada":#Granada
            limiteInf=18000
        elif condTasa=="Huelva":#Huelva
            limiteInf=21000
        elif condTasa=="Jaén":#Jaén
            limiteInf=23000
        elif condTasa=="Málaga":#Málaga
            limiteInf=29000
        elif condTasa=="Sevilla":#Sevilla
            limiteInf=41000
        print(limiteInf)
        Tasa=Tasa[(Tasa[Tasa.columns[2]] >= limiteInf) & (Tasa[Tasa.columns[2]] < limiteInf+1000)]
        
    elif Tipo==2:#Municipio
        #Tasa=Tasa[(Tasa[Tasa.columns[1]] == condTasa).any()]
        Tasa=Tasa[Tasa[Tasa.columns[1]] == condTasa]
        
    elif (Tipo==3):#Buffer
        Tasa=Tasa[Tasa[Tasa.columns[0]].isin(condTasa)]
    
    
    #Se eliminar filas duplicadas para sacar los percentiles

    Tasa.sort_values("grd_floaid", inplace = True)
    Tasa.drop_duplicates(subset ="grd_floaid",keep = 'first', inplace = True)
    minimo=Tasa[Tasa.columns[-1]].min()
    percentil_20=Tasa[Tasa.columns[-1]].quantile(0.2)
    percentil_40=Tasa[Tasa.columns[-1]].quantile(0.4)
    percentil_60=Tasa[Tasa.columns[-1]].quantile(0.6)
    percentil_80=Tasa[Tasa.columns[-1]].quantile(0.8)
    maximo=Tasa[Tasa.columns[-1]].max()
    
    
    return (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)
        





#icon = str(os.path.realpath(__file__))
#icon_path = icon.replace("startup.py","icono.png")
#action = QAction('EIS BUFFER 1KM')
#action.triggered.connect(interfaz)
#action.setIcon(QIcon(icon_path))
#iface.addToolBarIcon(action)




