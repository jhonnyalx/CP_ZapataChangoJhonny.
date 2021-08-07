#!/usr/bin/env python
# coding: utf-8

# In[148]:


'''
install library 
pip install python-docx 
pip install tika
pip install --upgrade "ibm-watson>=5.2.2"
pip install --upgrade sqlalchemy -t ./

C:/Users/GENERA/Desktop/tesis/InsumosDesarrollo/DesarrolloRpa/RecepcionArchivos/Iniciales
CFjUgd_IbUnSK1ewGXg4gC49ksE-r8V1_xo9ZrVsLGxY
https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/c14be64b-23f9-4621-bbd8-ffb152ae6e8c
20:687903ca-d1e6-47d7-8814-0fd4e17d48b2
Driver={SQL Server};Server=DESKTOP-AVPUDFG\SQLEXPRESS;Database=DB_PROCESAMIENTO_RPA;Trusted_Connection=yes;
Tecnologia
'''


# In[2]:


import gc 
import docx
import win32com.client
import re
import shutil
import os
import tika
from tika import parser 
import datetime
import math
import json
import traceback
#librerias base de datos
import sqlalchemy as sal
import pyodbc
from sqlalchemy import create_engine
import pandas as pd
import sys
import urllib.parse

#librerias Watson
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions


# In[11]:


#Creacion de estructura de carpetas, por archivo
def estructuraCarpetas(directorio,tipo,area):
    directorios=[]
    nombreArchivo=directorio.split("/")[-1]
    directorioRaiz="/".join(directorio.split("/")[:-2])+"/"+tipo+"/"+area+"/"+datetime.datetime.now().strftime("%d%m%y")  
    os.makedirs(directorioRaiz, exist_ok=True)

    if os.path.isfile(directorioRaiz+"/"+nombreArchivo):
        os.remove(directorioRaiz+"/"+nombreArchivo)
        
    #mover archivo a folder
    shutil.move(directorio,directorioRaiz+"/"+nombreArchivo)


# In[199]:


#leer documeto word
def leerDocumentoWord(directorio):
    doc=docx.Document(directorio)

    data=[reemplazarCaracteresEspeciales(x.text.strip()) for x in doc.paragraphs if reemplazarCaracteresEspeciales(x.text.strip())!=""]
    if len(data)>0:
        return " ".join(data)
    else: 
        return None


# In[200]:


#leer documentos pdf
def leerPdf(directorio):
    informacion = tika.parser.from_file(directorio)
    return reemplazarCaracteresEspeciales(informacion['content'])


# In[201]:


#transformar pdf a word
def transformarPdfWord(directorio):
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.visible = 1
        pdfdoc = directorio
        todocx = directorio.replace("pdf","docx")
        wb1 = word.Documents.Open(pdfdoc)
        wb1.SaveAs(todocx, FileFormat=16)  # file format for docx
        wb1.Close()
        word.Quit()
        return directorio.replace("pdf","docx")
    except Exception as e:
        return e


# In[202]:


#eliminar caracteres especiales y espacios en blanco
def reemplazarCaracteresEspeciales(data):
    return re.sub("^\s+|\s+$|\s+(?=\s)","", data.replace("\n"," ").replace("\t"," ").translate ({ord(c): " " for c in "!#^&*<>?|`~=+✓©'"}).replace('"',''))


# In[203]:


#algoritmo para identificar cedulas
def validarCedula(cedula):
    if len(cedula)==10:
        multip = (2, 1, 2, 1, 2, 1, 2, 1, 2)
        acumulador=0
        for x in range(len(cedula[:-1])):
            
            if int(cedula[:-1][x])*multip[x]>=10:
                acumulador+=int(cedula[:-1][x])*multip[x]-9
            else:
                acumulador+=int(cedula[:-1][x])*multip[x]

        if int(math.ceil(acumulador/10)*10-acumulador)==int(cedula[9]):
            return True
        else:
            return False
    else:
        return False


# In[204]:


#metodo para autentificar watson
def consumerWatson(data,keyWatson,urlServicioWatson,modelWatson):
    authenticator = IAMAuthenticator(keyWatson)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2021-03-25',
    authenticator=authenticator)
    natural_language_understanding.set_service_url(urlServicioWatson)
    
    #analizar texto
    response = natural_language_understanding.analyze(
    text=data,
    features=Features(
        entities=EntitiesOptions(model=modelWatson,emotion=True, sentiment=True)        
    )).get_result()
    
    data=json.loads((json.dumps(response, indent=2)))
    
    #procesar respuesta Watson
    if len(data["entities"])>0:
        #identificar Cedula de ciudadania
        identificacion=[x for x in [x["text"].replace("-","").replace(" ","") for x in data["entities"] if x['type']=="dicDocumentoIdentificacion"] if validarCedula(x)==True]
        habilidades=[x for x in data["entities"] if x["type"]=="dicHabilidadesTecnologia"]
        idiomas=[x for x in data["entities"] if x["type"]=="dicIdiomas"]
        resultado= {"identificacion":"","habilidades":[],"herramientas":[],"idiomas":[],"titulos":[]}
        
        if len(identificacion)>0:
            resultado["identificacion"]=identificacion[0]
        if len(habilidades)>0:
            #agregar registros unicos 
            resultado["habilidades"]=list(dict.fromkeys([x["text"] for x in habilidades]))
        if len(idiomas)>0:
            #agregar registros unicos 
            resultado["idiomas"]=list(dict.fromkeys([x["text"] for x in idiomas]))
        return resultado
    return None


# In[28]:


def ejecutarProcedimiento(engine,variables):
    
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("EXEC PROC_EXTRACCION_NLP ?,?, ?", variables)
        cursor.close()
        connection.commit()
    finally:
        connection.close()


