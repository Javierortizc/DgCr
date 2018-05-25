#!/usr/bin/env python
# -*- coding: utf-8 -*-

######### 1.- Se recibe input de consola #########
import sys
from Detect import *
# informe = "\rAngiotac de Torax\r\rAntecedentes: \r68 a?os. Obs. TEP cronico. Cardiopatia coronaria. CIA peque?a. \r\rHallazgos: \rSe obtuvo una adecuada representacion del tronco de la arteria pulmonar, sus ramas principales, segmentarias y subsegmentarias sin identificar defectos de llene compatibles con TEP actual. \rTronco de la arteria pulmonar dilatada (33 mm). \rCorazon aumentado de tama?o en forma global, principalmente a expensas de las cavidades izquierdas. Presenta elementos de revascularizacion miocardica. \rAorta de calibre conservado. \rNo hay derrame pleural ni pericardico. \rVolumenes pulmonares conservados. No se identifican masas o focos de condensacion. Opacidades con densidad en 'vidrio esmerilado ', mal definidos, en la lingula y el segmento basal medial del LID.  Varios peque?os nodulos densamente calcificados en ambos campos pulmonares, de aspecto residual. \rTraquea y bronquios principales de calibre normal, permeables. \rNo hay adenopatias mediastinicas, hiliares ni axilares solo peque?os linfonodos de hasta 5 mm de diametro. \rSuturas de esternotomia media. \r\rImpresion: \rExamen sin hallazgos compatibles con tromboembolismo pulmonar actual, ni elementos de cronicidad. \rSignos de hipertension pulmonar. Cardiomegalia. \rLos hallazgos descritos a nivel de lingula y en aspecto basal medial del LID, son sugerentes de fenomenos infeccioso - inflamatorios. \rNodulos densamente calcificados en ambos campos pulmonares de aspecto residual. \r\rAtentamente, \r\r\rDr. Claudio Silva Fuente-Alba /ARC\rInforme Validado / Dr(a). SILVA FUENTE-ALBA, CLAUDIO\r\r"

######### 2.- Se rimportan librerias necesarios #########
import pymysql,re #importa libreria sql y re
import nltk # Se importa libreria nltk con tokenizadores
from spaner import *
from nltk.tokenize import word_tokenize,sent_tokenize,line_tokenize
from nltk.corpus import stopwords # para eliminar stopwords de la busqueda
from string import punctuation # para eliminar puntuacion de la busqueda

######### 3.- Se definen funciones #########
# Defino funcion de injección de consulta
def sqlmsg(cosulta,tipo):
    curmsg = connmsg.cursor()
    curmsg.execute(cosulta)
    if tipo == "list":
        return list(curmsg)
    if tipo == "set":
        return set(curmsg)
    if tipo == "":
        return "Realizado"
    else:
        return "Debe escribir script de consutla, set o list para respuestra"
        cur.close()

# Defino función para recuperar las n~.
def corregirN(texto):
    t = texto
    for letra in range(len(t)):
        if t[letra] == "?":
            if t[letra-1].isalnum() and t[letra+1].isalnum():
                t = t[:letra]+"Ã±"+t[letra+1:]
    return t

def tokenizar(lista):
    """Recibe una lista de tuplas (id,impresion) y
    devuelve una lista de tuplas (id,list(impresion[lista(lineas[obj_frase,obj_frase]),[obj_frase]])"""
    tokenizado =[] # se crea lista para carga de resultados
    # se recibe lista[ de tupla de (id, Impresion)] linea 323 modificado
    for (x,y) in lista:
        index = x
        # arregla las ñ antes de tokenizar
        imp = corregirN(y)
        # primer paso, se tokeniza hasta nivel lineas
        tok_lineas = line_tokenize(imp.replace("\r","\n"))
        # creo lista que recibe las lineas tokenizadas por frases # tokenizo ademas por hasta el nivel frases
        tok_frases = [sent_tokenize(linea, language='spanish') for linea in tok_lineas]
        # creo lista para recibir tokenizacion hasta nivel palabras
        imp_tok =[[spaner(frase,word_tokenize(frase, language='spanish')) for frase in linea] for linea in tok_frases]
        tokenizado.append((index,imp_tok))
        # resultado es que en tok_palabras tengo [[linea],[[frase],[frase],[palabra,palabra]]]
        # hacer la consulta ¿Que token del informe esta en SNOMED_tok.
    return tokenizado

