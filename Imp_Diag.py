__author__ = 'javierortiz'

def Imp_Diag(inftok):
    encontrado = 0
    for palabra in inftok:
        if "imp" in palabra[:3]:
            encontrado = 1
            imp_diag = inftok.index(palabra)
        if encontrado == 1 and "diag" in palabra[:4]:
            Imp_diag_tok = inftok[imp_diag:]
    return Imp_diag_tok