# In[206]:


#generar estructura de respuesta
def crearRespuesta(error,mensaje,informacion,path):
    return {
      "error": error,
      "mensaje": mensaje,
      "nombreProceso":"Obtener informacion de archivo",
      "fecha": datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"),
      "path":path,
      "resultado": informacion
    }


# In[207]:


def transformacion(directorio,keyWatson,urlServicioWatson,modelWatson):
    respuesta=None
    data=None
    
    #verificar archivo en folder
    if os.path.isfile(directorio):
        try:
            
            if directorio.split("/")[-1].split(".")[-1].lower()=="pdf":
                #obtener informacion de pdf
                data=leerPdf(directorio)  

            if directorio.split("/")[-1].split(".")[-1].lower()!="pdf":
                #obtener informacion de WORD
                data=leerDocumentoWord(directorio)  
           
            if len(data)>0 or data!=None:
                #generar respuesta con resultados obtenidos
                dataWatson=consumerWatson(data,keyWatson,urlServicioWatson,modelWatson)
                
                if dataWatson!=None:
                    if dataWatson["identificacion"]!="":
                        respuesta=crearRespuesta("False","Consulta correcta",[dataWatson],directorio) 
                    else:
                        respuesta=crearRespuesta("True","Sin documento de identificacion",[],directorio) 
                else:
                    respuesta=crearRespuesta("True","Sin entidades identificadas por Watson",[],directorio)
                
            else:
                #generar respuesta con resultados obtenidos
                respuesta=crearRespuesta("True","Archivo no existe informacion",[],directorio)
            
              
        except Exception as error:     
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                         'line'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'menssage': str(exc_value).replace('"','').replace("'","")}
            
            respuesta=crearRespuesta("True","Revise el detalle",[traceback_details],directorio)
        
    else:
        respuesta=crearRespuesta("True","Archivo no existe",[],directorio)
    
    
    return respuesta


# In[208]:


def consultarExistencia(cadenaConectividad,resultado):
    
    directorio=resultado["path"]
    
    try:
        #variables
        dni=str(resultado["resultado"][0]["identificacion"])
        habilidades=resultado["resultado"][0]["habilidades"]
        idiomas=resultado["resultado"][0]["idiomas"]
        herramientas=resultado["resultado"][0]["herramientas"]
        titulos=resultado["resultado"][0]["titulos"]
        path=resultado["path"]
        
        #conectar a bd
        cnn=sal.create_engine('mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(cadenaConectividad))

    
        if cnn!=None:
            #verificar existencia de curriculumn
            sql_query = pd.read_sql_query("SELECT count(*) as countCurriculumn FROM TBL_CURRICULUM where CUR_DNI='"+dni+"'", cnn)
            
            if sql_query["countCurriculumn"][0]==0:
                #insertar registro
                cnn.execute("INSERT INTO TBL_CURRICULUM (CUR_DNI,CUR_PATH) VALUES ('"+dni+"','"+path+"')")
            else:
                cnn.execute("UPDATE TBL_CURRICULUM SET CUR_PATH='"+path+"' WHERE CUR_DNI='"+dni+"'")
                
                #insertar items
            if len(habilidades)>0:
                for x in habilidades:
                    ejecutarProcedimiento(cnn,[dni,x.upper(),"habilidades"])                 
            if len(idiomas)>0:
                for x in idiomas:
                    ejecutarProcedimiento(cnn,[dni,x.upper(),"idiomas"])   
            if len(herramientas)>0:
                for x in herramientas:
                    ejecutarProcedimiento(cnn,[dni,x.upper(),"herramientas"])   
            if len(titulos)>0:
                for x in titulos:
                    ejecutarProcedimiento(cnn,[dni,x.upper(),"titulos"])   
                    
        return crearRespuesta("False","Consulta correcta",[{"data":[resultado["resultado"][0]],"cedula":dni}],directorio)
                    
    except Exception as e:             
        exc_type, exc_value, exc_traceback = sys.exc_info()

        traceback_details = {
                         'line'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'menssage': str(exc_value).replace('"','').replace("'","")}
        
        return crearRespuesta("True","Revise el detalle",[{"data":[traceback_details],"cedula":""}],directorio)


# In[213]:


def extraccionNlu(directorio,keyWatson,urlServicioWatson,modelWatson,cadenaConectividad,area):
    resultado=[]
    insercionBd=None

    if os.path.isdir(directorio):
        archivos=os.listdir(directorio)
        for x in archivos:
            if x.split(".")[-1].lower()=="pdf" or x.split(".")[-1].lower()=="docx":
                dataTransformacion=transformacion(directorio+"/"+x,keyWatson,urlServicioWatson,modelWatson)
                #validar resultado
                if eval(dataTransformacion["error"])==False:
                    #asignar folder
                    dataTransformacion["path"]=directorio.replace("Iniciales","Procesado")+"/"+area+"/"+datetime.datetime.now().strftime("%d%m%y")+"/"+x
                    
                    insercionBd=consultarExistencia(cadenaConectividad,dataTransformacion)
                    resultado.append(insercionBd)
                    #Creacion estructura de carpetas ->Procesados
                    estructuraCarpetas(directorio+"/"+x,"Procesado",area)
                else:
                    #asignar folder
                    dataTransformacion["path"]=directorio.replace("Iniciales","NoProcesado")+"/"+area+"/"+datetime.datetime.now().strftime("%d%m%y")+"/"+x
                    
                    resultado.append(dataTransformacion)
                    #Creacion estructura de carpetas ->No procesados
                    estructuraCarpetas(directorio+"/"+x,"NoProcesado",area)
    
    return resultado


# In[ ]:




