#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#######################################
# Script que permite la generación de mapas
# meteorológicos extremos
# Author: Jorge Mauricio
# Email: jorge.ernesto.mauricio@gmail.com
# Date: Created on Thu Sep 28 08:38:15 2017
# Version: 1.0
#######################################
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata as gd
from time import gmtime, strftime
import time
import os
from time import gmtime, strftime
import ftplib
import shutil
import csv
import math

def main():
	print("Init")
	mapaRoya()

def descargarInfo():
	# datos del servidor
	serverInfo = claves()
	# conexión al server
	ftp = ftplib.FTP(serverInfo.ip)
	# login al servidor
	ftp.login(serverInfo.usr, serverInfo.pwd)
	# arreglo para determinar fecha
	arregloArchivos = []
	arregloFechas = []
	ftp.dir(arregloArchivos.append)
	for archivo in arregloArchivos:
	    arregloArchivo = archivo.split()
	    arregloFechas.append(arregloArchivo[8])
	FECHA_PRONOSTICO = arregloFechas[-1]
	rutaPronostico = "data/{}".format(FECHA_PRONOSTICO)
	ftp.cwd(FECHA_PRONOSTICO)
	# validar la ruta para guardar los datos
	if not os.path.exists(rutaPronostico):
		os.mkdir(rutaPronostico)
	else:
		print("***** Carpeta ya existe")

	# descarga de información
	for i in range(1,6):
		rutaArchivoRemoto = "d{}.txt".format(i)
		rutaArchivoLocal = "{}/d{}.txt".format(rutaPronostico,i)
		lf = open(rutaArchivoLocal, "wb")
		ftp.retrbinary("RETR " + rutaArchivoRemoto, lf.write, 8*1024)
		lf.close()
	ftp.close()
	return FECHA_PRONOSTICO

def generarFechas(f):
	"""
	Función que permite generar una lista de fechas a partir del día actual
	param: f: fecha actual
	"""
	arrayF = []
	tanio, tmes, tdia = f.split('-')
	anio = int(tanio)
	mes = int(tmes)
	dia = int(tdia)

	dirAnio = anio
	dirMes = mes
	dirDia = dia

	# generar lista de fechas
	for i in range(0,5,1):
		if i == 0:
			newDiaString = '{}'.format(dia)
			if len(newDiaString) == 1:
				newDiaString = '0' + newDiaString
			newMesString = '{}'.format(mes)
			if len(newMesString) == 1:
				newMesString = '0' + newMesString
			fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
			arrayF.append(fecha)
		if i > 0:
			dia = dia + 1
			if mes == 2 and anio % 4 == 0:
				diaEnElMes = 29
			elif mes == 2 and anio % 4 != 0:
				diaEnElMes = 28
			elif mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
				diaEnElMes = 31
			elif mes == 4 or mes == 6 or mes == 9 or mes == 11:
				diaEnElMes = 30
			if dia > diaEnElMes:
				mes = mes + 1
				dia = 1
			if mes > 12:
				anio = anio + 1
				mes = 1
			newDiaString = '{}'.format(dia)
			if len(newDiaString) == 1:
				newDiaString = '0' + newDiaString
			newMesString = '{}'.format(mes)
			if len(newMesString) == 1:
				newMesString = '0' + newMesString
			fecha = '{}'.format(anio)+"-"+newMesString+"-"+newDiaString
			arrayF.append(fecha)
	return arrayF


def generarTexto(f, k,vMn, vMx):
	"""
	Función que nos permite generar el texto correspondiente para cada mapa
	param: f: fecha
	param: k: nombre de la columna
	param: vMn: valor mínimo
	param: vMx: valor máximo
	"""
	titulo = ""
	if k == "Rain":
		titulo = "Precipitación acumulada en 24h de {} a {} mm\n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Tmax":
		titulo = "Temperatura máxima en 24h de {} a {} ºC \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Tmin":
		titulo = "Temperatura mínima en 24h de {} a {} ºC \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	elif k == "Windpro":
		titulo = "Viento promedio en 24h de {} a {} km/h \n Pronóstico válido para: {}".format(vMn, vMx, f)
		return titulo
	else:
		pass

