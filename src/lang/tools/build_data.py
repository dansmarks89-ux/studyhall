import json, re, hashlib, sys
sys.path.insert(0, '.')
import yue_data as Y, ko_data as K
from pron_ko import pron

def hid(*a): return hashlib.md5('|'.join(a).encode()).hexdigest()[:10]
def lines(s): return [l.split('|') for l in s.strip().split('\n')]

# ---------------- Cantonese ----------------
yv = []
for lv, topic, en, zh, jp, note in lines(Y.PHRASES):
    yv.append(dict(id=hid('v', zh, en), lv=int(lv), topic=topic, en=en, tg=zh, rom=jp, note=note))
ys = []
for jp, ch, mean, grp in lines(Y.TONES):
    ys.append(dict(id=hid('t', jp, ch), kind='tone', group='Tones: ' + grp, rom=jp, tg=ch, en=mean))

# ---------------- Korean ----------------
# Hand-checked overrides where the automatic checker is wrong or misses a rule.
KO_OVR = {
 '저는 미국 사람이에요': '저는 미국 사라미에요',
 '한국 음식 좋아해요?': '한국 음식 조아해요',
 '쭉 가세요': '쭉 가세요',
 '아직 한국어를 잘 못해요': '아직 한구거를 잘 모태요',
 '이따가 전화할게요': '이따가 전화할께요',
 '내일 비가 올 거예요': '내일 비가 올 꺼예요',
 '좀 도와주실 수 있어요?': '좀 도와주실 쑤 이써요',
}
KO_NOTE_ADD = {
 '맛없어요': ' Most people say 마섭써요; the dictionary standard is 마덥써요.',
}
from korean_romanizer.romanizer import Romanizer
def rr(p):
    r = Romanizer(p).romanize()
    r = r.replace('lr', 'll')
    r = re.sub(r'([kpt])\1\1', r'\1\1', r)
    return r
def strip(s): return re.sub(r'[?!,.\s]', '', s)

kv = []
for lv, topic, en, ko, note in lines(K.PHRASES):
    p = KO_OVR.get(ko) or pron(ko)[0]
    note = note + KO_NOTE_ADD.get(ko, '')
    kv.append(dict(id=hid('v', ko, en), lv=int(lv), topic=topic, en=en, tg=ko,
                   pron=p if strip(p) != strip(ko) else '', rom=rr(p), note=note.strip()))
ks = []
for letter, rom, ex, how, kind in lines(K.LETTERS):
    ks.append(dict(id=hid('l', letter), kind='letter', group='Letters: ' + ('vowels' if kind == 'vowel' else 'consonants'),
                   tg=letter, rom=rom, ex=ex, en=how, sub=kind))
for ko, en in lines(K.READING):
    p = pron(ko)[0]
    ks.append(dict(id=hid('r', ko), kind='read', group='Reading practice', tg=ko, en=en,
                   pron=p if strip(p) != strip(ko) else '', rom=rr(p)))

json.dump(dict(vocab=yv, sounds=ys), open('yue.json', 'w'), ensure_ascii=False)
json.dump(dict(vocab=kv, sounds=ks), open('ko.json', 'w'), ensure_ascii=False)
print('yue', len(yv), len(ys), ' ko', len(kv), len(ks))
for c in kv:
    if c['tg'] in KO_OVR or c['tg'] in ('몰라요', '배불러요', '닭고기', '잘 먹겠습니다', '맛없어요'):
        print(c['tg'], '|', c['pron'], '|', c['rom'], '|', c['note'])
assert len({c['id'] for c in yv + ys}) == len(yv + ys)
assert len({c['id'] for c in kv + ks}) == len(kv + ks)
