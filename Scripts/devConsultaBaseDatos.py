#!/usr/bin/env python
# coding: utf-8

# In[108]:


'''
cadenaConectividadNepotismo='Driver={SQL Server};Server=DESKTOP-AVPUDFG\SQLEXPRESS;Database=DB_NEPOTISMO;Trusted_Connection=yes;'
cadenaConectividadPep='Driver={SQL Server};Server=DESKTOP-AVPUDFG\SQLEXPRESS;Database=DB_PEPS;Trusted_Connection=yes;'

query="select  PXE_ID,PXE_DNI,PXE_NOMBRE,PXE_APELLIDO, PXE_DIRECCION,EMP_NOMBRE,EMP_APELLIDO,EMP_DNI,EMP_FECHA_NACIMIENTO,EMP_SEXO,EMP_ESTADO,PAR_DESCRIPCION,PAR_GRADO from TBL_PARENTESCO_EMPLEADO PE INNER JOIN TBL_EMPLEADOS E ON E.EMP_ID=PE.EMP_ID INNER JOIN TBL_PARENTESCO P ON P.PAR_ID=PE.PAR_ID WHERE PXE_DNI='***'"

query="select P.PEP_DNI,P.PEP_FECHA_INICIO, P.PEP_FECHA_FIN, I.INST_DESCRIPCION,I.INST_ID, (SELECT DATEDIFF(MONTH, P.PEP_FECHA_INICIO, P.PEP_FECHA_FIN)) AS MESES from TBL_PERSONAS_PEP P INNER JOIN TBL_INSTITUCION I ON I.INST_ID=P.INST_ID WHERE P.PEP_DNI='***'"
conectividadConsultaSQL(cadenaConectividadPep,query,'1718913815')

'''


# In[ ]:


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


# In[169]:


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


# In[175]:


def conectividadConsultaSQL(cadena,query,cedula):
    try:
        query=query.replace("***",cedula)
        #conectar a bd
        cnn=sal.create_engine('mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(cadena))
        result = pd.read_sql_query(query,cnn).to_json(orient="records")
        parsed = eval(json.dumps(json.loads(result)))
        if len(parsed)>0:
            return crearRespuesta("False","Consulta correcta",[{"data":parsed[0],"cedula":cedula}],"")
        else:
            return crearRespuesta("False","Consulta correcta",[{"data":"Sin coincidencia","cedula":cedula}],"")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
                         'line'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'menssage': str(exc_value).replace('"','').replace("'","")}
        
        return crearRespuesta("True","Revise el detalle",[traceback_details],"")

