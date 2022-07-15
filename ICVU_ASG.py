import os
import arcpy
from arcpy import env

arcpy.AddMessage("***Correcta importacion de bibliotecas / librerias***")

def ScriptTool(dpa_pob, colegios, origen_etnico, part_ciudadana, tasa_analfabetismo, universidades, comisarias, telecomunicacion, vialidad, vialidad_pavimentada, centros_salud, concentracion_contaminante, erodabilidad,
             farmacias, volcanes, parques_urbanos, residuos, resultados, resultados_finales, pond_viv_ent, pond_sal_ma,pond_con_mov, pond_cond_soc) :
    # código de ejecución del script
    return

# Ejecución del código si el archivo se ha ejecutado pero no se ha importado
if __name__ == '__main__':

#-------------------------------------------------------------------------
# Declaracion de variables
#-------------------------------------------------------------------------
    # 
    dpa_pob = arcpy.GetParameterAsText(0)
    colegios = arcpy.GetParameterAsText(1)
    origen_etnico = arcpy.GetParameterAsText(2)
    part_ciudadana = arcpy.GetParameterAsText(3)
    tasa_analfabetismo = arcpy.GetParameterAsText(4)
    universidades = arcpy.GetParameterAsText(5)
    comisarias = arcpy.GetParameterAsText(6)
    telecomunicacion = arcpy.GetParameterAsText(7)
    vialidad = arcpy.GetParameterAsText(8)
    vialidad_pavimentada = arcpy.GetParameterAsText(9)
    centros_salud = arcpy.GetParameterAsText(10)
    concentracion_contaminante = arcpy.GetParameterAsText(11)
    erodabilidad = arcpy.GetParameterAsText(12)
    farmacias = arcpy.GetParameterAsText(13)
    volcanes = arcpy.GetParameterAsText(14)
    parques_urbanos = arcpy.GetParameterAsText(15)
    residuos = arcpy.GetParameterAsText(16)
    resultados = arcpy.GetParameterAsText(17)
    resultados_finales = arcpy.GetParameterAsText(18)
    pond_viv_ent = arcpy.GetParameterAsText(19)
    pond_sal_ma = arcpy.GetParameterAsText(20)
    pond_con_mov = arcpy.GetParameterAsText(21)
    pond_cond_soc = arcpy.GetParameterAsText(22)

    ScriptTool(dpa_pob, colegios, origen_etnico, part_ciudadana, tasa_analfabetismo, universidades, comisarias, telecomunicacion, 
            vialidad, vialidad_pavimentada, centros_salud, concentracion_contaminante, erodabilidad,farmacias,volcanes, parques_urbanos, residuos, resultados, resultados_finales,pond_viv_ent,pond_sal_ma,pond_con_mov, pond_cond_soc)

#------------------------------------------------------------------------

# Definir entorno
aprx = arcpy.mp.ArcGISProject("CURRENT")
aprxMap = aprx.listMaps()[0]
layers = aprxMap.listLayers()
layers = layers[0:len(layers)-2]

arcpy.AddMessage("***Correcta definición de entorno***")


#Limpiar tabla de contenido, pero mantener mapa base
# for layer in layers:
#   aprxMap.removeLayer(layer) 


#Limpiar tablas
tables = aprxMap.listTables()
for table in tables:
   aprxMap.removeTable(table)

arcpy.AddMessage("***Correcta limpieza de tablas***")


#-------------------------------------------------------------------------
## INDICE DE VIVIENDA Y ENTORNO
#-------------------------------------------------------------------------
arcpy.AddMessage("***Comienza procesado de Familia ÍNDICE DE VIVIENDA Y ENTORNO***")
#indice dependencia 

campo="dependencia"
tipo_campo="FLOAT"

arcpy.management.AddField(dpa_pob, campo, tipo_campo)

parametros="fun(!tramo_uno!, !tramo_dos!, !tramo_tres!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion="""def fun(tramoa, tramob, tramoc):
    dependencia = (tramoa+tramoc)/tramob
    return dependencia"""

arcpy.management.CalculateField(dpa_pob, campo,  parametros, code, funcion, tipo)

# Areas sanas

#Utilizar buffer (Zona de influencia) a los residuos de 0,3KM

out_name_res = "residuos_buffer"
distancia = "0.3 Kilometers"
fc_out = "{}//{}".format(resultados, out_name_res)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.PairwiseBuffer(residuos, fc_out, distancia)




#Creación de un nuevo campo de área en el buffer de residuos para evitar futuras confusiones

campo = "area_residuos"
parametros = "funcion(!Shape_Area!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(ar_res):
    area_res= 1 * ar_res
    return area_res"""
