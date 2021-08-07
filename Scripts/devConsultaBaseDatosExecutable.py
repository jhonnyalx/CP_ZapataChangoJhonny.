
#VARIABLES DE ENTRADA ROCKETBOT
query=GetVar('varQuery')
cadena=GetVar('varCadena')
cedula=GetVar('varCedula')

# In[636]:


import devConsultaBaseDatos as datos

SetVar("varResultadoBaseDatos",datos.conectividadConsultaSQL(cadena,query,cedula))