# ¿Como vamos a consultar a la base de snomed?
def sql(cosulta,tipo,conn):
    cur = conn.cursor()
    cur.execute(cosulta)
    if tipo == "list":
        return list(cur)
    if tipo == "set":
        return set(cur)
    else:
        return "Debe escribir script de consutla, set o list para respuestra"
    cur.close()

def enlistar(lista):
    for i in range(0,len(lista),1):
         lista[i] = (lista[i][0],set(lista[i][1].split(",")))
    return lista

def quitarAcentos(texto):
    t = texto
    while "Ã­" in t:
        t = t[:t.index("Ã­")]+"i"+t[t.index("Ã­")+1:]
    while "Ã¡" in t:
        t = t[:t.index("Ã¡")]+"a"+t[t.index("Ã¡")+1:]
    while "Ã©" in t:
        t = t[:t.index("Ã©")]+"e"+t[t.index("Ã©")+1:]
    while "Ã³" in t:
        t = t[:t.index("Ã³")]+"o"+t[t.index("Ã³")+1:]
    while "Ãº" in t:
        t = t[:t.index("Ãº")]+"u"+t[t.index("Ãº")+1:]
    while "í" in t:
        t = t[:t.index("í")]+"i"+t[t.index("í")+1:]
    while "á" in t:
        t = t[:t.index("á")]+"a"+t[t.index("á")+1:]
    while "é" in t:
        t = t[:t.index("é")]+"e"+t[t.index("é")+1:]
    while "ó" in t:
        t = t[:t.index("ó")]+"o"+t[t.index("ó")+1:]
    while "ú" in t:
        t = t[:t.index("ú")]+"u"+t[t.index("ú")+1:]
    return t

def sinAcentos(Lista):
    ltok = Lista
    for i in range(len(ltok)):
        ltok[i] = (quitarAcentos(ltok[i][0]),)+(ltok[i][1:])
    return ltok

########## funcion para recomponer inf tok a 3 niveles ###############
def recomponer(inf_tok):
    recol_inf = []
    for linea in inf_tok:
        recol_linea = []
        for frase in linea:
            recol_linea.append(" ".join(frase))
        recol_inf.append(" ".join(recol_linea))
    inf_recomp = "\n".join(recol_inf)
    try:
        for i in range(0,len(inf_recomp),1):
            if inf_recomp[i] == "." or inf_recomp[i] == ":" or inf_recomp[i] == ",":
                inf_recomp = inf_recomp[:i-1]+inf_recomp[i:]
    except:
        pass
    return inf_recomp