arcpy.management.CalculateField(out_name_res, campo, parametros, code, funcion, tipo)



#Creación de un nuevo campo de área en la división política administrativa para evitar futuras confusiones

campo = "area_comunal"
parametros = "funcion(!Shape_Area!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(ar_com):
    area_com= 1 * ar_com
    return area_com"""
arcpy.management.CalculateField(dpa_pob, campo, parametros, code, funcion, tipo)



#Se necesita saber cuantos metros cuadrados de parques urbanos hay en cada comuna.
#Se hará con el geoprocesamiento "resumir dentro de"


out_name_pc = "parques_comunales"
fc_out = "{}//{}".format(resultados, out_name_pc)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, parques_urbanos, fc_out)




#Como está en kilómetros cuadrados, se debe pasar a metros cuadrados

campo = "area_parque"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(kilometroscuadrados):
    metroscuadrados = kilometroscuadrados * 1000000
    return metroscuadrados"""
arcpy.management.CalculateField(out_name_pc, campo, parametros, code, funcion, tipo)



#Como ya están los datos de áreas verdes, áreas malas y área total por comuna
#Se procede a juntarlas todas en un solo shape con unión espacial


out_name_asym = "Union_areas_sanas_y_malas"
fc_out = "{}//{}".format(resultados, out_name_asym)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)


arcpy.analysis.SpatialJoin(out_name_pc, out_name_res, fc_out)




#Sin embargo, hay que tener cuidado con los valores nulos.
#Hay que transformarlos a 0
# a- residuos


campo = "area_residuos"
parametros = "funcion(!area_residuos!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion (residuos):
    if residuos == None:
        return 0
    else:
        return residuos"""
arcpy.management.CalculateField(out_name_asym, campo, parametros, code, funcion, tipo)




#Lo mismo para los parques

campo = "area_parque"
parametros = "funcion(!area_parque!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion (parques):
    if parques == None:
        return 0
    else:
        return parques"""
arcpy.management.CalculateField(out_name_asym, campo, parametros, code, funcion, tipo)




#Finalmente, se calcula la expresión final de areas sanas
#Lo mismo para los parques

campo = "areas_sanas"
parametros = "funcion(!area_residuos!,!area_parque!,!area_comunal!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion (residuos,parque,comuna):
    sano = (parque-residuos)/comuna
    return sano"""
arcpy.management.CalculateField(out_name_asym, campo, parametros, code, funcion, tipo)



#Finalmente, las áreas se deben estandarizar.
#Adicionalmente, para áreas negativas, se le dará el valor "0"

campo = "areas_sanas"
parametros = "funcion(!areas_sanas!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(sana):
    if sana <= 0:
        return 0
    else:
        area = sana*1000
        return area""" 
arcpy.management.CalculateField(out_name_asym, campo, parametros, code, funcion, tipo)

arcpy.AddMessage("***Familia ÍNDICE DE VIVIENDA Y ENTORNO procesada correctamente***")

#-------------------------------------------------------------------------
## SALUD Y MEDIO AMBIENTE
#-------------------------------------------------------------------------
arcpy.AddMessage("***Comienza procesado de Familia SALUD Y MEDIO AMBIENTE***")
#Cercanias
#Se cuenta la cantidad de farmacias con el geoprocesamiento "resumir dentro de"


out_name_fc = "farmacias_comunales"
fc_out = "{}//{}".format(resultados, out_name_fc)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, farmacias, fc_out)




#Se le cambia el nombre del campo para evitar posibles errores

campo = "cantidad_farmacias"
parametros = "funcion(!Point_Count!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(cantidad):
    far = cantidad * 1
    return far"""
arcpy.management.CalculateField(out_name_fc, campo, parametros, code, funcion, tipo)




#Se cuenta la cantidad de centros de salud con el geoprocesamiento "resumir dentro de"


out_name_fcc = "farmacias_centrosalud_comunales"
fc_out = "{}//{}".format(resultados, out_name_fcc)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(out_name_fc, centros_salud, fc_out)





#Al igual que el anterior, se le cambia el nombre del campo para evitar posibles errores

campo = "cantidad_centros"
parametros = "funcion(!Point_Count_1!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(cantidadcentros):
    cantidad = cantidadcentros * 1
    return cantidad"""
