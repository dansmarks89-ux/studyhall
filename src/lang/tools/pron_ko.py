import g2pk2.g2pk2 as m
m.annotate=lambda s,mecab: s
from g2pk2 import G2p
from korean_romanizer.romanizer import Romanizer
import re
g=G2p()
def pron(s):
    t=re.sub(r'[?!,.]','',s)
    p=g(t)
    return p, Romanizer(p).romanize()
