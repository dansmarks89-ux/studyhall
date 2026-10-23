import json, re, sys
from wordfreq import zipf_frequency as z
STOP=set("a an the of to and or in on for with by is are be as at that this it its from who which what someone something someone's one's your their his her not no into than more most very about over under out up off so such do does did has have had was were been being when where while how why if then them they he she we you i me my our us any all some each other others another way often usually especially person people thing things kind type part being".split())
TH={-2:4.8,-1:4.8,0:4.3,1:4.0,2:3.8,3:3.8,4:3.6,5:3.6,6:3.6,7:3.4,8:3.4,9:3.4,10:3.4}
def zz(w):
    c=[w]
    for suf,rep in [("ies","y"),("es",""),("s",""),("ed",""),("ed","e"),("ing",""),("ing","e"),("ly",""),("ily","y"),("ier","y"),("iest","y"),("er",""),("est",""),("ness",""),("ment","")]:
        if w.endswith(suf) and len(w)-len(suf)>=3: c.append(w[:-len(suf)]+rep)
    if re.search(r"(.)\1(ed|ing)$",w): c.append(re.sub(r"(.)\1(ed|ing)$",r"\1",w))
    return max(z(x,'en') for x in c)
def hard_words(text, lv, allow=()):
    out=[]
    for w in re.findall(r"[A-Za-z][a-z'-]*", text):
        if w[0].isupper() and w.lower() not in text.lower()[:1]: pass
        lw=w.lower().strip("'")
        if lw in STOP or lw in allow or "-" in lw: continue
        if zz(lw)<TH[lv]: out.append(lw)
    return out
if __name__=="__main__":
    items=json.load(open(sys.argv[1]))
    n=0; tot=0; ex=[]
    for x in items:
        if x["track"]!="vocab": continue
        tot+=1; h=hard_words(x["def"],x["level"])
        if h: n+=1; ex.append((x["level"],x["term"],h))
    print(n,"of",tot,"defs use a word harder than the level allows")
    import random; random.seed(1)
    for e in random.sample(ex,min(25,len(ex))): print(e)