arcpy.management.CalculateField(out_name_fcc, campo, parametros, code, funcion, tipo)





#Finalmente, se calcula el campo "salud"

campo = "salud"
parametros = "funcion(!cantidad_farmacias!,!cantidad_centros!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(farmacias,centros):
    salud = (farmacias+centros)/257
    return salud"""
arcpy.management.CalculateField(out_name_fcc, campo, parametros, code, funcion, tipo)


# Calidad de aire

#Se crea un nuevo campo y además los valores nulos se traspasan a 0

campo = "concentracion"
parametros = "funcion(!prom_contam!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(contaminacion):
    if contaminacion == None:
        return 0
    else:
        return contaminacion
    """
arcpy.management.CalculateField(concentracion_contaminante, campo, parametros, code, funcion, tipo)

# Riesgos

#Se hace una zona de influencia en volcanes de 20Km

out_name_vol = "volcanes_buffer"
distancia = "20 Kilometers"
fc_out = "{}//{}".format(resultados, out_name_vol)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.PairwiseBuffer(volcanes, fc_out, distancia)



#Se hace un "resumir dentro de" para la erodabilidad muy alta y alta


out_name_er = "erosiones_comunales"
fc_out = "{}//{}".format(resultados, out_name_er)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, erodabilidad, fc_out)




#La erosion se pasa de km2 a metros2 

campo = "area_erosion"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(areaerosion):
    metroscuadrados = areaerosion * 1000000
    return metroscuadrados"""
arcpy.management.CalculateField(out_name_er, campo, parametros, code, funcion, tipo)




#Se hace un "resumir dentro de" para los volcanes

out_name_ervol= "erosion_y_volcan_comunales"
fc_out = "{}//{}".format(resultados, out_name_ervol)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(out_name_er, out_name_vol, fc_out)



#Los valores nulos se pasan a 0

campo = "SUM_Area_SQUAREKILOMETERS_1"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS_1!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion (erosion):
    if erosion == None:
        return 0
    else:
        return erosion"""
arcpy.management.CalculateField(out_name_ervol, campo, parametros, code, funcion, tipo)




#Los volcanes se pasan de km2 a metros2

campo = "area_volcan"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS_1!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(areavolcan):
    metroscuadrados = areavolcan * 1000000
    return metroscuadrados"""
arcpy.management.CalculateField(out_name_ervol, campo, parametros, code, funcion, tipo)





#Una vez hecho esto, se suman las areas correspondientes y se divide por el total

campo = "riesgos"
parametros = "funcion(!area_erosion!,!area_volcan!,!area_comunal!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(erosion,volcan,comuna):
    peligro = (erosion+volcan)/comuna
    return peligro"""
arcpy.management.CalculateField(out_name_ervol, campo, parametros, code, funcion, tipo)

arcpy.AddMessage("***Familia SALUD Y MEDIO AMBIENTE procesada correctamente***")


#-------------------------------------------------------------------------
# CONECTIVIDAD Y MOVILIDAD
#-------------------------------------------------------------------------
arcpy.AddMessage("***Comienza procesado de Familia CONECTIVIDAD Y MOVILIDAD***")

#Seguridad
#Se hace un "resumir dentro de" para saber cuantas comisarias hay por comuna

out_name_com = "comisarias_comunales"
fc_out = "{}//{}".format(resultados, out_name_com)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, comisarias, fc_out)



#Se crea un campo con un nombre razonable

campo = "numero_comisarias"
parametros = "funcion(!Point_Count!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(cantidadcom):
    numero = cantidadcom
    return numero""" 
arcpy.management.CalculateField(out_name_com, campo, parametros, code, funcion, tipo)





#Finalmente, se divide el área por comisarias

campo = "cobertura_comisarias"
parametros = "funcion(!area_comunal!,!numero_comisarias!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(comuna,comisarias):
    area = comuna/comisarias
    return area"""
arcpy.management.CalculateField(out_name_com, campo, parametros, code, funcion, tipo)


# Vialidad

#Se aplica un "resumir dentro de" para saber la distancia de las calles por comuna

