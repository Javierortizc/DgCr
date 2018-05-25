import csv, copy, re
import pymysql

def sql(cosulta,tipo):
    conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='SNOMED')
    cur = conn.cursor()
    cur.execute(cosulta)
    if tipo == "list":
        return list(cur)
    if tipo == "set":
        return set(cur)
    cur.close()

class objeto_de_busqueda:
    """PASO sub0: se crea objetos que seran agregados al
    set self.setmodificadores de preparar_objetos"""
    def __init__(self, referencia, tipo, caracteristica, expresion_regular, direccion):
        self.referencia = referencia
        self.tipo = tipo
        self.caracteristica = caracteristica
        self.expresion_regular = expresion_regular
        self.direccion = direccion
    def encontrado_en(self, expresion, start, end, largo_frase):
        self.expresion = expresion
        self.start = start
        self.end = end
        self.desde = start
        self.hasta = end
        if self.direccion == "Adelante":
            self.desde = self.end
            self.hasta = largo_frase
        elif self.direccion == "Atras":
            self.desde = 0
            self.hasta = self.start
        elif self.direccion == "Entremedio":
            self.desde = self.start
            self.hasta = self.end
        elif self.direccion == "Bidireccional":  # se debe evitar al maximo la bidirecionalidad
            self.desde = 0
            self.hasta = largo_frase
        elif self.direccion == "Borde":
            pass

class carga_objetos:
    """PASO 0: Se crea objeto que tiene los terminos modificadores a
    buscar en PASO 3."""
    def __init__(self):
        self.setmodificadores = set()
    def preparar_objetos(self, filecsv):
        with open(filecsv) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', lineterminator='\n', fieldnames=['ref', 'tip', 'cat','exp','dir'])
            is_first_row = True
            for row in reader:
                if is_first_row:
                    is_first_row = False
                    continue   # skip the row
                self.setmodificadores.add(objeto_de_busqueda(row.get('ref'), row.get('tip'), row.get('cat'), row.get('exp'), row.get('dir')))

class termino_encontrado:
    """PASO 1.1: El algoritmo de busqueda encuentra los terminos y le entregará
    este objeto a analizar_frase con la funcion agregar_termino_encontrado.
    Esta clase define a objeto que representa a un termino encontrado.
    Termino que sera agregado a self.terminos de analizar frase"""
    def __init__(self, descr_id, termino, start, end):
        self.id = descr_id
        self.termino = termino
        self.start = start
        self.end = end
        self.modificado_por = set()
    def modificada_por(self,termino_modifica):
        self.modificada_por.add(termino_modifica)