def mapaRoya():
	"""
	Función que permite generar los mapas de eventos extremos
	"""
	# ********** fecha pronóstico
	# fechaPronostico = fp
	fechaPronostico = "2018-02-21"
	# fechaPronostico = strftime("%Y-%m-%d")

	# ********** path
	# path server
	# path = "/home/jorge/Documents/work/autoPronosticoSonora"
	# os.chdir(path)
	# path local


	# ********* Lat y Long
	LONG_MAX = -86.1010
	LONG_MIN = -118.2360
	LAT_MAX = 33.5791
	LAT_MIN = 12.37

	# ********** Path
	# Mac : path = "/Users/jorgemauricio/Documents/Research/alermap_roya"
	# Linux : path = "/home/jorge/Documents/Research/alermap_roya"
	path = "/home/jorge/Documents/Research/alermap_roya"
	os.chdir(path)

	# ********** array colores
	# generar fechas mediante función
	arrayFechas = generarFechas(fechaPronostico)

	# leer csv
	dataTemp = "{}/data/{}/d1.txt".format(path,fechaPronostico)
	dataTemp2 = "{}/data/{}/d2.txt".format(path,fechaPronostico)
	dataTemp3 = "{}/data/{}/d3.txt".format(path,fechaPronostico)
	dataTemp4 = "{}/data/{}/d4.txt".format(path,fechaPronostico)
	dataTemp5 = "{}/data/{}/d5.txt".format(path,fechaPronostico)

	data = pd.read_csv(dataTemp)
	data2 = pd.read_csv(dataTemp2)
	data3 = pd.read_csv(dataTemp3)
	data4 = pd.read_csv(dataTemp4)
	data5 = pd.read_csv(dataTemp5)

	data["Tmax1"] = data["Tmax"]
	data["Tmax2"] = data2["Tmax"]
	data["Tmax3"] = data3["Tmax"]
	data["Tmax4"] = data4["Tmax"]
	data["Tmax5"] = data5["Tmax"]

	data["Tmin1"] = data["Tmin"]
	data["Tmin2"] = data2["Tmin"]
	data["Tmin3"] = data3["Tmin"]
	data["Tmin4"] = data4["Tmin"]
	data["Tmin5"] = data5["Tmin"]

	data["Dpoint1"] = data["Dpoint"]
	data["Dpoint2"] = data2["Dpoint"]
	data["Dpoint3"] = data3["Dpoint"]
	data["Dpoint4"] = data4["Dpoint"]
	data["Dpoint5"] = data5["Dpoint"]

	data["Tpro1"] = data["Tpro"]
	data["Tpro2"] = data2["Tpro"]
	data["Tpro3"] = data3["Tpro"]
	data["Tpro4"] = data4["Tpro"]
	data["Tpro5"] = data5["Tpro"]

	data["indice1"] = data.apply(lambda x: generarIndice(x["Tmax1"],x["Tpro1"],x["Tmin1"],x["Dpoint1"]), axis=1).astype(int)
	data["indice2"] = data.apply(lambda x: generarIndice(x["Tmax2"],x["Tpro2"],x["Tmin2"],x["Dpoint2"]), axis=1).astype(int)
	data["indice3"] = data.apply(lambda x: generarIndice(x["Tmax3"],x["Tpro3"],x["Tmin3"],x["Dpoint3"]), axis=1).astype(int)
	data["indice4"] = data.apply(lambda x: generarIndice(x["Tmax4"],x["Tpro4"],x["Tmin4"],x["Dpoint4"]), axis=1).astype(int)
	data["indice5"] = data.apply(lambda x: generarIndice(x["Tmax5"],x["Tpro5"],x["Tmin5"],x["Dpoint5"]), axis=1).astype(int)

	data["indiceTotal"] = data.apply(lambda x: generarIncideTotal(x["indice1"],x["indice2"],x["indice3"],x["indice4"],x["indice5"]), axis=1)

	data["indiceNumero"] = data.apply(lambda x: generarNumero(x["indiceTotal"]), axis=1)

	print(data.head())# comenzar con el proceso
	tiempoInicio = strftime("%Y-%m-%d %H:%M:%S")
	print("Empezar procesamiento tiempo: {}".format(tiempoInicio))

	#obtener valores de x y y
	lons = np.array(data['Long'])
	lats = np.array(data['Lat'])

	#%% set up plot
	plt.clf()

	fig = plt.figure(figsize=(8,4))
	m = Basemap(projection='mill',llcrnrlat=LAT_MIN,urcrnrlat=LAT_MAX,llcrnrlon=LONG_MIN,urcrnrlon=LONG_MAX,resolution='h', area_thresh = 10000)

	# # # # # # # # # #
	# generar lats, lons
	x, y = m(lons, lats)

	# numero de columnas y filas
	numCols = len(x)
	numRows = len(y)

	# generar xi, yi
	xi = np.linspace(x.min(), x.max(), 1000)
	yi = np.linspace(y.min(), y.max(), 1000)

	# generar el meshgrid
	xi, yi = np.meshgrid(xi, yi)

	# generar zi
	z = np.array(data["indiceNumero"])
	zi = gd((x,y), z, (xi,yi), method='cubic')
	#zi = gd((x,y), z, (xi,yi))

	# agregar shape
	m.readshapefile('shapes/Estados', 'Estados')

	# clevs
	clevs = [1,2,3,4,5,6,7,8,9,10]

	# contour plot
	cs = m.contourf(xi,yi,zi, clevs, zorder=25, alpha=0.7, cmap='RdYlGn_r')

	# colorbar
	cbar = m.colorbar(cs, location='right', pad="5%")

	# simbología
	cbar.set_label("")

	# titulo del mapa
	plt.title("Índice de Presencia de Roya")

	tituloTemporalArchivo = "{}/data/{}/{}_Roya.png".format(path,fechaPronostico,arrayFechas[0])

	# crear anotación
	latitudAnotacion = (LAT_MAX + LAT_MIN) / 2
	longitudAnotacion = (LONG_MAX + LONG_MIN) / 2
	plt.annotate('@2018 INIFAP', xy=(longitudAnotacion,latitudAnotacion), xycoords='figure fraction', xytext=(0.45,0.45), color='g')

	# guardar mapa
	plt.savefig(tituloTemporalArchivo, dpi=300)
	print('****** Genereate: {}'.format(tituloTemporalArchivo))

	# finalizar con el proceso
	tiempoFinal = strftime("%Y-%m-%d %H:%M:%S")
	print("Terminar procesamiento tiempo: {}".format(tiempoInicio))


def generarIndice(tmax, tpro, tmin, dpoint):
	tmidnight = tmax - tmin
	if tpro > 25 and tpro < 30 and tmidnight > 15 and tmidnight < 20 and dpoint >5:
		return 1
	else:
		return 0

def generarIncideTotal(i1, i2, i3, i4, i5):
	indiceTotal = "{}{}{}{}{}".format(int(i1),int(i2),int(i3),int(i4),int(i5))
	return indiceTotal

def generarNumero(indiceTotal):
	if indiceTotal == "11111":
		return 10
	elif indiceTotal == "11110":
		return 9
	elif indiceTotal == "01111":
		return 8
	elif indiceTotal == "11100":
		return 7
	elif indiceTotal == "01110":
		return 6
	elif indiceTotal == "00111":
		return 5
	elif indiceTotal == "11000":
		return 4
	elif indiceTotal == "01100":
		return 3
	elif indiceTotal == "00110":
		return 2
	elif indiceTotal == "00011":
		return 1
	else:
		return 0

if __name__ == '__main__':
    main()