out_name_vi = "vialidad_comunal"
fc_out = "{}//{}".format(resultados, out_name_vi)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, vialidad_pavimentada, fc_out)



#Se cambia el nombre del campo para facilitar comprensión y se pasa 
#de kilómetros a metros

campo = "largo_vialidad"
parametros = "funcion(!SUM_Length_KILOMETERS!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(largo):
    calles = largo * 1000
    return calles"""
arcpy.management.CalculateField(out_name_vi, campo, parametros, code, funcion, tipo)



#Finalmente, se divide por las calles totales regionales

campo = "red_vial"
parametros = "funcion(!largo_vialidad!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(largo):
    red = largo / 7188522
    return red"""
arcpy.management.CalculateField(out_name_vi, campo, parametros, code, funcion, tipo)

#Buena señal de conexion

#Utilizar buffer (Zona de influencia) a la red de telecomunicaciones de 0,3 KM

out_name_tel= "telecomunicacion_buffer"
distancia = "0.3 Kilometers"
fc_out = "{}//{}".format(resultados, out_name_tel)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.PairwiseBuffer(telecomunicacion, fc_out, distancia)



#Se hace un resumir dentro de para saber los metros cuadrados 


out_name_telcom= "telecomunicacion_comunal"
fc_out = "{}//{}".format(resultados, out_name_telcom)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, out_name_tel, fc_out)



#Se pasan de km cuadrado a metro cuadrado

campo = "area_telecomunicacion"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(kilometroscuadrados):
    metroscuadrados = kilometroscuadrados * 1000000
    return metroscuadrados"""
arcpy.management.CalculateField(out_name_telcom, campo, parametros, code, funcion, tipo)





#Finalmente, se aplica la formula de area telecomunicacion/area total

campo = "conexion"
parametros = "funcion(!area_comunal!,!area_telecomunicacion!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(comuna,telecom):
    zona = telecom/comuna
    return zona"""
arcpy.management.CalculateField(out_name_telcom, campo, parametros, code, funcion, tipo)

arcpy.AddMessage("***Familia CONECTIVIDAD Y MOVILIDAD procesada correctamente***")


#-------------------------------------------------------------------------
## CONDICIÓN SOCIO-CULTURAL
#-------------------------------------------------------------------------
arcpy.AddMessage("***Comienza procesado de Familia CONDICIÓN SOCIO-CULTURAL***")

# Tasa de analfabetismo

campo = "tasa_analfabetos"
parametros = "funcion(!t_analf_a!,!t_analf_b!,!t_analf_c!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(primeraño,segundoaño,terceraño):
    tasaprom = (primeraño+segundoaño+terceraño)/3
    return tasaprom"""
arcpy.management.CalculateField(tasa_analfabetismo, campo, parametros, code, funcion, tipo)

#Instituciones

#Hacer área de influencia de 1,2km para los colegios

out_name_col= "colegios_buffer"
distancia = "1.2 Kilometers"
fc_out = "{}//{}".format(resultados, out_name_col)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.PairwiseBuffer(colegios, fc_out, distancia)



#Hacer área de influencia de 5km para universidades

out_name_uni = "universidades_buffer"
distancia = "5 Kilometers"
fc_out = "{}//{}".format(resultados, out_name_uni)

if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.PairwiseBuffer(universidades, fc_out, distancia)



#Se cuenta el área de colegios con el geoprocesamiento "resumir dentro de"


out_name_colcom = "colegios_comunales"
fc_out = "{}//{}".format(resultados, out_name_colcom)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(dpa_pob, out_name_col, fc_out)





#Para no tener conflictos futuros, se genera un nuevo campo
#y se pasa a metros cuadrados (colegio)

campo = "area_colegios"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(area_col):
    area = area_col * 100000
    return area""" 
arcpy.management.CalculateField(out_name_colcom, campo, parametros, code, funcion, tipo)





#Se cuenta el área de universidades con el geoprocesamiento "resumir dentro de"


out_name_cyu = "colegios_y_universidades_comunales"
fc_out = "{}//{}".format(resultados, out_name_cyu)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.SummarizeWithin(out_name_colcom, out_name_uni, fc_out)






#Se deben hacer 0 los campos nulos de las universidades