class diccionario_snomed:
    def __init__(self, host, user, passwd, db):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db)
        cur = self.conn.cursor()
        cur.execute("SET GLOBAL group_concat_max_len=32568;")
        self.conn.commit()
        cur.close()
    def sql(self,cosulta,tipo):
        cur = self.conn.cursor()
        cur.execute(cosulta)
        if tipo == "list":
            return list(cur)
        if tipo == "set":
            return set(cur)
        cur.close()
    def carga(self):
        self.Tok_1 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=1 GROUP BY palabra;","list")))
        self.Tok_2 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=2 GROUP BY palabra;","list")))
        self.Tok_3 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=3 GROUP BY palabra;","list")))
        self.Tok_4 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=4 GROUP BY palabra;","list")))
        self.Tok_5 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=5 GROUP BY palabra;","list")))
        self.Tok_6 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=6 GROUP BY palabra;","list")))
        self.Tok_7 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=7 GROUP BY palabra;","list")))
        self.Tok_8 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=8 GROUP BY palabra;","list")))
        self.Tok_9 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=9 GROUP BY palabra;","list")))
        self.Tok_10 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=10 GROUP BY palabra;","list")))
        self.Tok_11 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=11 GROUP BY palabra;","list")))
        self.Tok_12 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=12 GROUP BY palabra;","list")))
        self.Tok_13 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=13 GROUP BY palabra;","list")))
        self.Tok_14 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=14 GROUP BY palabra;","list")))
        self.Tok_15 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=15 GROUP BY palabra;","list")))
        self.Tok_16 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=16 GROUP BY palabra;","list")))
        self.Tok_17 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=17 GROUP BY palabra;","list")))
        self.Tok_18 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=18 GROUP BY palabra;","list")))
        self.Tok_19 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=19 GROUP BY palabra;","list")))
        self.Tok_20 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=20 GROUP BY palabra;","list")))
        self.Tok_21 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=21 GROUP BY palabra;","list")))
        self.Tok_22 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=22 GROUP BY palabra;","list")))
        self.Tok_23 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=23 GROUP BY palabra;","list")))
        self.Tok_24 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=24 GROUP BY palabra;","list")))
        self.Tok_25 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=25 GROUP BY palabra;","list")))
        self.Tok_26 = sinAcentos(enlistar(self.sql("SELECT palabra,GROUP_CONCAT(descriptor_id) FROM descr_es_dx WHERE len_descr=26 GROUP BY palabra;","list")))
        self.ACR = self.sql("SELECT Acronimo,id_term_exp FROM Acronimos","list")
    def dame(self,len_descr):
        if len_descr == 1:
            return self.Tok_1
        elif len_descr == 2:
            return self.Tok_2
        elif len_descr == 3:
            return self.Tok_3
        elif len_descr == 4:
            return self.Tok_4
        elif len_descr == 5:
            return self.Tok_5
        elif len_descr == 6:
            return self.Tok_6
        elif len_descr == 7:
            return self.Tok_7
        elif len_descr == 8:
            return self.Tok_8
        elif len_descr == 9:
            return self.Tok_9
        elif len_descr == 10:
            return self.Tok_10
        elif len_descr == 11:
            return self.Tok_11
        elif len_descr == 12:
            return self.Tok_12
        elif len_descr == 13:
            return self.Tok_13
        elif len_descr == 14:
            return self.Tok_14
        elif len_descr == 15:
            return self.Tok_15
        elif len_descr == 16:
            return self.Tok_16
        elif len_descr == 17:
            return self.Tok_17
        elif len_descr == 18:
            return self.Tok_18
        elif len_descr == 19:
            return self.Tok_19
        elif len_descr == 20:
            return self.Tok_20
        elif len_descr == 21:
            return self.Tok_21
        elif len_descr == 22:
            return self.Tok_22
        elif len_descr == 23:
            return self.Tok_23
        elif len_descr == 24:
            return self.Tok_24
        elif len_descr == 25:
            return self.Tok_25
        elif len_descr == 26:
            return self.Tok_26
    def dameACR(self):
        return self.ACR

