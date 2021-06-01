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

from .Andalusian_Population_loader import *
from .Andalusian_Population_startup1 import *


class InterfazDeCarga(QDialog):
    def __init__(self,parent,geometria):
        super().__init__()
        self.widget=QWidget()
        self.setWindowTitle('Cargando')
        self.setGeometry(geometria.x()+geometria.width()/4,geometria.y()+geometria.height()/4,300,150)
        self.setFocus();
        dlggLayout = QVBoxLayout(self)
        self.spinner=QtWaitingSpinner(self.widget)
        dlggLayout.addWidget(self.spinner)
        self.setLayout(dlggLayout)
        self.spinner.start()
        #ventana_error(titulo="Importación finalizada",mensaje="Proceso de importación finalizado correctamente")
        
    def cerrar(self):
        self.spinner.stop()
        self.close()

class VentanaError(QDialog):
    def __init__(self,parent=None,titulo="ERROR",mensaje="Se ha producido un error"):
        super().__init__()
        self.ventana_errores = QWidget(self)
        self.setWindowTitle(str(titulo))
        self.setGeometry(500, 400, 300, 150)
        vLayout = QVBoxLayout(self)
        self.ventana_errores.setLayout(vLayout)
        
        texto=QPlainTextEdit (str(mensaje))
        texto.setReadOnly(True)
        texto.setStyleSheet("background-color: transparent;")
        texto.setMaximumHeight(100)
        #texto.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        vLayout.addWidget(texto)
        vLayout.addStretch(1)

        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.accepted.connect(self.aceptar)
        self.buttonBox.rejected.connect(self.cerrar)
        vLayout.addWidget(self.buttonBox, alignment=Qt.AlignRight | Qt.AlignBottom)
        #vLayoutAux.addWidget(self.buttonBox)
        
    def cerrar(self):
        self.close()
    def aceptar(self):
        self.accept()
    

