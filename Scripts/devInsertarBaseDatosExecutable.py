
#VARIABLES DE ENTRADA ROCKETBOT
cadena=GetVar('varCadena')
varResultadosPep=GetVar('varResultadosPep')
varResultadosNepotismo=GetVar('varResultadosNepotismo')
varResultadosAntecedentes=GetVar('varResultadosAntecedentes')
varResultadosSenescyt=GetVar('varResultadosSenescyt')

# In[636]:


import devInsertarBaseDatos as insertBd


varResultadoBaseDatos=[]

if len(varResultadosPep)>0:
    varResultadoBaseDatos.append(insertBd.insertarBaseDatos(cadena,[x for x in eval(varResultadosPep) if x["error"]=="False"],"Pep001"))
if len(varResultadosSenescyt)>0:
    varResultadoBaseDatos.append(insertBd.insertarBaseDatos(cadena,[x for x in eval(varResultadosSenescyt) if x["error"]=="False"],"Senescyt001"))
if len(varResultadosAntecedentes)>0:
    varResultadoBaseDatos.append(insertBd.insertarBaseDatos(cadena,[x for x in eval(varResultadosAntecedentes) if x["error"]=="False"],"AntecedentesPenales001"))
if len(varResultadosNepotismo)>0:
    varResultadoBaseDatos.append(insertBd.insertarBaseDatos(cadena,[x for x in eval(varResultadosNepotismo) if x["error"]=="False"],"Nepotismo001"))
    
SetVar("varResultadoBaseDatos",varResultadoBaseDatos)