campo = "SUM_Area_SQUAREKILOMETERS_1"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS_1!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(universidades):
    if universidades == None:
        return 0
    else:
        return universidades""" 
arcpy.management.CalculateField(out_name_cyu, campo, parametros, code, funcion, tipo)




#Para no tener conflictos futuros, se genera un nuevo campo
#y se pasa a metros cuadrados (universidades)

campo = "area_universidades"
parametros = "funcion(!SUM_Area_SQUAREKILOMETERS_1!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(area_uni):
    areauni = area_uni * 100000
    return areauni""" 
arcpy.management.CalculateField(out_name_cyu, campo, parametros, code, funcion, tipo)





#Finalmente, se calcula lo solicitado 
#(area influencia colegios + universidades)/total comunal.
#Se le llamará "instituciones"

campo = "instituciones"
parametros = "funcion(!area_comunal!,!area_colegios!,!area_universidades!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(comuna,colegios,universidades):
    areafinal = (universidades+colegios)/comuna
    return areafinal"""
arcpy.management.CalculateField(out_name_cyu, campo, parametros, code, funcion, tipo)

#Tasa de participacion 

#Se crea un nuevo campo de tasa de participacion

campo = "tasa_participacion"
parametros = "funcion(!part!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(parti):
    par = parti * 1
    return par
    """
arcpy.management.CalculateField(part_ciudadana, campo, parametros, code, funcion, tipo)


# Origen étnico

#Se debe intersectar el origen étnico con el shape de población
inp_pol = "'4- Condiciones socio-culturales\Origen étnico' #;'5-Base división política administrativa\División Político Administrativa y Población' #"
out_name_iet = "interseccion_etnica"
fc_out = "{}//{}".format(resultados, out_name_iet)


if arcpy.Exists (fc_out):
    arcpy.Delete_management (fc_out)
    
arcpy.analysis.Intersect(inp_pol,fc_out)




#Se calcula la tasa de origen étnico

campo = "tasa_etnia"
parametros = "funcion(!T_POB!,!Total!)"
code = "PYTHON3"
tipo = "DOUBLE"
funcion = """def funcion(poblacion,etnia):
    tasa = etnia/poblacion
    return tasa"""
arcpy.management.CalculateField(out_name_iet, campo, parametros, code, funcion, tipo)

arcpy.AddMessage("***Familia CONDICIÓN SOCIO-CULTURAL procesada correctamente***")


#-------------------------------------------------------------------------
## Proceso de estandarización
#-------------------------------------------------------------------------

arcpy.AddMessage("***Comienza el proceso de estandarización***")

# VIVIENDA Y ENTORNO
#Se estandariza el campo areas_sanas

variable = "areas_sanas variable_areas_sanas"
metodo = "MIN-MAX"
rango_inicial = "0"
rango_final = "1"

arcpy.management.StandardizeField(out_name_asym, variable, metodo, rango_inicial, rango_final)

# SALUD Y MEDIOAMBIENTE

#Se estandariza el campo salud

variable = "salud variable_salud"


arcpy.management.StandardizeField(out_name_fcc, variable, metodo, rango_inicial, rango_final)


#Se estandariza el campo contaminacion

variable = "concentracion variable_contaminacion"


arcpy.management.StandardizeField(concentracion_contaminante, variable, metodo, rango_inicial, rango_final)


#Se estandariza el campo riesgos

variable = "riesgos variable_riesgos"


arcpy.management.StandardizeField(out_name_ervol, variable, metodo, rango_inicial, rango_final)

# CONECTIVIDAD Y MOVILIDAD

#Se estandariza el campo coberturas_comisarias

variable = "cobertura_comisarias variable_cobertura"


arcpy.management.StandardizeField(out_name_com, variable, metodo, rango_inicial, rango_final)

#Se estandariza el campo red_vial

variable = "red_vial variable_red_vial"


arcpy.management.StandardizeField(out_name_vi, variable, metodo, rango_inicial, rango_final)

#Se estandariza el campo conexiones

variable = "conexion variable_conexion"


arcpy.management.StandardizeField(out_name_telcom, variable, metodo, rango_inicial, rango_final)


# CONDICION SOCIO-CULTURAL

#Se estandariza el campo instituciones

variable = "instituciones variable_instituciones"


arcpy.management.StandardizeField(out_name_cyu, variable, metodo, rango_inicial, rango_final)


#Se estandariza el campo tasa analfabetos

