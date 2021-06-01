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
import pandas as pd

from .Andalusian_Population_startup1 import *


class InterfazInstalacion(QDialog):
    def __init__(self, parent=None,lista_url_capas250=[]):
        super().__init__(parent)
        self.lista_url_capas250=lista_url_capas250
        self.salida=False
        self.fase="0/0"

        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle("Instalación de Capas")
        self.main_widget = QtWidgets.QWidget(self)
        #self.main_widget.setFocus()

        VerticalLayout = QVBoxLayout(self.main_widget) 
        self.label=QLabel("Proceso de instalación de las capas del IECA (Instituto de Estadística y Cartografía de Andalucía)\n"
        "Este procedimiento puede llevar unos minutos")
        self.log = QPlainTextEdit(self.main_widget)
        self.log.setReadOnly(True)
        self.LabelEvolucion=QLabel()
        VerticalLayout.addWidget(self.label)
        VerticalLayout.addWidget(self.log)
        VerticalLayout.addWidget(self.LabelEvolucion)

        VerticalLayout.addStretch(1)
        btnLayout = QHBoxLayout()
        self.btn1 = QPushButton("Salir")
        self.btn1.clicked.connect(self.cerrar)
        btnLayout.addWidget(self.btn1)
        btnLayout.addStretch(1)
        self.btn2 = QPushButton("Finalizar") 
        self.btn2.setEnabled(False)
        self.btn2.clicked.connect(self.cerrar)
        btnLayout.addWidget(self.btn2)
        self.btn3 = QPushButton("Comenzar") 
        self.btn3.clicked.connect(self.comenzar)
        btnLayout.addWidget(self.btn3)
        VerticalLayout.addLayout(btnLayout)

        self.setLayout(VerticalLayout)

    def cerrar(self):
        self.close()

    def comenzar(self):
        self.btn1.setEnabled(False)
        self.btn2.setEnabled(False)
        self.btn3.setEnabled(False)

        self.thread = QThread()
        self.worker = Worker(None,self.lista_url_capas250)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.PrintLogMain)
        self.thread.start()

        self.thread.finished.connect(lambda: self.btn1.setEnabled(True))
        self.thread.finished.connect(lambda: self.btn2.setEnabled(True))
        
        

        #self.PrintLog()
        #self.exportar_tablas()

        self.salida=True


    def PrintLogMain(self,msg="",fase="0/0"):
        self.log.appendPlainText(msg)
        self.LabelEvolucion.setText("Capas instaladas: " + fase)
            

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str,str)
    def __init__(self,parent=None,lista_url_capas250=[]):
        super().__init__(parent)
        self.lista_url_capas250=lista_url_capas250
        

    def PrintLog(self,msg):
        self.progress.emit(msg,self.fase)

    def run(self):
        basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
        tipoVersion=getVersion()
        
        self.fase="0/3"
        self.PrintLog("Obteniendo la capa de población (gridpob)")
        nombreAtributos=['grd_floaid','municipio','cmun','pob_tot','pob_m','edad0015','edad65_',
        'esp','ue15','mag','ams','tr_05','tr16_','afil_ss','afil_ss_m','pencinc','demp_pr','demp_pr_m']
        gridpobLayer=AnadirLayerQGIS(url=self.lista_url_capas250[2],nombre="Capa grid de poblacion", tipoCapa="WFS")
        OPTIONS=QgsVectorFileWriter.SaveVectorOptions()
        OPTIONS.driverName="CSV"
        idAtributos=[]
        for nombre in nombreAtributos:
            idAtributos.append(gridpobLayer.fields().indexOf(nombre))
            if idAtributos[-1]==-1:
                idAtributos.pop(-1)
                self.PrintLog("El atributo '"+ nombre + "' de la capa '" + gridpobLayer.name() + "' no se ha encontrado")
        OPTIONS.attributes=idAtributos
        OPTIONS.layerOptions =['SEPARATOR=SEMICOLON']
        OPTIONS.fileEncoding="UTF-8"
        if tipoVersion:
            QgsVectorFileWriter.writeAsVectorFormatV2(gridpobLayer, basepath + "tabla_gridpob.csv",QgsCoordinateTransformContext(),OPTIONS)
            pass
        else:
            QgsVectorFileWriter.writeAsVectorFormat(gridpobLayer, basepath + "tabla_gridpob.csv", 'UTF-8', gridpobLayer.crs(), 'CSV',attributes=idAtributos,layerOptions ='SEPARATOR=SEMICOLON')
        #self.PrintLog("Se ha finalizado la exportacion de la capa de población (gridpob)")

        self.PrintLog("Se están procesando los datos de la capa gridpob")
        df=pd.read_csv(basepath + "tabla_gridpob.csv",sep=";",header=0)
        df['grd_floaid']=df['grd_floaid'].str.replace('.','')
        k=0
        tam=df.shape[0]
        for i in range(tam):
            aux=df['cmun'][i].split(' / ')
            if len(aux)>1:
                aux2=df['municipio'][i].split(' / ')
                df['municipio'][i]=aux2[0]
                df['cmun'][i]=aux[0]
                j=1
                while j<len(aux):
                    df=df.append([df.loc[i]],ignore_index=True)
                    df['municipio'][tam-1+k+j]=aux2[j]
                    df['cmun'][tam-1+k+j]=aux[j]
                    j+=1
                k+=j-1

        df=df[(df[df.columns[3:]].T != -1).any()]
        #df.to_csv(basepath + "tabla_gridpob.csv",sep=";")


        self.fase="1/3"
        self.PrintLog("Obteniendo la capa tipologías constructivas (gridcattpLayer)")
        nombreAtributos=['grd_floaid','ctotal','porc_c011','porc_c012','porc_c02','porc_c03','porc_c04','porc_c05','porc_c08','porc_c09']
        
        gridcattpLayer=AnadirLayerQGIS(url=self.lista_url_capas250[3],nombre="Capa grid de tipologías constructivas", tipoCapa="WFS")
        OPTIONS=QgsVectorFileWriter.SaveVectorOptions()
        OPTIONS.driverName="CSV"
        idAtributos=[]
        for nombre in nombreAtributos:
            idAtributos.append(gridcattpLayer.fields().indexOf(nombre))
            if idAtributos[-1]==-1:
                idAtributos.pop(-1)
                self.PrintLog("El atributo '"+ nombre + "' de la capa '" + gridcattpLayer.name() + "' no se ha encontrado")
        OPTIONS.attributes=idAtributos
        OPTIONS.layerOptions =['SEPARATOR=SEMICOLON']
        OPTIONS.fileEncoding="UTF-8"
        if tipoVersion:
            QgsVectorFileWriter.writeAsVectorFormatV2(gridcattpLayer, basepath + "tabla_gridcattp.csv",QgsCoordinateTransformContext(),OPTIONS)
            #pass
        else:
            QgsVectorFileWriter.writeAsVectorFormat(gridcattpLayer, basepath + "tabla_gridcattp.csv", 'UTF-8', gridcattpLayer.crs(), 'CSV',attributes=idAtributos,layerOptions ='SEPARATOR=SEMICOLON')
        #self.PrintLog("Se ha finalizado la exportacion de la capa tipologías constructivas (gridcattpLayer)")
        
        df_aux=pd.read_csv(basepath + "tabla_gridcattp.csv",sep=";",header=0)
        df_aux=df_aux[(df_aux[df_aux.columns[1:]].T != 0).any()]
        df_aux['grd_floaid']=df_aux['grd_floaid'].str.replace('.','')
        df_res=pd.merge(df, df_aux, how='outer', on='grd_floaid')
        df=df_res
        

        self.fase="2/3"
        self.PrintLog("Obteniendo la capa de mortalidad RMES (gridmortalidad)")
        nombreAtributos=['GRD_FLOAID','RMES_A00','RMES_A45','RMES_A65']
        gridmortalidadLayer=AnadirLayerQGIS(url=self.lista_url_capas250[4],nombre="Capa grid de mortalidad", tipoCapa="WFS")
        OPTIONS=QgsVectorFileWriter.SaveVectorOptions()
        OPTIONS.driverName="CSV"
        idAtributos=[]
        for nombre in nombreAtributos:
            idAtributos.append(gridmortalidadLayer.fields().indexOf(nombre))
            if idAtributos[-1]==-1:
                idAtributos.pop(-1)
                self.PrintLog("El atributo '"+ nombre + "' de la capa '" + gridmortalidadLayer.name() + "' no se ha encontrado")
        OPTIONS.attributes=idAtributos
        OPTIONS.layerOptions =['SEPARATOR=SEMICOLON']
        OPTIONS.fileEncoding="UTF-8"
        if tipoVersion:
            QgsVectorFileWriter.writeAsVectorFormatV2(gridmortalidadLayer, basepath + "tabla_gridmortalidad.csv",QgsCoordinateTransformContext(),OPTIONS)
            #pass
        else:
            QgsVectorFileWriter.writeAsVectorFormat(gridmortalidadLayer, basepath + "tabla_gridmortalidad.csv", 'UTF-8', gridmortalidadLayer.crs(), 'CSV',attributes=idAtributos,layerOptions ='SEPARATOR=SEMICOLON')
        #self.PrintLog("Se ha finalizado la exportacion de la capa de mortalidad RMES (gridmortalidad)")
        df_aux=pd.read_csv(basepath + "tabla_gridmortalidad.csv",sep=";",header=0)
        df_aux=df_aux[(df_aux[df_aux.columns[1:]].T != -1).any()]

        df_aux=df_aux.rename(columns={"GRD_FLOAID":"grd_floaid"})

        df_aux['grd_floaid']=df_aux['grd_floaid'].str.replace('.','')
        df_res=pd.merge(df, df_aux, how='outer', on='grd_floaid')
        df=df_res

        self.fase="3/3"
        """
        self.PrintLog("Obteniendo la capa de tipología de viviendas (gridcatv)")
        nombreAtributos=['grd_floaid','nviv','nviv_i045m2','aant_mediana','nviv_i60a']
        gridcatvLayer=AnadirLayerQGIS(url=self.lista_url_capas250[5],nombre="Capa grid de mortalidad", tipoCapa="WFS")
        OPTIONS=QgsVectorFileWriter.SaveVectorOptions()
        OPTIONS.driverName="CSV"
        idAtributos=[]
        #for i in gridcatvLayer.fields():
        #    print(i.name())
        for nombre in nombreAtributos:
            idAtributos.append(gridcatvLayer.fields().indexOf(nombre))
            if idAtributos[-1]==-1:
                idAtributos.pop(-1)
                self.PrintLog("El atributo '"+ nombre + "' de la capa '" + gridcatvLayer.name() + "' no se ha encontrado")
        #print(idAtributos)
        OPTIONS.attributes=idAtributos
        OPTIONS.layerOptions =['SEPARATOR=SEMICOLON']
        OPTIONS.fileEncoding="UTF-8"
        if tipoVersion:
            QgsVectorFileWriter.writeAsVectorFormatV2(gridcatvLayer, basepath + "tabla_gridcatv.csv",QgsCoordinateTransformContext(),OPTIONS)
            #pass
        else:
            QgsVectorFileWriter.writeAsVectorFormat(gridcatvLayer, basepath + "tabla_gridcatv.csv", 'UTF-8', gridcatvLayer.crs(), 'CSV',attributes=idAtributos,layerOptions ='SEPARATOR=SEMICOLON')
        
        #self.PrintLog("Se ha finalizado la exportacion de la capa de tipología de viviendas (gridcatv)")
        df_aux=pd.read_csv(basepath + "tabla_gridcatv.csv",sep=";",header=0)
        df_aux=df_aux[(df_aux[df_aux.columns[1:]].T != 0).any()]
        df_aux['grd_floaid']=df_aux['grd_floaid'].str.replace('.','')
        #df_aux['grd_floaid'] = df_aux['grd_floaid'].astype(float)
        df_res=pd.merge(df, df_aux, how='outer', on='grd_floaid')
        df=df_res

        self.fase="4/4"
        """
        
        """self.PrintLog("Obteniendo la capa de tipología de viviendas (gridcatv)")
        nombreAtributos=['grd_floaid','nviv_i045m2','aant_mediana','nviv_i60a']
        gridcatvLayer=AnadirLayerQGIS(url=self.lista_url_capas250[5],nombre="Capa grid de mortalidad", tipoCapa="WFS")
        OPTIONS=QgsVectorFileWriter.SaveVectorOptions()
        OPTIONS.driverName="CSV"
        idAtributos=[]
        #for i in gridcatvLayer.fields():
        #    print(i.name())
        for nombre in nombreAtributos:
            idAtributos.append(gridcatvLayer.fields().indexOf(nombre))
            if idAtributos[-1]==-1:
                idAtributos.pop(-1)
                self.PrintLog("El atributo '"+ nombre + "' de la capa '" + gridcatvLayer.name() + "' no se ha encontrado")
        #print(idAtributos)
        OPTIONS.attributes=idAtributos
        OPTIONS.layerOptions =['SEPARATOR=SEMICOLON']
        OPTIONS.fileEncoding="UTF-8"
        if tipoVersion:
            QgsVectorFileWriter.writeAsVectorFormatV2(gridcatvLayer, basepath + "tabla_gridcatv.csv",QgsCoordinateTransformContext(),OPTIONS)
        else:
            QgsVectorFileWriter.writeAsVectorFormat(gridcatvLayer, basepath + "tabla_gridcatv.csv", 'UTF-8', gridcatvLayer.crs(), 'CSV',attributes=idAtributos,layerOptions ='SEPARATOR=SEMICOLON')
        
        #self.PrintLog("Se ha finalizado la exportacion de la capa de tipología de viviendas (gridcatv)")
        df_aux=pd.read_csv(basepath + "tabla_gridcatv.csv",sep=";",header=0)
        df_aux=df_aux[(df_aux[df_aux.columns[1:]].T != 0).any()]
        df_aux['grd_floaid']=df_aux['grd_floaid'].str.replace('.','')
        #df_aux['grd_floaid'] = df_aux['grd_floaid'].astype(float)
        df_res=pd.merge(df, df_aux, how='outer', on='grd_floaid')
        df=df_res"""





        df = df[df['cmun'].notna()]
        os.remove(basepath + 'tabla_gridpob.csv')
        os.remove(basepath + 'tabla_gridcattp.csv')
        os.remove(basepath + 'tabla_gridmortalidad.csv')
        #os.remove(basepath + 'tabla_gridcatv.csv')
        df.to_csv(basepath + "tabla.csv",sep=";",decimal=",")

        self.PrintLog("Se ha finalizado la exportacion de capas")
        #Señal de que ha finalizado
        self.finished.emit()
