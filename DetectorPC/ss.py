import math
Za = 1.2815515641 # calculado para intervalo de confianza de 90% (1-alpha)
Zb = 0.8416212327 # 1.0364333907 para un 85% # 1.2815515641 para 90% # 0.8416212327 para 80% # 1.6448536251 calculado para un poder de 95% (1-beta)
# se calcularon los Z con la calculadora de la página http://www.measuringu.com/zcalcp.php
pi0 = 0.0375 # prevalencia inicial en la poblacion
pi1 = 0.0125 # prevalencia final en la poblacion
d = pi0-pi1 # cambio minimo detectable por el estudio
sides = 1 # si la hipotesis es es distinto (2), si la hipotesis es, es mayor o, es menor (1)

n = (1/d**2)*((math.sqrt((Za/sides)*(pi0*(1-pi0)))+math.sqrt((Zb)*(pi1*(1-pi1))))**2)
print ("Tamaño de muestra calculado de: ", str(int(n)))

pob = 68180.0 # poblacion

ss = n/(1+((n-1)/pob))

print ("Tamaño de muestra coregido por poblacion calculado de: ", str(int(ss)))

q = 0.1 # proporcion esperada de perdidas en el seguimimento

np = ss/(1-q)
print ("Tamaño de muestra coregido por poblacion considerando perdidas calculado de: ", str(int(np)))