def analizar_informe(informe,diagnosticos,conn):
    conn = conn
    diagnosticos = diagnosticos
    (index,imp_tok) = informe
    resultado = []
    #print ("Analizando el mensaje: ", index, "=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")
    for linea in range(0,len(imp_tok),1): #para cada linea en informe (niv linea en inf_tok)
        for frase in range(0,len(imp_tok[linea]),1): #para cada frase en la linea (niv_frase en niv_linea)
            ID_ENCUENTROS = []
            encontrados = 0
            #remover stopwords
            niv_frase = [word for word in imp_tok[linea][frase].frase_span if word[0] not in stopwords.words('spanish')]
            #BUSCO ACRONIMOS
            acrencontrado=0
            for (acr,des) in diagnosticos.dameACR():
                if des != None: ## Modificdado par retirar acronimos que no son diagnosticos.
                    buscando = re.search(acr,imp_tok[linea][frase].frase)
                    if buscando != None:
                        acrencontrado=1
                        (start,end) = buscando.span()
                        ID_ENCUENTROS.append((des, acr,(start,end)))
                        #print (acr, "--->", imp_tok[linea][frase].frase)
            # print (niv_frase)
            #print ("Frase de largo", len(niv_frase), "-----------------------------------------------------------------------------")
            frase_tup = [(palabra[0].lower(),0,set(),palabra[1]) for palabra in niv_frase if palabra[0] not in punctuation]
            #print (frase_tup)
            #ACA CONVERTIMOS LA FRASE A (Palabra, encontrado=0, {IDs})
            len_descr = len(frase_tup)
            if len_descr > 25:
                len_descr = 26
            # vamos a consultar por cada lista de tokens (frase) desde el descriptor más largo al más corto, si el indicador de encuentros es 0. Limitando por el largo de la frase. Si la frase tiene 8 palabras, buscarmens de 8 hacia abajo.
            # Estableciendo nivel maximo.
            # print (frase_tup)
            while len_descr != 0:
                # print ("Loop de: ", len_descr, "tokens.")
                # ----INICIO---- Obteniendo tokens a buscar por nivel
                toks_a_buscar = diagnosticos.dame(len_descr)
                # ----FIN---- Termino de obtener tokes por nivel y comparo
                for l in range(0,len(frase_tup),1): #agrego ids de palabras iguales a tok
                    (palabra,encuentro,ids,span) = frase_tup[l]
                    if encuentro == 0:
                    #print (palabra , encuentro , ids)
                        for (tok,ind) in toks_a_buscar:
                            if palabra == tok:
                                frase_tup[l] = (palabra,encuentro,ind,span)
                # ver si hay ids = seguiodos con el len_descr buscado.
                # print (frase_tup) # ojo activar esto te pone la tupla previo al procesamiento (llena de ids)
                #print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #print ("Comienza revision")
                for m in range(0,len(frase_tup),1):
                    # print ("m = ",m)
                    (palabra,encuentro,ids,span) = frase_tup[m]
                    # NO busco si el termino fue encntrado o si lo que me queda de frase es menor al largo del concepto. ESTO DEBIESE IR EN EL LOOP SUPERIOR
                    #print ("Comprobando completitud de los descriptores.", "Analizando", palabra, ids) ##ACA SE QUEDA PEGADO HABIENDO AGREGADO SOLO UN ID
                    if encuentro == 0:
                        start = span[0] # desde donde busco el termino, start del primer token
                        find = 0 # si ya encontraste no busques mas en sus ids
                        for indice in ids:
                            # print ("Buscando", indice)
                            rep = 1 # indice para contar repeticiones de id
                            sec_en_rev = 1 # indice para saber el numero de palabra buscado por iteracion
                            if find == 1:
                                 break
                            while sec_en_rev <= len_descr:
                                # print ("Buscando", sec_en_rev, "repeticion.")
                                if rep == len_descr:
                                    #ENCONTRADO!! #ahora confirmar orden
                                    buff = []
                                    tokenc = []
                                    for j in range(m,m+rep,1):
                                        (a,b,c,d) = frase_tup[j]
                                        term = (quitarAcentos(sql("SELECT term FROM description_s FORCE INDEX(PRIMARY) WHERE id=(CAST("+indice+" AS char));","list",conn)[0][0])).lower()
                                        # print (a, "-->", term)
                                        if a in term:
                                            if a not in buff:
                                                buff.append(term.index(a))
                                            else:
                                                break
                                        tokenc.append(a)
                                    if sorted(buff)==buff:
                                        for j in range(m,m+rep,1):
                                            (a,b,c,d) = frase_tup[j]
                                            frase_tup[j] = (a,1,indice,d)
                                            #Agragar el ID a termino encontrado en el informe!!!
                                        ID_ENCUENTROS.append((indice, term,(start,d[1])))
                                        encontrados = 1
                                        # print ("ENCONTRADO!")
                                        #print (tokenc, "--->", imp_tok[linea][frase].frase)
                                    else:
                                        # print ("FALSA ALARMA")
                                        # print (tokenc)
                                        pass
                                # si se pasa del largo de la frase termina el while
                                if m+sec_en_rev >= len(frase_tup):
                                    break
                                (x,y,nex_id,z) = frase_tup[m+sec_en_rev]
                                if indice in nex_id:
                                    # print (indice)
                                    rep += 1
                                sec_en_rev += 1
                    else:
                        continue
                # Disminuyo nivel en el loop while
                len_descr -= 1
                # Reseteo ids
                for k in range(len(frase_tup)):
                    (palabra,encuentro,ids,span) = frase_tup[k]
                    if encuentro == 0:
                        frase_tup[k] = (palabra,encuentro,set(),span)
            if encontrados == 1 or acrencontrado==1:
                resultado.append((index, imp_tok[linea][frase].frase,ID_ENCUENTROS))
    return resultado

