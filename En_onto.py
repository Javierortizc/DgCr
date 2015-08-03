def enonto(onto, inf) :
    index=2 #contador para el for siguente
    inf_onto_resultado = []          #creo lista resultado con nombre de ontología
    for diag in inf[2:]:           #para cada palabra (candidato a diagnostico)  tambien se puede hacer con el contador como indicie
        if diag.isalpha() == True:                   #continua solo si es palabra (si es puntuación pasa a la siguiente)
            for (code,term) in onto:
                if term in str(diag):            #si esta la palabra en el listado Snomed
                    inf_onto_resultado.append((index,diag,code))
        index+=1
    return inf_onto_resultado