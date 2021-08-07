
#VARIABLES DE ENTRADA ROCKETBOT
keyWatson=GetVar('varKeyWatson')
urlServicioWatson=GetVar('varUrlServicioWatson')
modelWatson=GetVar('varModelWatson')
pathDocumento=GetVar('varPathDocumento')
cadenaConexion=GetVar('varCadenaConexion')
area=GetVar('varArea')


# In[636]:


import devTransformacion as transformacion

SetVar("varResultadoExtraccion",transformacion.extraccionNlu(pathDocumento,keyWatson,urlServicioWatson,modelWatson,cadenaConexion,area))