def run(ms):
    resultado = []
    p = Pool(8)
    rs = p.map_async(analizar_informe, [ms[i] for i in range(0,len(ms),1)], callback=resultado.append)
    largo = rs._number_left
    # print ('Procesando', largo, 'paquetes de', rs._chunksize, 'informes c/u.')
    progress = ProgressBar(widgets=[progressbar.Percentage(),'(', progressbar.Counter(),'of',str(largo),')', progressbar.AnimatedMarker(), progressbar.Bar() ,progressbar.Timer()],maxval=largo).start()
    while True:
        progress.update(largo-rs._number_left)
        sleep(1)
        if rs.ready():
            break
    progress.finish()
    p.close()
    p.terminate()
    return resultado


def inicializar():
    ######### 4.- Se inicializa sistema #########
    # PASO 3: CARGAMOS DICCIONARIOS DE TERMINOS SNOMED -------------------------------------
    #cargar lista de busquedas en RAM
    diagnosticos = diccionario_snomed(host='localhost', user='sqlTEP', passwd='sqlTEP', db='SNOMED')
    #separador por corte concat
    diagnosticos.carga()
    return diagnosticos;

def subirunnivel(resultado):
    temp = []
    for i in resultado:
        for j in i:
            temp.append(j)
    return temp

def segmentarimpresion(informe):
    i=0
    imp = informe.replace("\n","\r")
    #primero buscar impresion
    # si no se encuentra buscar OBX
    if "OBX|2" in imp:
        imp = imp[:imp.rindex("OBX|2")]
    while i < 4:
        i+=1
        if "\rImpresion" in imp:
            imp = imp[imp.index("\rImpresion")+1:]
        if "\rIR" in imp:
            imp = imp[imp.index("\rIR")+1:]
        if "\rimpresion" in imp:
            imp = imp[imp.index("\rimpresion")+1:]
        if "\rIMPRESION" in imp:
            imp = imp[imp.index("\rIMPRESION")+1:]
        if "\r Impresion" in imp:
            imp = imp[imp.index("\r Impresion")+1:]
    # si no encontro impresion corta el encabezado del mensaje. No sería necesario si antes parsiamos HL7 al campo OBX1.F5.
    if "OBX|1" in imp:
        imp = imp[imp.index("OBX|1"):]
    i = 0
    while i < 4:
        i+=1
        if "\rAtentamente," in imp:
            imp = imp[:imp.rindex("\rAtentamente,")]
        if "\r Atentamente," in imp:
            imp = imp[:imp.rindex("\r Atentamente,")]
        if "\rAtentamente." in imp:
            imp = imp[:imp.rindex("\rAtentamente.")]
        if "Dr." in imp:
            imp = imp[:imp.index("Dr.")]
        if "\rDr" in imp:
            imp = imp[:imp.index("\rDr")]
        if "Dra." in imp:
            imp = imp[:imp.index("Dra.")]
        if "Dr(a)." in imp:
            imp = imp[:imp.index("Dr(a).")]
        # Eliminar enters de los bordes
    i = 0
    while i < 5:
        i+=1
        if imp[0] == " ":
            imp = imp[1:]
        if imp[-1] == " ":
            imp = imp[:-1]
        if imp[:3] == "\r\r\r":
            imp = imp[3:]
        if imp[0] == "\r":
            imp = imp[1:]
        if imp[-3:] == "\r\r\r":
            imp = imp[:-3]
        if imp[-1] == "\r":
            imp = imp[:-1]
    return imp


