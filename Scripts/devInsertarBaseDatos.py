#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
varResultadosPep=[{'error': 'False', 'mensaje': 'Consulta correcta', 'nombreProceso': 'Obtener informacion de base de datos', 'fecha': '01/08/21 20:51:51', 'path': '', 'resultado': [{'data': [{'PEP_DNI': '1716866916', 'PEP_FECHA_INICIO': '2019-09-30', 'PEP_FECHA_FIN': '2021-04-11', 'INST_DESCRIPCION': 'Director Ejecutivo del Instituto Nacional de Investigación del Transporte', 'INST_ID': 55, 'MESES': 19}], 'cedula': '1716866916'}]}]
varResultadosNepotismo=[{'error': 'False', 'mensaje': 'Consulta correcta', 'nombreProceso': 'Obtener informacion de base de datos', 'fecha': '01/08/21 20:51:50', 'path': '', 'resultado': [{'data': [{'PXE_ID': 11, 'PXE_DNI': '1716866916', 'PXE_NOMBRE': 'LUIS', 'PXE_APELLIDO': 'AGUAS', 'PXE_DIRECCION': 'García Moreno, entre Vélez y Hurtado, Guayaquil, Ecuador', 'EMP_NOMBRE': 'CARMEN ELIZABETH', 'EMP_APELLIDO': 'LUCERO NOVILLO', 'EMP_DNI': '0910142942', 'EMP_FECHA_NACIMIENTO': '1999-08-28', 'EMP_SEXO': 'f', 'EMP_ESTADO': 'a', 'PAR_DESCRIPCION': 'Nieto/a', 'PAR_GRADO': '2'}, {'PXE_ID': 19, 'PXE_DNI': '1716866916', 'PXE_NOMBRE': 'LUIS', 'PXE_APELLIDO': 'AGUAS', 'PXE_DIRECCION': 'García Moreno, entre Vélez y Hurtado, Guayaquil, Ecuador', 'EMP_NOMBRE': 'ELIO ANTONIO', 'EMP_APELLIDO': 'GALARZA GALLARDO', 'EMP_DNI': '0703263228', 'EMP_FECHA_NACIMIENTO': '2006-09-27', 'EMP_SEXO': 'm', 'EMP_ESTADO': 'a', 'PAR_DESCRIPCION': 'Tio/Tia', 'PAR_GRADO': '3'}], 'cedula': '1716866916'}]}]
varResultadosAntecedentes=[{'error': 'False', 'mensaje': 'Consulta correcta', 'nombreProceso': 'Consulta Antecedentes Penales', 'fecha': '01/08/21 20:51:48', 'path': '', 'resultado': [{'data': [{'error': '', 'identity': '1716866916', 'name': 'AGUAS BUCHELI LUIS FERNANDO', 'antecedent': 'NO', 'seclusion': 'NO', 'idr': '31054301', 'type': 'CEDULA DE IDENTIDAD'}], 'cedula': '1716866916'}]}]
varResultadosSenescyt=[{'error': 'False', 'mensaje': 'Consulta correcta', 'nombreProceso': 'Consulta Senescyt', 'fecha': '01/08/21 20:51:41', 'path': '', 'resultado': [{'data': [{'FechaRegistro': '2014-04-09', 'Institucion': 'PONTIFICIA UNIVERSIDAD CATOLICA DEL ECUADOR', 'NumeroRegistro': '1027-14-86046417', 'Observacion': '', 'Reconocido': '', 'Tipo': 'Nacional', 'Titulo': 'MAGISTER EN REDES DE COMUNICACIONES'}, {'FechaRegistro': '2010-10-21', 'Institucion': 'PONTIFICIA UNIVERSIDAD CATOLICA DEL ECUADOR', 'NumeroRegistro': '1027-10-1022854', 'Observacion': '', 'Reconocido': '', 'Tipo': 'Nacional', 'Titulo': 'INGENIERO DE SISTEMAS Y COMPUTACION'}], 'cedula': '1716866916'}]}]
cadena='Driver={SQL Server};Server=DESKTOP-AVPUDFG\SQLEXPRESS;Database=DB_PROCESAMIENTO_RPA;Trusted_Connection=yes;'
bandera='SENESCYT'
'''


# In[89]:


#librerias base de datos
import sqlalchemy as sal
import pyodbc
from sqlalchemy import create_engine
import pandas as pd
import sys
import urllib.parse
import datetime
import json
import traceback


# In[90]:


#generar estructura de respuesta
def crearRespuesta(error,mensaje,informacion,path):
    return {
      "error": error,
      "mensaje": mensaje,
      "nombreProceso":"Obtener informacion de base de datos",
      "fecha": datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"),
      "path":path,
      "resultado": informacion
    }


# In[91]:


def ejecutarProcedimiento(engine,variables):
    
    connection = engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("EXEC PRO_RESULTADOS_RPA ?,?,?,?", variables)
        cursor.close()
        connection.commit()
    finally:
        connection.close()


# In[185]:


def insertarBaseDatos(cadena,data,bandera):
    
    resultado=[]
    
    for info in data:
        fecha=info['fecha']
        dni=info['resultado'][0]['cedula']
        
        try:
            #conectar a bd
            cnn=sal.create_engine('mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(cadena))
            result=info['resultado'][0]['data']
            if len(result)>0:
                for x in result:
                    ejecutarProcedimiento(cnn,[str(x).replace("'",'"'),fecha,bandera,dni])
            
            resultado.append(crearRespuesta("False","Registro exitoso",{"data":[{"proceso":bandera,"registros":len(result)}],"cedula":dni},""))

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                             'line'  : exc_traceback.tb_lineno,
                             'name'    : exc_traceback.tb_frame.f_code.co_name,
                             'type'    : exc_type.__name__,
                             'menssage': str(exc_value).replace('"','').replace("'","")}

            resultado.append(crearRespuesta("True","Revise el detalle",{"data":[traceback_details],"cedula":dni},""))
            
    return resultado