class InterfazMapa(QDialog):
    def __init__(self,parent=None,lista_url_capas250=[],TipoTasa=[]):
        super().__init__()
        self.TipoTasa=TipoTasa
        self.lista_url_capas250=lista_url_capas250

        #self.colores_inv=[0 for i in range(len(TipoTasa))]
        aux=["#00ff00","#009000","#ffff00","#ff9000","#ff0000"]
        self.color_lista=[aux for i in range(len(TipoTasa))]
        aux=[0 for i in range(len(aux))]
        self.condicion_lista=[aux for i in range(len(TipoTasa))]
        self.minimo=[0 for i in range(len(TipoTasa))]
        self.maximo=[1 for i in range(len(TipoTasa))]
        self.idCurrentRow=0


        self.setWindowTitle('Caracterización de la población andaluza')
        self.setGeometry(250, 180, 900, 700)
        self.main_widget = QtWidgets.QWidget(self)
        #self.main_widget.setFocus()
        
        dlgLayout = QVBoxLayout()
        self.main_widget.setLayout(dlgLayout)
        
        #Tabs
        
        
        self.tabwidget = QTabWidget()
        #tabwidget.addTab(inequidadVLayout, "Tab 1")

        nombres_capas=[]
        
        self.inequidadGUI()
        self.configuracionGUI()
        dlgLayout.addWidget(self.tabwidget, 0)
        self.setLayout(dlgLayout)
        
    def inequidadGUI(self):
        inequidadVLayout = QVBoxLayout()
        gb_archivo = QGroupBox("Archivo")    
        verticalLayoutArchivo = QVBoxLayout()
        horzLayout01 = QHBoxLayout()
        #gb_archivo.setAlignment(Qt.AlignHCenter)
        gb_archivo.setStyleSheet('QGroupBox {'
        'border: 2px outset gray;'
        'border-radius: 5px;'
        'margin-top: 0.5em;}'
        'QGroupBox::title {'
        'subcontrol-origin: margin;'
        'left: 10px;'
        'padding: 0 3px;}')
        horzLayout01.addWidget(QLabel('Nombre de la imagen:'))
        self.nombre_fichero=QLineEdit('mapa')
        horzLayout01.addWidget(self.nombre_fichero)
        verticalLayoutArchivo.addLayout(horzLayout01)
        
        horzLayout02 = QHBoxLayout()
        btn_directorio = QPushButton('...')
        btn_directorio.setDefault(False)
        btn_directorio.setAutoDefault(False)
        horzLayout02.addWidget(QLabel('Directorio de la imagen:'))
        self.data_path=QLineEdit(str(QgsProject.instance().readPath("./")))
        horzLayout02.addWidget(self.data_path)
        horzLayout02.addWidget(btn_directorio)
        btn_directorio.clicked.connect(self.obtener_directorio)
        verticalLayoutArchivo.addLayout(horzLayout02)
        gb_archivo.setLayout(verticalLayoutArchivo)
        
        inequidadVLayout.addWidget(gb_archivo)
        
        gb_valor_referencia = QGroupBox("Valor de Referencia")
        gb_valor_referencia.setStyleSheet('QGroupBox {'
        'border: 2px inset gray;'
        'border-radius: 5px;'
        'margin-top: 0.5em;}'
        'QGroupBox::title {'
        'subcontrol-origin: margin;'
        'left: 10px;'
        'padding: 0 3px;}')
        verticalLayoutValorReferencia = QVBoxLayout()
        self.horzLayout2 = QHBoxLayout()
        inequidadVLayout.addWidget(QLabel("")) 
        self.xqlineedit=QLineEdit("294326")
        self.yqlineedit=QLineEdit("4122700")
        self.horzLayout2.addWidget(QLabel('X:'))
        self.horzLayout2.addWidget(self.xqlineedit)
        self.horzLayout2.addStretch(1)
        self.horzLayout2.addWidget(QLabel('Y:'))
        self.horzLayout2.addWidget(self.yqlineedit)
        self.horzLayout2.addStretch(1)
        self.horzLayout2.addWidget(QLabel('Distancia de visualización del mapa(m):'))
        self.bufferVisionLineedit=QLineEdit("1000")
        self.horzLayout2.addWidget(self.bufferVisionLineedit)
        self.horzLayout2.addStretch(20)
        verticalLayoutValorReferencia.addLayout(self.horzLayout2)

        horzLayout03 = QHBoxLayout()
        horzLayout03.addWidget(QLabel("Tipología:")) 
        self.myCombobox_valor_referencia = QComboBox()
        self.myCombobox_valor_referencia.addItem('Andalucia')
        self.myCombobox_valor_referencia.addItem('Provincia')
        self.myCombobox_valor_referencia.addItem('Municipio')
        self.myCombobox_valor_referencia.addItem('Buffer')
        self.myCombobox_valor_referencia.setMinimumContentsLength(15) 
        self.myCombobox_valor_referencia.activated.connect(self.mostrar_tipologia_valor_referencia)
        horzLayout03.addWidget(self.myCombobox_valor_referencia)
        horzLayout03.addStretch(1) 
        self.valorRererenciaQlabel=QLabel('')
        horzLayout03.addWidget(self.valorRererenciaQlabel)
        self.bufferlineedit= QLineEdit('1000')
        self.bufferlineedit.setVisible(False)
        horzLayout03.addWidget(self.bufferlineedit)
        self.myCombobox_valor_referencia_provincia=QComboBox()
        self.myCombobox_valor_referencia_provincia.addItem('PuntoXY')
        self.myCombobox_valor_referencia_provincia.addItem('Almería')
        self.myCombobox_valor_referencia_provincia.addItem('Cádiz')
        self.myCombobox_valor_referencia_provincia.addItem('Córdoba')
        self.myCombobox_valor_referencia_provincia.addItem('Granada')
        self.myCombobox_valor_referencia_provincia.addItem('Huelva')
        self.myCombobox_valor_referencia_provincia.addItem('Jaén')
        self.myCombobox_valor_referencia_provincia.addItem('Málaga')
        self.myCombobox_valor_referencia_provincia.addItem('Sevilla')
        self.myCombobox_valor_referencia_provincia.setMinimumContentsLength(15) 
        self.myCombobox_valor_referencia_provincia.setVisible(False)
        horzLayout03.addWidget(self.myCombobox_valor_referencia_provincia)
        self.municipiolineedit= QLineEdit('PuntoXY')
        
        basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
        df=pd.read_csv(basepath + "tabla.csv",sep=";",decimal=",",header=0)
        # sorting by first name
        df.sort_values("municipio", inplace = True)
          
        # dropping ALL duplicte values
        df.drop_duplicates(subset ="municipio",
                             keep = 'first', inplace = True)
        names=df["municipio"]
        completer = QCompleter(names)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.municipiolineedit.setCompleter(completer)
        
        self.municipiolineedit.setVisible(False)
        horzLayout03.addWidget(self.municipiolineedit)
        horzLayout03.addStretch(20) 
        verticalLayoutValorReferencia.addLayout(horzLayout03)
        
        gb_valor_referencia.setLayout(verticalLayoutValorReferencia)
        
        inequidadVLayout.addWidget(gb_valor_referencia)
        
        inequidadVLayout.addWidget(QLabel("")) 
        titulo_listwidget=QLabel("Tasa 250x250")
        titulo_listwidget.setFont(QFont('Arial', 12))
        VertTasaLayout = QVBoxLayout()
        VertTasaLayout.addWidget(titulo_listwidget)
        self.listwidget_capas250=QListWidget()
        #self.listwidget_capas250.setSelectionMode (QAbstractItemView.ExtendedSelection) # Hold CTRL to select multiple
        
        incr=0
        for malla250 in self.TipoTasa:
            malla250=malla250[1]
            self.listwidget_capas250.addItem(str(incr+1) + ". "+ malla250)#myQListWidgetItem
            self.listwidget_capas250.item(incr).setFont(QFont('Arial', 14))
            incr+=1
        self.listwidget_capas250.setSpacing(5)
        self.listwidget_capas250.itemClicked.connect(self.calculaSimbologia)
        VertTasaLayout.addWidget(self.listwidget_capas250) 
        HorzListLayout = QHBoxLayout()
        HorzListLayout.addLayout(VertTasaLayout)
        
        titulo_listwidget=QLabel("Simbologia")
        titulo_listwidget.setFont(QFont('Arial', 12))
        VertSimbologiaLayout = QVBoxLayout()
        VertSimbologiaLayout.addWidget(titulo_listwidget)
        self.listwidget_capas250_simbologia=QListWidget()
        
        self.listwidget_capas250_simbologia.itemDoubleClicked.connect(self.cambiar_color)
        self.listwidget_capas250_simbologia.itemPressed.connect(self.deshabilitarImportacion)
        self.listwidget_capas250_simbologia.setFixedHeight(300)
        #self.listwidget_capas250.setSelectionMode (QAbstractItemView.ExtendedSelection) # Hold CTRL to select multiple
        self.listwidget_capas250_simbologia.setDragDropMode(QAbstractItemView.InternalMove)
        self.listwidget_capas250_simbologia.setAcceptDrops(True)
        VertSimbologiaLayout.addWidget(self.listwidget_capas250_simbologia) 
        btnLayout1 = QHBoxLayout()
        self.btn1_0 = QPushButton('Eliminar')
        self.btn1_0.clicked.connect(self.eliminarItemSimbologia)
        self.btn1_0.setEnabled(False)
        btnLayout1.addWidget(self.btn1_0)
        btnLayout1.addStretch(1)
        self.btn1_1 = QPushButton('Añadir')
        self.btn1_1.clicked.connect(self.anadirSimbologia)
        self.btn1_1.setEnabled(False)
        btnLayout1.addWidget(self.btn1_1)
        btnLayout1.addStretch(1)
        self.btn1_2 = QPushButton('Invertir colores')
        self.btn1_2.clicked.connect(self.invertirColor)
        self.btn1_2.setEnabled(False)
        btnLayout1.addWidget(self.btn1_2)
        VertSimbologiaLayout.addLayout(btnLayout1)
        
        HorzListLayout.addLayout(VertSimbologiaLayout)
        inequidadVLayout.addLayout(HorzListLayout)
        
        self.checkbox_capa_tasa=QtWidgets.QCheckBox("Mantener la capa de la Tasa despues de la importación")
        inequidadVLayout.addWidget(self.checkbox_capa_tasa) 
        self.checkbox_centro=QtWidgets.QCheckBox("Mantener la capa del punto central despues de la importación")
        inequidadVLayout.addWidget(self.checkbox_centro) 
        self.checkbox_buffer=QtWidgets.QCheckBox("Mantener la capa buffer despues de la importación")
        inequidadVLayout.addWidget(self.checkbox_buffer) 
        inequidadVLayout.addStretch(1)
        btnLayout = QHBoxLayout()
        btn1 = QPushButton('Cerrar')
        btn1.clicked.connect(self.cerrar)
        btnLayout.addWidget(btn1)
        btnLayout.addStretch(1)
        self.btn1_3 = QPushButton('Aplicar')
        self.btn1_3.clicked.connect(self.aplicarCambios)
        self.btn1_3.setEnabled(True)
        self.btn1_3.setDefault(True)
        self.btn1_3.setAutoDefault(True)
        btnLayout.addWidget(self.btn1_3)
        self.btn1_4 = QPushButton('Importar')
        self.btn1_4.clicked.connect(self.ejecutar_inequidad)
        self.btn1_4.setEnabled(False)
        btnLayout.addWidget(self.btn1_4)
        inequidadVLayout.addLayout(btnLayout)
        
        tab1=QWidget()
        tab1.setLayout(inequidadVLayout)
        self.tabwidget.addTab(tab1, "Mapa")
        
        
    def configuracionGUI(self):
        configuracionVLayout = QVBoxLayout()
        
        formLayout = QFormLayout()
        btnLayout = QHBoxLayout()
        
        self.url_ortofoto=QLineEdit(self.lista_url_capas250[0])
        self.url_municipios=QLineEdit(self.lista_url_capas250[1])
        self.url_gridpob=QLineEdit(self.lista_url_capas250[2])
        self.url_gridcatt=QLineEdit(self.lista_url_capas250[3])
        self.url_gridmort=QLineEdit(self.lista_url_capas250[4])
        self.texto_buffer=QLineEdit(self.lista_url_capas250[5])
        
        formLayout.addRow('Fuente capa ortofoto(WMS):', self.url_ortofoto)
        formLayout.addRow('Fuente capa municipios(WFS):', self.url_municipios)
        formLayout.addRow('Fuente capa grid de población(WFS):', self.url_gridpob)
        formLayout.addRow('Fuente capa gridcattp de uso del suelo(WFS):', self.url_gridcatt)
        formLayout.addRow('Fuente capa grid de mortalidad(WFS):', self.url_gridmort)
        formLayout.addRow('Nombre capa buffer:', self.texto_buffer)
        configuracionVLayout.addLayout(formLayout)
        
        btn1 = QPushButton('Cerrar')
        btn1.clicked.connect(self.cerrar)
        btnLayout.addWidget(btn1)
        btnLayout.addStretch(1)
        btn2 = QPushButton('Aplicar')
        btn2.clicked.connect(self.AplicarUrl)
        configuracionVLayout.addStretch(1)
        btnLayout.addWidget(btn2)
        configuracionVLayout.addLayout(btnLayout) 
    
        tab3=QWidget()
        tab3.setLayout(configuracionVLayout)
        self.tabwidget.addTab(tab3, "Configuracion")
    def AplicarUrl(self):
        layer_ortofoto = QgsRasterLayer(self.url_ortofoto.text(), "Capa ortofoto", "WMS")
        layer_municipios = QgsVectorLayer(self.url_municipios.text(), "Capa municipios", "WFS")
        layer_pob = QgsVectorLayer(self.url_gridpob.text(), "Capa pob", "WFS")
        layer_catt = QgsVectorLayer(self.url_gridcatt.text(), "Capa catt", "WFS")
        layer_mort = QgsVectorLayer(self.url_gridmort.text(), "Capa mort", "WFS")
        if not layer_ortofoto.isValid():
            VentanaError(mensaje="La fuente de la capa ortofoto no es válida").exec()
            return
        elif not layer_municipios.isValid():
            VentanaError(mensaje="La fuente de la capa municipios no es válida").exec()
            return
        elif not layer_pob.isValid():
            VentanaError(mensaje="La fuente de la capa grid de población no es válida").exec()
            return
        elif not layer_catt.isValid():
            VentanaError(mensaje="La fuente de la capa gridcattp de uso del suelo no es válida").exec()
            return
        elif not layer_mort.isValid():
            VentanaError(mensaje="La fuente de la capa grid de mortalidad no es válida").exec()
            return
        self.lista_url_capas250[0]=self.url_ortofoto.text()
        self.lista_url_capas250[1]=self.url_municipios.text()
        self.lista_url_capas250[2]=self.url_gridpob.text()
        self.lista_url_capas250[3]=self.url_gridcatt.text()
        self.lista_url_capas250[4]=self.url_gridmort.text()
        self.lista_url_capas250[5]=self.texto_buffer.text()
        
        if (ComprobarCambiosGridTXT(self.lista_url_capas250)):
            if(VentanaError(titulo="Aplicar cambios",mensaje="Para aplicar los cambios, QGIS se cerrará y cuando se ejecute de nuevo el Plugin, "
            "se llevará a cabo la instalación de la/s nueva/s capa/s.\n\n¿Desea continuar?").exec()):
                ActualizarUrl(self.lista_url_capas250)
                EliminarTablaCSV()
                sys.exit()
            else:#Si el usuario no acepta, se sale sin actualizar la Url en el TXT
                return
        ActualizarUrl(self.lista_url_capas250)
    def aplicarCambios(self):
        self.getSimbologia()
        self.muestraSimbologia()
        self.btn1_4.setEnabled(True)
        self.btn1_4.setDefault(True)
        self.btn1_4.setAutoDefault(True)
    def deshabilitarImportacion(self):
        self.btn1_4.setEnabled(False)
        self.btn1_4.setDefault(False)
        self.btn1_4.setAutoDefault(False)
        self.btn1_3.setDefault(True)
        self.btn1_3.setAutoDefault(True)
    def cerrar(self):
        self.close()
    def ejecutar_inequidad(self): #HACER QUE SE VEA POR DELANTE DEL QDIALOG
        #interfazCarga=InterfazDeCarga(None,self.geometry())
        #interfazCarga.exec()
        self.seleccionar_capas_criterio(importar=1)
        #ventana_error(titulo="Importación finalizada",mensaje="Proceso de importación finalizado correctamente")
        #interfazCarga.cerrar()
    def invertirColor(self):
        self.color_lista[self.idCurrentRow].reverse()
        self.muestraSimbologia()
        self.deshabilitarImportacion()
    def obtener_directorio(self):
        dialog = QFileDialog()
        self.data_path.setText(dialog.getExistingDirectory(None, 'Directorio de la imagen',self.data_path.text()))
    def calculaSimbologia(self):
        #Se inicializan las condiciones
        self.idCurrentRow=self.listwidget_capas250.currentRow()
        self.seleccionar_capas_criterio(importar=0)
        if self.listwidget_capas250_simbologia.count()==0:
            for id in range(len(self.color_lista[self.idCurrentRow])):
                self.CreaItemSimbologia(id)
        self.muestraSimbologia()
        self.btn1_0.setEnabled(True)
        self.btn1_1.setEnabled(True)
        self.btn1_2.setEnabled(True)
        self.deshabilitarImportacion()
    def muestraSimbologia(self):
        for incr in range(len(self.color_lista[self.idCurrentRow])):
            self.listwidget_capas250_simbologia.item(incr).widgetText.setText(str(self.condicion_lista[self.idCurrentRow][incr]))
            self.listwidget_capas250_simbologia.item(incr).widgetLabel.setStyleSheet(
                "border: 1px solid black;min-width: 20px;min-height: 20px;background-color: " + str(self.color_lista[self.idCurrentRow][incr]))
        self.actualiza_leyenda()
    def CreaItemSimbologia(self,id):
        myQListWidgetItem=clase_colores(id=id,color=self.color_lista[self.idCurrentRow][id],condicion=self.condicion_lista[self.idCurrentRow][id])
        self.listwidget_capas250_simbologia.addItem(myQListWidgetItem)#myQListWidgetItem
        self.listwidget_capas250_simbologia.setItemWidget(myQListWidgetItem, myQListWidgetItem.widget)
        self.listwidget_capas250_simbologia.item(id).widgetText.editingFinished.connect(self.actualiza_leyenda)
    def eliminarItemSimbologia(self):
        id=self.listwidget_capas250_simbologia.currentRow()
        if id>=0:
            self.listwidget_capas250_simbologia.takeItem(id)
            self.color_lista[self.idCurrentRow].pop(id)
            self.condicion_lista[self.idCurrentRow].pop(id)
        if self.listwidget_capas250_simbologia.count():
            self.actualiza_leyenda()
        self.deshabilitarImportacion()
    def actualiza_leyenda(self):
        for id in range(self.listwidget_capas250_simbologia.count()-1):
            legend1=self.listwidget_capas250_simbologia.item(id).widgetText.text()
            legend2=self.listwidget_capas250_simbologia.item(id+1).widgetText.text()
            texto=str(legend1) + " - " + str(legend2)
            self.listwidget_capas250_simbologia.item(id).widgetLabelLeyenda.setText(texto)
        #Ultimo valor
        self.listwidget_capas250_simbologia.item(id+1).widgetLabelLeyenda.setText(str(legend2)+" - "+str(self.maximo[self.idCurrentRow]))
    def mostrar_tipologia_valor_referencia(self):
        id=self.myCombobox_valor_referencia.currentIndex()
        if (id==0):#Andalucia
            self.valorRererenciaQlabel.setText('')
            self.bufferlineedit.setVisible(False)
            self.myCombobox_valor_referencia_provincia.setVisible(False)
            self.municipiolineedit.setVisible(False)
        elif(id==1):#Provincia
            self.valorRererenciaQlabel.setText('Provincia:')
            self.bufferlineedit.setVisible(False)
            self.myCombobox_valor_referencia_provincia.setVisible(True)
            self.municipiolineedit.setVisible(False)
        elif(id==2):#Municipio
            self.valorRererenciaQlabel.setText('Municipio:')
            self.bufferlineedit.setVisible(False)
            self.myCombobox_valor_referencia_provincia.setVisible(False)
            self.municipiolineedit.setVisible(True)
        elif (id==3):#Buffer
            self.valorRererenciaQlabel.setText('Dist. buffer(m):')
            self.bufferlineedit.setVisible(True)
            self.myCombobox_valor_referencia_provincia.setVisible(False)
            self.municipiolineedit.setVisible(False)
    def obtener_minmax(self,tipo=0,lista=[0,100]):
        CifRed=1 #numero de cifras de redondeo
        if(tipo==0):
            self.minimo[self.idCurrentRow]=lista[0]
            self.maximo[self.idCurrentRow]=lista[1]
            minimo=self.minimo[self.idCurrentRow]
            maximo=self.maximo[self.idCurrentRow]
            incr=(maximo-minimo)/5
            if not(len(self.condicion_lista[self.idCurrentRow])):
                self.condicion_lista[self.idCurrentRow]=[round(float(minimo),CifRed),round(float(minimo+incr),CifRed),round(float(minimo+2*incr),CifRed),
                round(float(minimo+3*incr),CifRed),round(float(minimo+4*incr),CifRed)]
        elif(tipo==1):
            self.minimo[self.idCurrentRow]=round(float(lista[0]),CifRed)
            self.maximo[self.idCurrentRow]=round(float(lista[5]),CifRed)
            self.condicion_lista[self.idCurrentRow]=[round(float(lista[0]),CifRed),round(float(lista[1]),CifRed),round(float(lista[2]),CifRed),
            round(float(lista[3]),CifRed),round(float(lista[4]),CifRed)]
    def getSimbologia(self):
        for id in range(self.listwidget_capas250_simbologia.count()):
            self.color_lista[self.idCurrentRow][id]=str(self.listwidget_capas250_simbologia.item(id).widgetLabel.palette().button().color().name())
            self.condicion_lista[self.idCurrentRow][id]=str(self.listwidget_capas250_simbologia.item(id).widgetText.text())
    def anadirSimbologia(self):
        color="#000000"
        condicion=0
        id=self.listwidget_capas250_simbologia.count()
        self.color_lista[self.idCurrentRow].append(str(color))
        self.condicion_lista[self.idCurrentRow].append(str(condicion))
        self.CreaItemSimbologia(id)
        self.deshabilitarImportacion()
    def cambiar_color(self):
        color_nuevo_inequidad_1=QColorDialog.getColor().name()
        id=self.listwidget_capas250_simbologia.currentRow()
        self.listwidget_capas250_simbologia.item(id).widgetLabel.setStyleSheet("border: 1px solid black;min-width: 20px;min-height: 20px;background-color: " + color_nuevo_inequidad_1)    
        self.deshabilitarImportacion()
    def getcondTasa(self,zLayer):
        condTasa=0
        id=self.myCombobox_valor_referencia.currentIndex()
        if id==0:#Andalucia
            zLayer.setName("Quintiles respecto a Andalucia")
            pass
        elif id==1:#Provincia
            condTasa=self.myCombobox_valor_referencia_provincia.currentText()
            zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
        elif id==2:#Municipio
            condTasa=self.municipiolineedit.text()
            zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            """
            df=df[df['municipio']==condTasa]
            print(df.size)
            if (df.size>0):
                condTasa=float(df.iloc[0]['cmun'])
            """
        elif id==3:#Buffer 
            condTasa=[]
            for f in zLayer.getFeatures():
                    condTasa.append(float(f['grd_floaid'].replace('.','')))
            zLayer.setName("Quintiles  respecto a buffer de " + str(self.bufferVisionLineedit.text()) + "m ")
        
        return condTasa
    def seleccionar_capas_criterio(self,importar=0):
        tipoVersion=getVersion()
        numDecimales=1
        IdTasa=self.listwidget_capas250.currentRow()
        myTargetField=self.TipoTasa[IdTasa][0]
        NombreLeyenda=self.TipoTasa[IdTasa][1]
        tamano_buffer=float(self.bufferVisionLineedit.text())
        x=float(self.xqlineedit.text())
        y=float(self.yqlineedit.text())
        basepath = os.path.dirname(os.path.realpath(__file__)) + "\\"
        df=pd.read_csv(basepath + "tabla.csv",sep=";",decimal=",",header=0)
        if tipoVersion==1:
            tLayer=QgsVectorLayer("Point", "punto", "memory")
            vLayer=QgsVectorLayer("Polygon", "buffer", "memory")
            tLayer.setCrs(QgsCoordinateReferenceSystem(25830))
            vLayer.setCrs(QgsCoordinateReferenceSystem(25830))
        else:
            tLayer=QgsVectorLayer("Point?crs=EPSG:25830", "punto", "memory")
            vLayer=QgsVectorLayer("Polygon?crs=EPSG:25830", "buffer", "memory")
        myField = QgsField( 'id', QVariant.Int )
        vLayer.dataProvider().addAttributes([myField])
        vLayer.updateFields()
        point_centro = QgsGeometry.fromPointXY(QgsPointXY(float(x), float(y)))#yqlineedit.text()
        vpr = tLayer.dataProvider()
        f = QgsFeature()
        f.setGeometry(point_centro)
        vpr.addFeatures([f])
        tLayer.updateExtents()
        tFeats = tLayer.getFeatures()

        for tfeat in tLayer.getFeatures():
            geom = tfeat.geometry()
            buffer = geom.buffer(tamano_buffer, 5)
            feat_vista=tfeat
            tfeat.setGeometry(buffer)
            vLayer.dataProvider().addFeatures([tfeat])


        myTargetField=str(myTargetField)
        NombreLeyenda=str(NombreLeyenda)
        IdRereferencia=self.myCombobox_valor_referencia.currentIndex()
        Layer=AnadirLayerQGIS(url=self.lista_url_capas250[2],nombre="Capa grid de poblacion", tipoCapa="WFS")
        
        if (IdTasa==0):#Poblacion Total
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            poblacion=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    poblacion.append(float(f["pob_tot"]))
                    if all(flag > 0 for flag in [poblacion[-1]]):
                        Tasa.append(float(poblacion[-1]))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            Tasa = df[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=df['pob_tot']
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        elif (IdTasa==1):#Tasa menores 15 años
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            poblacion=[]
            poblacion15=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    poblacion.append(float(f["pob_tot"]))
                    poblacion15.append(float(f["edad0015"]))
                    if all(flag > 0 for flag in [poblacion[-1],poblacion15[-1]+0.1]):
                        Tasa.append(round(float(100*poblacion15[-1]/poblacion[-1]),numDecimales))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            dfReducido=df[(df['edad0015'] >= 0) & (df['pob_tot'] > 0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*(dfReducido['edad0015']/dfReducido['pob_tot'])
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})
            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

            
        elif (IdTasa==2):#Tasa mayores 65 años
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            poblacion=[]
            poblacion65=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    poblacion.append(float(f["pob_tot"]))
                    poblacion65.append(float(f["edad65_"]))
                    if all(flag > 0 for flag in [poblacion[-1],poblacion65[-1]+0.1]):
                        Tasa.append(round(float(100*poblacion65[-1]/poblacion[-1]),numDecimales))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            dfReducido=df[(df['edad65_'] >= 0) & (df['pob_tot'] > 0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*(dfReducido['edad65_']/dfReducido['pob_tot'])
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

            
        elif (IdTasa==3):#Poblacion extranejra
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            den=[]
            num=[]
            aux1=[]
            aux2=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    den.append(float(f['pob_tot']))
                    aux1.append(float(f['esp']))
                    aux2.append(float(f['ue15']))
                    if aux2[-1]>0:
                        num.append(float(den[-1]-aux1[-1]-aux2[-1]))
                    else:
                        num.append(float(den[-1]-aux1[-1]))
                    num.append(float(den[-1]-aux1[-1]-aux2[-1]))
                    if all(flag > 0 for flag in [aux1[-1]+0.1,aux2[-1]+0.1,den[-1],num[-1]+0.1]):
                        Tasa.append(round(float(100*num[-1]/den[-1]),numDecimales))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            dfReducido=df[(df['pob_tot']-df['esp']-df['ue15'] >= 0) & (df['esp'] >= 0) & (df['ue15'] >= 0) & (df['pob_tot'] > 0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*((dfReducido['pob_tot']-dfReducido['esp']-dfReducido['ue15'])/dfReducido['pob_tot'])
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        elif (IdTasa==4):#Poblacion activa
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            den=[]
            num=[]
            aux1=[]
            aux2=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                aux1.append(float(f['edad0015']))
                aux2.append(float(f['edad65_']))
                den.append(float(f['pob_tot']-(aux1[-1]+aux2[-1])))
                num.append(float(f['afil_ss']))
                if all(flag > 0 for flag in [aux1[-1]+0.1,aux2[-1]+0.1,den[-1],num[-1]+0.1]):
                    Tasa.append(round(float(100*num[-1]/den[-1]),numDecimales))
                else:
                    Tasa.append(float(-1))
                
                zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            condTasa=self.getcondTasa(zLayer)
            dfReducido=df[(df['afil_ss'] >= 0) & (df['pob_tot'] > 0) & (f['pob_tot']-(f['edad0015']+f['edad65_'])>0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*((dfReducido['afil_ss'])/(dfReducido['pob_tot']-(dfReducido['edad0015']+dfReducido['edad65_'])))
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})
            Tasa.loc[Tasa[myTargetField] > 100, myTargetField] = 100 #Se satura a 100%

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        elif (IdTasa==5):#Paro registrado
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            den=[]
            num=[]
            aux1=[]
            aux2=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                aux1.append(float(f['edad0015']))
                aux2.append(float(f['edad65_']))
                den.append(float(f['pob_tot']-(aux1[-1]+aux2[-1])))
                num.append(float(f['demp_pr']))
                if all(flag > 0 for flag in [aux1[-1]+0.1,aux2[-1]+0.1,den[-1],num[-1]+0.1]):
                    Tasa.append(round(float(100*num[-1]/den[-1]),numDecimales))
                else:
                    Tasa.append(float(-1))
                
                zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            dfReducido=df[(df['demp_pr'] >= 0) & (df['pob_tot'] > 0) & (f['pob_tot']-(f['edad0015']+f['edad65_'])>0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*((dfReducido['demp_pr'])/(dfReducido['pob_tot']-(dfReducido['edad0015']+dfReducido['edad65_'])))
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        elif (IdTasa==6):#RMEs Total
            Layer2=AnadirLayerQGIS(url=self.lista_url_capas250[4],nombre="Capa grid RMEs", tipoCapa="WFS")
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
                
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer2, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer2=interseccion['OUTPUT']
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            rme=[]
            Tasa=[]
            i=0
            for f in zLayer.getFeatures():
                for f2 in zLayer2.getFeatures():
                    if f2.geometry().equals(f.geometry()):
                        rme.append(float(f2["RMES_A00"]))
                        if all(flag > 0 for flag in [rme[-1]]):
                            Tasa.append(float(rme[-1]))
                        else:
                            Tasa.append(float(-1))
                        
                        zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            Tasa = df[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=df['RMES_A00']
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)
        elif (IdTasa==7):#RMEs 45-65
            Layer2=AnadirLayerQGIS(url=self.lista_url_capas250[4],nombre="Capa grid RMEs", tipoCapa="WFS")
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
                
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer2, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer2=interseccion['OUTPUT']
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            rme=[]
            Tasa=[]
            i=0
            for f in zLayer.getFeatures():
                for f2 in zLayer2.getFeatures():
                    if f2.geometry().equals(f.geometry()):
                        rme.append(float(f2["RMES_A45"]))
                        if all(flag > 0 for flag in [rme[-1]]):
                            Tasa.append(float(rme[-1]))
                        else:
                            Tasa.append(float(-1))
                        
                        zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            Tasa = df[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=df['RMES_A45']
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        
        elif (IdTasa==8):#RMEs >65
            Layer2=AnadirLayerQGIS(url=self.lista_url_capas250[4],nombre="Capa grid RMEs", tipoCapa="WFS")
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
                
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer2, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                zLayer2=interseccion['OUTPUT']
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            rme=[]
            Tasa=[]
            i=0
            for f in zLayer.getFeatures():
                for f2 in zLayer2.getFeatures():
                    if f2.geometry().equals(f.geometry()):
                        rme.append(float(f2["RMES_A65"]))
                        if all(flag > 0 for flag in [rme[-1]]):
                            Tasa.append(float(rme[-1]))
                        else:
                            Tasa.append(float(-1))
                        
                        zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            Tasa = df[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=df['RMES_A65']
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)
        
        
        elif (IdTasa==9):#Tasa mujeres
            if tipoVersion==1:
                interseccion=processing.run("qgis:extractbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'OUTPUT':'TEMPORARY_OUTPUT'})
                
                zLayer=interseccion['OUTPUT']
                zLayer.setName(str(NombreLeyenda))
            else:
                interseccion=processing.run("qgis:selectbylocation", 
                {'INPUT':Layer, 
                'PREDICATE':0,
                'INTERSECT':vLayer,
                'METHOD':0})
                zLayer = interseccion.materialize(QgsFeatureRequest().setFilterFids(interseccion.selectedFeatureIds()))
                zLayer.setName(str(NombreLeyenda))
                
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            poblacion=[]
            poblacionm=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    poblacion.append(float(f["pob_tot"]))
                    poblacionm.append(float(f["pob_m"]))
                    if all(flag > 0 for flag in [poblacion[-1],poblacionm[-1]+0.1]):
                        Tasa.append(round(float(100*poblacionm[-1]/poblacion[-1]),numDecimales))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])

            zLayer.commitChanges()
            zLayer.updateFields()
            
            #A partir de aqui es donde se modifica para cada Tasa
            condTasa=self.getcondTasa(zLayer)
            if condTasa=="PuntoXY":
                condTasa=calcularPuntoXY(Tipo=IdRereferencia,tLayer=tLayer,lista_url_capas250=self.lista_url_capas250)
                if IdRereferencia==1:
                    zLayer.setName("Quintiles respecto a la provincia: " + condTasa)
                elif IdRereferencia==2:
                    zLayer.setName("Quintiles respecto al municipio: " + condTasa)
            dfReducido=df[(df['pob_m'] >= 0) & (df['pob_tot'] > 0)]
            Tasa = dfReducido[['grd_floaid','municipio','cmun']]
            Tasa[myTargetField]=100*(dfReducido['pob_m']/dfReducido['pob_tot'])
            Tasa=Tasa[(Tasa[myTargetField] >= 0)]
            Tasa=Tasa.round({myTargetField:numDecimales})

            (minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo)=calcularValorReferencia(Tipo=IdRereferencia, Tasa=Tasa, condTasa=condTasa)

        """
        elif (IdTasa==3):#muj/hom
            Layer=AnadirLayerQGIS(url=self.lista_url_capas250[2],nombre="Capa grid de poblacion", tipoCapa="WFS")
            #Layer = QgsProject.instance().mapLayersByName("gridpob:gridpob_250")[0]  #gridpob:gridpob_250
            interseccion=processing.run("qgis:extractbylocation", 
            {'INPUT':Layer, 
            'PREDICATE':0,
            'INTERSECT':vLayer,
            'OUTPUT':'TEMPORARY_OUTPUT'})
            
            zLayer=interseccion['OUTPUT']
            zLayer.setName(NombreLeyenda)
            myField = QgsField( myTargetField, QVariant.Double )
            zLayer.dataProvider().addAttributes([myField])
            zLayer.updateFields()
            
            #QgsProject.instance().addMapLayer(zLayer)
            
            prov = zLayer.dataProvider()
            numero_tasa=zLayer.fields().indexOf(myTargetField)
            zLayer.startEditing()

            gidmp=[]
            hombre=[]
            mujer=[]
            Tasa=[]
            for f in zLayer.getFeatures():
                    gidmp.append(int(f["gidmp"]))
                    hombre.append(float(f["pob_h"]))
                    mujer.append(float(f["pob_m"]))
                    if all(flag > 0 for flag in [mujer[-1],hombre[-1]+0.1]):
                        Tasa.append(round(float(mujer[-1]/hombre[-1]),numDecimales))
                    else:
                        Tasa.append(float(-1))
                    
                    zLayer.changeAttributeValue(f.id(), numero_tasa, Tasa[-1])
            zLayer.commitChanges()
            zLayer.updateFields()
            zLayer.updateExtents()
            zFeats = zLayer.getFeatures()

            dict={'gidmp':gidmp, myTargetField:Tasa}
            df=pd.DataFrame(dict)
            df2=df[df[myTargetField] >= 0]
            df2.sort_values("gidmp", inplace = True)
            df2.drop_duplicates(subset ="gidmp",keep = 'first', inplace = True)
            minimo=df2[myTargetField].min()
            percentil_20=df2[myTargetField].quantile(0.2)
            percentil_40=df2[myTargetField].quantile(0.4)
            percentil_60=df2[myTargetField].quantile(0.6)
            percentil_80=df2[myTargetField].quantile(0.8)
            maximo=df2[myTargetField].max()
            """
            

        #id=listwidget_capas250.currentRow()
        if importar==0:
            self.obtener_minmax(tipo=1,lista=[minimo,percentil_20,percentil_40,percentil_60,percentil_80,maximo])
        #listwidget_capas250_simbologia.item(IdTasa).actualiza_condicion()

        if (importar==1):
            #print(df2.describe(include='all') )
            

            myRangeList = []

            #QgsProject.instance().addMapLayer(zLayer)
            graduated_renderer = QgsGraduatedSymbolRenderer()
            lista_cond=self.condicion_lista[self.idCurrentRow]
            max_cond=self.maximo[self.idCurrentRow]
            lista_col=self.color_lista[self.idCurrentRow]
            for id in range(len(self.color_lista[self.idCurrentRow])-1):
                myColour = QColor(str(lista_col[id]))
                mySymbol2 = QgsSymbol.defaultSymbol(zLayer.geometryType())
                mySymbol2.setColor(myColour)
                mySymbol2.setOpacity(0.5)
                if tipoVersion==1:
                    graduated_renderer.addClassRange(QgsRendererRange(QgsClassificationRange(str(lista_cond[id])+' - '+str(lista_cond[id+1]), float(lista_cond[id]), float(lista_cond[id+1])), mySymbol2))
                else:
                    myRange2 = QgsRendererRange(float(lista_cond[id]), float(lista_cond[id+1]), mySymbol2,'Group 1')
                    myRangeList.append(myRange2)
                    #graduated_renderer.addClassRange(QgsRendererRange(float(lista_cond[id]), float(lista_cond[id+1])), mySymbol2,'Group 1')

            
            myColour = QColor(str(lista_col[id+1]))
            mySymbol2 = QgsSymbol.defaultSymbol(zLayer.geometryType())
            mySymbol2.setColor(myColour)
            mySymbol2.setOpacity(0.5)
            if tipoVersion==1:
                graduated_renderer.addClassRange(QgsRendererRange(QgsClassificationRange(str(lista_cond[id+1])+' - '+str(max_cond), float(lista_cond[id+1]), float(max_cond)), mySymbol2))
            else:
                myRange2=QgsRendererRange(float(lista_cond[id+1]), float(max_cond), mySymbol2,'Group 1')
                myRangeList.append(myRange2)
                graduated_renderer = QgsGraduatedSymbolRenderer('', myRangeList)
            
            # create renderer object
            graduated_renderer.setClassAttribute(myTargetField)
            zLayer.setRenderer(graduated_renderer)
            zLayer.triggerRepaint()

            #Se añade el label
            if (tamano_buffer<=2000):#Solo si está a menos de 2Km
                layer_settings  = QgsPalLayerSettings()
                text_format = QgsTextFormat()
                text_format.setFont(QFont("Arial", 6))
                buffer_settings = QgsTextBufferSettings()
                buffer_settings.setEnabled(True)
                buffer_settings.setSize(1)
                buffer_settings.setColor(QColor("white"))
                text_format.setBuffer(buffer_settings)
                layer_settings.setFormat(text_format)
                layer_settings.fieldName = myTargetField
                layer_settings.placement = 1
                layer_settings.enabled = True
                layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
                zLayer.setLabelsEnabled(True)
                zLayer.setLabeling(layer_settings)
                zLayer.triggerRepaint()

            self.importar_inequidad(zLayer,vLayer,tLayer,myTargetField,NombreLeyenda)
    def importar_inequidad(self,zLayer,vLayer,tLayer,TipoAbreviado,TituloLeyenda):#Capa de Tasa, Capa buffer, Capa punto, nombre archivo, titulo leyenda
        tamano_buffer=float(self.bufferVisionLineedit.text())
        borrar_buffer=not(self.checkbox_buffer.isChecked())
        borrar_centro=not(self.checkbox_centro.isChecked())
        borrar_capa_tasa=not(self.checkbox_capa_tasa.isChecked())
        vLayer.setName(self.texto_buffer.text()+ " " +str(tamano_buffer) + "m")
        uLayer=AnadirLayerQGIS(url=self.lista_url_capas250[0],nombre="Ortofoto", tipoCapa="WMS")
        QgsProject.instance().addMapLayer(uLayer)
        lblLayer=AnadirLayerQGIS(url=self.lista_url_capas250[1],nombre="Capa municipios", tipoCapa="WFS")
        QgsProject.instance().addMapLayer(lblLayer)
        AnadirLayerQGIS(url=vLayer,nombre="aux", tipoCapa="WFS",layer=1)
        QgsProject.instance().addMapLayer(vLayer)
        AnadirLayerQGIS(url=zLayer,nombre="aux", tipoCapa="WFS",layer=1)
        QgsProject.instance().addMapLayer(zLayer)
        AnadirLayerQGIS(url=tLayer,nombre="aux", tipoCapa="WFS",layer=1)
        QgsProject.instance().addMapLayer(tLayer)

        symbol = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'red'})
        tLayer.renderer().setSymbol(symbol)
        tLayer.triggerRepaint()
        
        symbol = QgsFillSymbol.createSimple({'name': 'circle', 'width_border' : '0.66', 'style' : 'no'})
        vLayer.renderer().setSymbol(symbol)
        vLayer.triggerRepaint()
        
        wLayername = "buffer_vista"
        wLayer=QgsVectorLayer("Polygon", wLayername, "memory")
        QgsProject.instance().addMapLayer(wLayer)
        myField = QgsField( 'id', QVariant.Double )
        wLayer.dataProvider().addAttributes([myField])
        wLayer.updateFields()
        
        uLayer = QgsProject.instance().mapLayersByName(uLayer.name())[0]
        lblLayer = QgsProject.instance().mapLayersByName(lblLayer.name())[0]
        wLayer.setCrs(uLayer.crs())
        wFeats = wLayer.getFeatures()
        

        symbol = QgsFillSymbol.createSimple({'name': 'square', 'width_border' : '0.66', 'style' : 'no'})
        lblLayer.renderer().setSymbol(symbol)
        layer_settings  = QgsPalLayerSettings()
        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial", 8))
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))
        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)
        layer_settings.fieldName = "nombre"
        layer_settings.placement = 1
        layer_settings.enabled = True
        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        lblLayer.setLabelsEnabled(True)
        lblLayer.setLabeling(layer_settings)
        lblLayer.triggerRepaint()
       
            
        for feat_vista in tLayer.getFeatures():
            geom = feat_vista.geometry()
            dist=float(self.bufferVisionLineedit.text())
            buffer_vista = geom.buffer(dist+0.5*dist, 5)
            feat_vista.setGeometry(buffer_vista)
            wLayer.dataProvider().addFeatures([feat_vista])


        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.renderContext().setDpi(150)
        map = QgsLayoutItemMap(layout)
        map.setRect(QRectF(0, 0, 100, 100))
        map.setExtent(wLayer.extent())
        map.setLayers([tLayer,vLayer,lblLayer,zLayer,uLayer])
        map.setBackgroundColor(QColor(255, 255, 255))
        map.attemptResize(QgsLayoutSize(1753,1240, QgsUnitTypes.LayoutPixels))
        layout.addLayoutItem(map)



        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map)
        legend.setLegendFilterByMapEnabled(True)
        layerTree = QgsLayerTree()
        layers_name = [tLayer.name(),vLayer.name(),zLayer.name()]
        #layers = [i for i in QgsProject().instance().mapLayers().values() if i.name() in layer_names]
        #for l in layers:
        #    layerTree.addLayer(l)
        for l_name in layers_name:
            layerTree.addLayer(QgsProject.instance().mapLayersByName(l_name)[0])

        legend.model().setRootGroup(layerTree)

        legend.setTitle(str(TituloLeyenda))
        legend.setStyleFont(QgsLegendStyle.Title, QFont("Comic Sans MS", 18))
        legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Comic Sans MS", 14))
        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(15, 10, QgsUnitTypes.LayoutPixels))
        legend.setFrameEnabled(True)
        legend.refresh()

        pdf_path = os.path.join(self.data_path.text(), self.nombre_fichero.text() + "_" + str(TipoAbreviado) + '.png')
        exporter = QgsLayoutExporter(layout)
        exporter.exportToImage(pdf_path, QgsLayoutExporter.ImageExportSettings())
        #Borrar documentos
        QgsProject.instance().removeMapLayer(wLayer)
        del wLayer
        if borrar_centro:
            QgsProject.instance().removeMapLayer(tLayer)
            del tLayer
        if borrar_buffer:
            QgsProject.instance().removeMapLayer(vLayer)
            del vLayer
        if borrar_capa_tasa:
            QgsProject.instance().removeMapLayer(zLayer)
            del zLayer

        #Se refresca el mapa
        iface.mapCanvas().refresh()