def procesar(informe,diagnosticos):
    # PASO 1: SE IDENTIFICA SECCION DE IMPRESION --------------------------------------------
    L = [(1,informe)]
    # buscar impresion en el mensaje (lo ideal es primero parsiar y tener solo OBX1)
    ms=[]
    for (x,y) in L:
        imp = segmentarimpresion(y)
        ms.append((x,imp))

    L = ms
    impresion = ms[0][1]
    #print (impresion)


    # PASO 2: PROCESAMOS LOS MENSAJES ------------------------------------------------------
    # Tokenizamos a 3 niveles, lineas, frases, palabras.
    ms = tokenizar(L)
    #print (ms)


    # PASO 4: BUSCAMOS TERMINOS SNOMED -------------------------------------
    # vamos a eliminar stopwords
    # vamos a hacer la busqueda de conceptos por frase.
    # Vamos a crear una lista de tuplas por frases en las que (Palabra, encontrado=0, [IDs]) a partir de la lista ms de [(id,imp_tok)]
    conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='SNOMED')
    resultado = analizar_informe(ms[0],diagnosticos,conn)
    # print (ms)
    conn.close()

    #PASO 5: PIPE3 entrega un nivel mas de lista por lo que la funcion de la parte inferior prepara lso datos
    #se necesita una lista de tuplas y no una lista de listas de tuplas, por lo que se crea la siguiente funcion

    # Lo siguiente No es necesario si no se paralelizan procesos
    #if len(resultado)!=0:
    #    resultado = subirunnivel(resultado[0])

    #print (resultado)

    ################################################################################
    #///////////      INICIA DETECTOR DE NEGACION       \\\\\\\\\\\\\\\\\\\
    #-------------------------------------------------------------------------------
    # PASO 0: Importo Detect y cargo las regex para la busqueda.
    # se asigna a ua variable la instancia carga_objetos
    a_buscar = carga_objetos()
    # se cargan los objetos en dicha instancia
    a_buscar.preparar_objetos("cargare.csv")

    #-------------------------------------------------------------------------------
    # PASO 1: tomo la variable resultado y la trasformo en objeto frase y le agrego sus terminos encontrados.
    analisis = [] #lista que tomará los analisis de cada frase
    for (id_mensaje, frase, lista_targets) in resultado:
        analizando = analizar_frase(frase)
        for target in lista_targets:
            analizando.agregar_termino_encontrado(target[0], target[1], target[2][0], target[2][1])
        #analizando.buscar_ACR()    #aca no sirve porque no llegan las frases
        analisis.append((id_mensaje, analizando))

    #-------------------------------------------------------------------------------
    # PASO 2, buscamos los modificadores.
    for (id_mensaje,obj_analisis) in analisis:
        obj_analisis.buscar_modificadores(a_buscar)

    #-------------------------------------------------------------------------------
    # PASO 3, elimino modificadores contenidos modificadores.
    for (id_mensaje,obj_analisis) in analisis:
        obj_analisis.eliminar_mod_contenidos()

    #-------------------------------------------------------------------------------
    # PASO 4, ajustamos alcances.
    for (id_mensaje,obj_analisis) in analisis:
        obj_analisis.actualizar_alcances()

    #-------------------------------------------------------------------------------
    # PASO 5, verificamos apuntamiento.
    for (id_mensaje,obj_analisis) in analisis:
        obj_analisis.evaluar_apuntamiento()

    ##-------------------------------------------------------------------------------
    ## PASO 6, extraemos resultados.
    #for (id_mensaje,obj_analisis) in analisis:
    #    obj_analisis.resultado()



    ####### LECTURA DEL RESULTADO ##########

    #1.- Se da el pool de ids.
    L = [("1",)]

    setTEP = set([988479017,1423242011,1832151019,1838453018,2799133019,2853413013,3069648013])
    Lr = []

    for (x,y) in analisis:
        for termino in y.terminos:
            neg = 0
            act = 1
            for modificador in termino.modificado_por:
                if modificador.caracteristica == 'NEG':
                    neg = 1
                if modificador.caracteristica == 'ANTIGUO':
                    act = 0
            Lr.append((x,termino.id,neg,act))


    pool_inf = set() #para que los informes sin nada identificados salgan igualmente.
    for a in L:
        pool_inf.add(int(a[0]))


    #______________________________________
    # calculamos la presencia actual
    Tr = []
    for id_msg in pool_inf:
        id_msg = str(id_msg)
        dg_LR = 0
        Historico = 0
        Presenciatep = 0
        Almenos1negada = 0
        for (x,y,z,w) in Lr:
            if y != None:
                if x==int(id_msg) and (z==1):
                    Almenos1negada = 1
                if x==int(id_msg) and (int(y) in setTEP) and (w==0):
                    Historico = 1
                    #Menciontep = 1
                if x==int(id_msg) and (int(y) in setTEP) and (w==1) and (z==0):
                    Presenciatep = 1
        if Historico==0 and Presenciatep==1 and Almenos1negada == 0:
            dg_LR = 1
        Tr.append((id_msg,dg_LR))

    # print (Tr)

    ######## SE CREAN VARIABLES DE RESPUESTA EN HTML ########## impresion se creo nuevamente
    if Tr[0][1]==1:
        critico =  ("<p style=\"color:red;\"><b>EL INFORME ES CRITICO</b></p>")
    else:
        critico =  ("<p style=\"color:green;\"><b>EL INFORME NO ES CRITICO</b></p>")


    tablasdefrases = str()

    for fraseAnalizada in analisis:
        (idImp,objetoAnalizando) = fraseAnalizada
        tablasdefrases += '<table >'
        tablasdefrases += '<h5 style=\"text-align: left;\"><b>&nbsp;Frase: </b>'
        tablasdefrases += objetoAnalizando.frase
        tablasdefrases += '</h5>'
        tablasdefrases += '<tr bgcolor=\"#83A3CE\">'
        tablasdefrases += '<th>Diagnostico</th>'
        tablasdefrases += '<th style=\"width:100%;text-align:left;\">Modificador CARACTERISTICA (Ubicacion) (Alcance)</th>'
        tablasdefrases += '</tr>'
        tablasdefrases += '<tr>'
        for termino in objetoAnalizando.terminos:
            tablasdefrases += '<td>'
            tablasdefrases += termino.termino
            tablasdefrases += '</td>'
            tablasdefrases += '<td>'
            for modificador in termino.modificado_por:
                tablasdefrases += "\""+modificador.expresion+"\"\t"
                tablasdefrases += modificador.caracteristica
                tablasdefrases += "\t("+str(modificador.start)+","+str(modificador.end)+")"
                tablasdefrases += "\t("+str(modificador.desde)+","+str(modificador.hasta)+")"
            tablasdefrases += '</td>'
            tablasdefrases += '</tr>'

        tablasdefrases += '</table><br/>'



    html = "<h3 style=\"text-align:left;\">Impresion identificada:</h3>"
    html += impresion
    html += "<h3 style=\"text-align: left;\">Deteccion de Patologia Critica:</h3>"
    html += critico
    html += "<h3 style=\"text-align: left;\">Diagnosticos identificados:</h3>"
    html += tablasdefrases


    return (html)
