class spaner:
    def __init__(self,frase,frase_tok):
        self.frase = frase
        self.frase_tok = frase_tok
        self.frase_span = []
        frasebuff = frase.lower()
        ubicacionbuff = 0
        for tok in self.frase_tok:
            if tok=="``" or tok =="''":
                tok = '"'
            else:
                start = ubicacionbuff + frasebuff.index(tok.lower())
                end = start+len(tok)
                self.frase_span.append((tok,(start,end)))
                frasebuff = frasebuff.replace(tok.lower(),"",1)
                ubicacionbuff += len(tok)
    def span(self):
        return [elemento[1] for elemento in self.frase_span]
    def starts(self):
        return [elemento[1][0] for elemento in self.frase_span]
    def ends(self):
        return [elemento[1][1] for elemento in self.frase_span]
