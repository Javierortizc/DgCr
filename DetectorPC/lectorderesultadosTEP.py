##Para la lectur del resultado de todos se utiliza
def sql(cosulta,tipo):
    conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='Mensajes TEP')
    cur = conn.cursor()
    cur.execute(cosulta)
    if tipo == "list":
        return list(cur)
    if tipo == "set":
        return set(cur)
    if tipo == "":
        return "Realizado"
    else:
        return "Debe escribir script de consutla, set o list para respuestra"
    cur.close()
    conn.close()

#1.- Se descarga bd.
L = sql("SELECT id FROM Mensajes_hl7_1516 WHERE Valido = 1","set")

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
#for (a,b,c,d) in Lr:
#    pool_inf.add(int(a))

#______________________________________
# paso 1 calculamos la precensia actual
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


#cargamos la precensia actual
cur.close()
conn.close()
conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='Mensajes TEP')
cur = conn.cursor()
for i in Tr:
    s = str(i[0])
    t = str(i[1])
    fs = "INSERT INTO NLPTEP (`Id Informe`, `Presencia Actual`) VALUES ("+s+","+t+");"
    try:
        cur.execute(fs)
        conn.commit()
    except:
        pass


#______________________________________
# paso 2 calculamos la precensia

Tr = []
for id_msg in pool_inf:
    dg_LR = 0
    Almenos1negada = 0
    Menciontep = 0
    for (x,y,z,w) in Lr:
        if y != None:
            if x==int(id_msg) and (int(y) in setTEP) and (z==1):
                Almenos1negada = 1
                Menciontep = 1
            if x==int(id_msg) and (int(y) in setTEP) and (z==0):
                Menciontep = 1
    if Almenos1negada==0 and Menciontep==1:
        dg_LR = 1
    Tr.append((id_msg,dg_LR))


#cargamos la precensia
cur.close()
conn.close()
conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='Mensajes TEP')
cur = conn.cursor()
for i in Tr:
    s = str(i[0])
    t = str(i[1])
    fs = "UPDATE NLPTEP SET `Presencia`="+t+" WHERE `Id Informe`="+s+";"
    cur.execute(fs)
    conn.commit()


#______________________________________
# paso 3 calculamos solo mencion


Tr = []
for id_msg in pool_inf:
    dg_LR = 0
    for x in resultado:
        if x[0]==int(id_msg) and len(x[2])!=0:
            for y in x[2]:
                if (y[0] != None) and (int(y[0]) in setTEP):
                    dg_LR = 1
    Tr.append((id_msg,dg_LR))

#cargamos la precensia
cur.close()
conn.close()
conn = pymysql.connect(host='localhost', user='sqlTEP', passwd='sqlTEP', db='Mensajes TEP')
cur = conn.cursor()
for i in Tr:
    s = str(i[0])
    t = str(i[1])
    fs = "UPDATE NLPTEP SET `Mencion`="+t+" WHERE `Id Informe`="+s+";"
    cur.execute(fs)
    conn.commit()
