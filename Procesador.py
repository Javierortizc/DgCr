__author__ = 'javierortiz'

from nltk.tokenize import *

from SNoMed import *
from En_onto import enonto
from Imp_Diag import Imp_Diag


#SNoMed = [(939485,"desgarro"),(4939345,"multifibrilar"),(239824,"izquierda"),(7494398,"edema")]

informe = "Examen: ECOGRAFIA DE REGION ISQUIOTIBIAL DERECHA\n\nSe complemento con secuencias potenciadas en T1, T2, T2 FS y STIR.\n\nA nivel del tercio medio, en el espesor del músculo semitendinoso se observa área de discontinuidad de las fibras, que mide 3,5 x 2,6 x 0,6 cm. Se observa extensa área de edema de fibras musculares adyacentes y colección liquida laminar que rodea al músculo\n\nIMPRESIÓN DIAGNÓSTICA:\nLos hallazgos descritos son compatibles con un desgarro multifibrilar a nivel del espesor del tercio medio del músculo semitendinoso, asociado a edema de las fibras musculares adyacentes."

# NORMALISO Y TOKENISO
inf_norm = informe.lower()
inftok =  word_tokenize(inf_norm)

# SELECCIONO SOLO LA PARTE DE LA IMPRESION DIAGNOSTICA. (puedo ocupar rfind para encontrar palabra desde atras, sería mas corto)
Imp_diag_tok = Imp_Diag(inftok)

#AHORA Imp_diag_tok TIENE LA IMPRESION DIAGNOSTICA TOKENIZADA.

# Buscar diagnosticos contenidas en una lista
DxCri_candidatos = enonto(SNoMed,Imp_diag_tok)

print ("Se encontro:")
print ("Index\tTermino\t\t\tCodigo SNoMed")
for (I,T,C) in DxCri_candidatos:
    print (I,"\t\t",T,"\t\t",C)

print ("Las palabras fueron:")
for (I,T,C) in DxCri_candidatos:
    print (Imp_diag_tok[I])


####### Lamtizar? ####### Plurales? ######### Expanción de acronimos ####### Detectar negaciones? ######