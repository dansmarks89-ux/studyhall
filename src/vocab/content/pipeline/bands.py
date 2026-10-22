import json
L = json.load(open("lemmas.json"))
B = [(0,4.5,5.0),(1,4.0,4.5),(2,3.7,4.0),(3,3.4,3.7),(4,3.1,3.4),(5,2.85,3.1),(6,2.6,2.85),(7,2.35,2.6),(8,2.1,2.35),(9,1.85,2.1),(10,1.5,1.85)]
import os; os.makedirs("bands", exist_ok=True)
meta={}
for lv,lo,hi in B:
    ws=[x for x in L if lo<=x["z"]<hi]
    open(f"bands/level{lv}.txt","w").write("\n".join(f'{x["w"]}\t{",".join(x["pos"])}\t{x["z"]:.2f}' for x in ws))
    meta[lv]={"lo":lo,"hi":hi,"n":len(ws)}
    print(lv, lo, hi, len(ws))
json.dump(meta, open("bands/meta.json","w"))