class clase_lista_malla250(QWidget):
    def __init__(self,parent=None,nombre="default_name",colores_invertidos=0):
        super().__init__()
        del(parent)
        #self.id=listwidget_capas250.currentRow()
        #self.nombre=listwidget_capas250.item(1).text()
        self.nombre=nombre
        
        
        self.widgetLabel = QLabel(self.nombre)
        self.widgetLabel.setFont(QFont('Arial', 10))
        widgetLayout = QHBoxLayout()
        widgetLayout.addWidget(self.widgetLabel)
        widgetLayout.addStretch(1)

        widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(widgetLayout)
        #self.setSizeHint(self.widget_prueba.sizeHint())
        #self.mostrar_item_capa250()
        

class clase_colores(QListWidgetItem):
    def __init__(self, parent=None, id = 0, color = "#000000", condicion = 0):
        super().__init__()
        del(parent)
        
        self.id = id
        self.widget=QWidget()
        self.widgetLabel = QLabel("")
        self.widgetLabel.setFont(QFont('Arial', 10))
        self.widgetLabel.setStyleSheet("border: 1px solid black;min-width: 20px;min-height: 20px;background-color: " + str(color))
        self.widgetText = QLineEdit(str(condicion))
        self.widgetText.setFont(QFont('Arial', 10))
        
        self.widgetLabelLeyenda = QLabel("0-0")
        self.widgetLabelLeyenda.setFont(QFont('Arial', 10))
        widgetLayout = QHBoxLayout()
        widgetLayout.addWidget(self.widgetLabel)
        widgetLayout.addWidget(self.widgetText)
        widgetLayout.addWidget(self.widgetLabelLeyenda)
        widgetLayout.addStretch(1)

        widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.widget.setLayout(widgetLayout)
        self.setSizeHint(self.widget.sizeHint())

    