class analizar_frase:
    """PASO 1: Se recibe frase en objeto que guarda frase,
    lista de terminos encontrados y lista de modificadores."""
    def __init__ (self,frase):
        self.frase = frase
        self.terminos = set()
        self.modificadores = set()
    def agregar_termino_encontrado(self, descr_id, termino, start, end):
        self.terminos.add(termino_encontrado(descr_id, termino, start, end))
    def buscar_modificadores(self, carga_objetos):
        """PASO 2: Esta es la funcion que realiza la busqueda propiamente tal, agregando los
        objetos_de_busqueda encontrados a self.modificadores y agregando el span con
        encontrado_en (funcion de Objeto a encontrar)"""
        for objeto in carga_objetos.setmodificadores:
            buscando = re.search(objeto.expresion_regular,self.frase)
            if buscando != None:
                (start,end) = buscando.span()
                encuentro = copy.copy(objeto)
                encuentro.encontrado_en(buscando.group(),start,end,buscando.endpos)
                self.modificadores.add(encuentro)
    def eliminar_mod_contenidos(self):
        """PASO 3: Elimina los objetos modificadores contenidos dentro de otros."""
        for objeto in self.modificadores:
            mod_tipo = set()
            for otro_objeto in self.modificadores-{objeto}:
                if objeto.tipo == otro_objeto.tipo:
                    mod_tipo.add(otro_objeto)
            if mod_tipo: #si el set esta vacio es False, else True
                for cada_objeto in mod_tipo:
                    if objeto.start >= cada_objeto.start and objeto.end <= cada_objeto.end:
                        self.modificadores = self.modificadores-{objeto}
                    elif objeto.start <= cada_objeto.start and objeto.end >= cada_objeto.end:
                        self.modificadores = self.modificadores-{cada_objeto}
                    else:
                        continue
    def actualizar_alcances(self):
        for objeto in self.modificadores: #primero fijo topes con objetos del mismo tipo
            mod_tipo = set()
            for otro_objeto in self.modificadores-{objeto}:
                if objeto.tipo == otro_objeto.tipo:
                    mod_tipo.add(otro_objeto)
                for cada_objeto in mod_tipo:
                    if cada_objeto.start >= objeto.desde and cada_objeto.end <= objeto.hasta: # si un objeto esta contenido en el alcance de otro.
                        if objeto.direccion == "Adelante": #si la regla del objeto que contiene es adelante
                            objeto.hasta = cada_objeto.start # se corta su alcance hasta el comienzo del objeto.
                        if objeto.direccion == "Atras":
                            objeto.desde = cada_objeto.end
                        if objeto.direccion == "Bidireccional":
                            if objeto.start > cada_objeto.end:
                                objeto.desde = cada_objeto.end
                            if objeto.end < cada_objeto.start:
                                objeto.hasta = cada_objeto.start
        for objeto in self.modificadores: # ahora fijo topes con bordes
            if objeto.direccion == "Borde":
                for otro_objeto in self.modificadores-{objeto}:
                    if otro_objeto.end < objeto.start and otro_objeto.hasta > objeto.start and (otro_objeto.direccion == "Adelante" or otro_objeto.direccion == "Bidireccional"):
                        otro_objeto.hasta = objeto.start
                    if otro_objeto.start > objeto.end and otro_objeto.desde < objeto.end and (otro_objeto.direccion == "Atras" or otro_objeto.direccion == "Bidireccional"):
                        otro_objeto.desde = objeto.end

    def evaluar_apuntamiento(self):
        for termino in self.terminos: # para cada diagnostico
            for modificador in self.modificadores: # evalua cada modificador
                if termino.start >= modificador.desde and termino.end <= modificador.hasta: #si esta dentro del alcance
                     termino.modificado_por.add(modificador) # agrega el objeto modificador al set modificado_por
    def resultado(self):
        print ("================================================================================================\n FRASE:")
        print (self.frase)
        for termino in self.terminos:
            print ("------ TERMINO ------")
            print (termino.termino)
            for modificador in termino.modificado_por:
                print (modificador.caracteristica)
    def resultadoalista(self):
        print ("================================================================================================\n FRASE:")
        print (self.frase)
        for termino in self.terminos:
            print ("------ TERMINO ------")
            print (termino.termino)
            for modificador in termino.modificado_por:
                print (modificador.caracteristica)
    def enlistar_terminos(self):
        print ("================================================================================================\n FRASE:")
        print (self.frase)
        print ("------------------------------------------------------------------------------------------------\n TERMINOS ENCONTRADOS:")
        for termino in self.terminos:
            print (termino.id, termino.termino,"(",termino.start,termino.end,")")
    def enlistar_modificadores(self):
        print ("================================================================================================\n FRASE:")
        print (self.frase)
        print ("------------------------------------------------------------------------------------------------\n MODIFICADORES ENCONTRADOS:")
        for modificador in self.modificadores:
            print (modificador.referencia, modificador.caracteristica, modificador.direccion, modificador.expresion,"(",modificador.start,modificador.end,")","(",modificador.desde,modificador.hasta,")")
    def enlistar_hallazgos(self):
        print ("================================================================================================\n FRASE:")
        print (self.frase)
        print ("------------------------------------------------------------------------------------------------\n TERMINOS ENCONTRADOS:")
        for termino in self.terminos:
            print (termino.id, termino.termino,"(",termino.start,termino.end,")")
        print ("------------------------------------------------------------------------------------------------\n MODIFICADORES ENCONTRADOS:")
        for modificador in self.modificadores:
            print (modificador.referencia, modificador.caracteristica, modificador.direccion, modificador.expresion,"(",modificador.start,modificador.end,")","(",modificador.desde,modificador.hasta,")")
    def buscar_ACR(self):
        ACR = sql("SELECT Acronimo,id_term_exp FROM Acronimos","list")
        for (acr,id_descr) in ACR:
            buscando = re.search(acr,self.frase)
            if buscando != None:
                (start,end) = buscando.span()
                self.terminos.add(termino_encontrado(id_descr, acr, start, end))
            else:
                continue

 
##### si encuentra actual pero solo corta alcanze de control de y no de actual.