variable = "tasa_analfabetos variable_analfabetos"


arcpy.management.StandardizeField(tasa_analfabetismo, variable, metodo, rango_inicial, rango_final)

#Se estandariza el campo tasa de participación

variable = "tasa_participacion variable_participacion"


arcpy.management.StandardizeField(part_ciudadana, variable, metodo, rango_inicial, rango_final)

#Se estandariza el campo tasa etnica

variable = "tasa_etnia variable_etnia"


arcpy.management.StandardizeField(out_name_iet, variable, metodo, rango_inicial, rango_final)

arcpy.AddMessage("***Estandarización finalizada***")


##################
arcpy.AddMessage("***Comienza importación de capas***")


#importar capa vivienda y entorno

nombre_ve= "DPA_viv_y_ent"

arcpy.conversion.FeatureClassToFeatureClass(dpa_pob, resultados, nombre_ve)





#importar capa salud y medio ambiente

nombre_sm = "DPA_sal_y_med"

arcpy.conversion.FeatureClassToFeatureClass(dpa_pob, resultados, nombre_sm)





#importar capa conectividad y movilidad

nombre_cm = "DPA_con_y_mov"

arcpy.conversion.FeatureClassToFeatureClass(dpa_pob, resultados, nombre_cm)






#importar capa condicion sociocultural

nombre_cs = "DPA_cond_soc"

arcpy.conversion.FeatureClassToFeatureClass(dpa_pob, resultados, nombre_cs)


arcpy.AddMessage("***Importación de capas finalizado***")

#####################
arcpy.AddMessage("***Comienza unión de campos***")


primer_criterio = "cod_comuna"
segundo_criterio = "cod_comuna"
campo_union = "variable_areas_sanas"

arcpy.management.JoinField(nombre_ve, primer_criterio, out_name_asym, segundo_criterio, campo_union)




campo_union = "variable_salud"

arcpy.management.JoinField(nombre_sm, primer_criterio, out_name_fcc, segundo_criterio, campo_union)





campo_union = "variable_riesgos"

arcpy.management.JoinField(nombre_sm, primer_criterio, out_name_ervol, segundo_criterio, campo_union)




campo_union = "variable_contaminacion"

arcpy.management.JoinField(nombre_sm, primer_criterio, concentracion_contaminante, segundo_criterio, campo_union)




campo_union = "variable_conexion"

arcpy.management.JoinField(nombre_cm, primer_criterio, out_name_telcom, segundo_criterio, campo_union)



campo_union = "variable_cobertura"

arcpy.management.JoinField(nombre_cm, primer_criterio, out_name_com, segundo_criterio, campo_union)





campo_union = "variable_red_vial"

arcpy.management.JoinField(nombre_cm, primer_criterio, out_name_vi, segundo_criterio, campo_union)



arcpy.AddMessage("***Unión de campos finalizado***")


#Se debe agregar un campo

nombre_campo = "nom_com"
tipo = "TEXT"
arcpy.management.AddField(nombre_cs, nombre_campo, tipo)



arcpy.AddMessage("***Comienza cálculo de campo***")

#Se calcula el campo


parametros = "funcion(!cod_comuna!)"
code = "PYTHON3"

funcion = """def funcion(comuna):
    if comuna == 14101:
        return "Valdivia"
    elif comuna == 14102:
        return "Corral"
    elif comuna == 14103:
        return "Lanco"
    elif comuna == 14104:
        return "Los Lagos"
    elif comuna == 14105:
        return "Máfil"
    elif comuna == 14106:
        return "Mariquina"
    elif comuna == 14107:
        return "Paillaco"
    elif comuna == 14108:
        return "Panguipulli"
    elif comuna == 14201:
        return "La Unión"
    elif comuna == 14202:
        return "Futrono"
    elif comuna == 14203:
        return "Lago Ranco"
    else:
        return "Río Bueno" """

arcpy.management.CalculateField(nombre_cs, nombre_campo, parametros, code, funcion, tipo)




#Se prosigue normal al proceso



segundo_criterio_com = "comuna"
campo_union = "variable_analfabetos"

arcpy.management.JoinField(nombre_cs, nombre_campo, tasa_analfabetismo, segundo_criterio_com, campo_union)





campo_union = "variable_instituciones"

arcpy.management.JoinField(nombre_cs, primer_criterio, out_name_cyu, segundo_criterio, campo_union)





#Se prosigue normal al proceso


campo_union = "variable_participacion"

arcpy.management.JoinField(nombre_cs, nombre_campo, part_ciudadana, segundo_criterio_com, campo_union)


campo_union = "variable_etnia"

arcpy.management.JoinField(nombre_cs, primer_criterio, out_name_iet, segundo_criterio, campo_union)

arcpy.AddMessage("***Cálculo de campo completado***")





##################


#Se suman los parámetros por cada tabla (condicion sociocultural)

campo = "indicador_cond_soc"
funcion = "!variable_analfabetos!+!variable_instituciones!+!variable_participacion!+!variable_etnia!"
code = "PYTHON3"
block = ''
tipo = "DOUBLE"
arcpy.management.CalculateField(nombre_cs, campo, funcion, code, block, tipo)




#Se estandariza el campo indicador_cond_soc

variable = "indicador_cond_soc variable_cond_soc"
metodo = "MIN-MAX"
rango_inicial = "0"
rango_final = "1"

arcpy.management.StandardizeField(nombre_cs, variable, metodo, rango_inicial, rango_final)



#Se suman los parámetros por cada tabla (salud y medio ambiente)

campo = "indicador_sal_y_med"
funcion = "!variable_salud!+!variable_riesgos!+!variable_contaminacion!"

arcpy.management.CalculateField(nombre_sm, campo, funcion, code, block, tipo)



#Se estandariza el campo indicador_sal_y_med

variable = "indicador_sal_y_med variable_sal_y_med"


arcpy.management.StandardizeField(nombre_sm, variable, metodo, rango_inicial, rango_final)




#Se suman los parámetros por cada tabla (condicion conectividad y movilidad)

campo = "indicador_con_y_mov"
funcion = "!variable_conexion!+!variable_cobertura!+!variable_red_vial!"

arcpy.management.CalculateField(nombre_cm, campo, funcion, code, block, tipo)




#Se estandariza el campo indicador_con_y_mov

variable = "indicador_con_y_mov variable_con_y_mov"


arcpy.management.StandardizeField(nombre_cm, variable, metodo, rango_inicial, rango_final)




#Como el de vivienda y entornos es solo una, solo se estandariza

variable = "variable_areas_sanas variable_viv_y_ent"

arcpy.management.StandardizeField(nombre_ve, variable, metodo, rango_inicial, rango_final)




###################


#Exportar DPA final

#importar capa vivienda y entorno

nombre = "DPA_final"

arcpy.conversion.FeatureClassToFeatureClass(dpa_pob, resultados_finales, nombre)

arcpy.AddMessage("***Exportar capa DPA FiNAL completado***")



#Se insertan los indicadores (vivienda y entorno)

campo_union = "variable_viv_y_ent"

arcpy.management.JoinField(nombre, primer_criterio, nombre_ve, segundo_criterio, campo_union)




#Se insertan los indicadores (salud y medio ambiente)


campo_union = "variable_sal_y_med"

arcpy.management.JoinField(nombre, primer_criterio, nombre_sm, segundo_criterio, campo_union)




#Se insertan los indicadores (conectividad y movilidad)

campo_union = "variable_con_y_mov"

arcpy.management.JoinField(nombre, primer_criterio, nombre_cm, segundo_criterio, campo_union)




#Se insertan los indicadores (condicion sociocultural)

campo_union = "variable_cond_soc"

arcpy.management.JoinField(nombre, primer_criterio, nombre_cs, segundo_criterio, campo_union)

arcpy.AddMessage("***Inserción de indicadores completado***")


#Se calcula el indicador final

campo = "ICV"
funcion = "!variable_viv_y_ent!*{}+!variable_sal_y_med!*{}+!variable_con_y_mov!*{}+!variable_cond_soc!*{}".format(pond_viv_ent, pond_sal_ma, pond_con_mov,pond_cond_soc)
code = "PYTHON3"
block = ''
tipo = "DOUBLE"
arcpy.management.CalculateField(nombre, campo, funcion, code, block, tipo)

arcpy.AddMessage("***Cálculo de indicador final completado***")


ruta_final_dpa = "{}\\{}".format(resultados_finales, nombre)

aprxMap.addDataFromPath(ruta_final_dpa)



arcpy.AddMessage("***Proceso de herramienta finalizado con éxito***")

