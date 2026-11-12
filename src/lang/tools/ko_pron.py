"""Korean pronunciation ("said like") and romanization for the Study Hall Korean course.

g2pk2 applies the standard pronunciation rules; it needs a morphological tagger to know
which syllables are verb endings, particles, etc. (e.g. 올 거예요 -> 올 꺼예요). MeCab
can't be installed here, so Kiwi (kiwipiepy) stands in, adapted to the MeCab interface.

    from ko_pron import pron, rom
    pron("내일 비가 올 거예요")  -> "내일 비가 올 꺼예요"
    rom("내일 비가 올 꺼예요")   -> "naeil biga ol kkeoyeyo"
"""
import re, sys, os, io, contextlib
from kiwipiepy import Kiwi

_kiwi = Kiwi()

class _KiwiAsMecab:
    """MeCab-like .pos(): surface tokens that concatenate to the string without spaces,
    each tagged 'TAG1+TAG2' like mecab-ko (g2pk2 uses the last tag)."""
    def pos(self, s):
        toks = _kiwi.tokenize(s)
        groups = []  # [start, end, [tags]]
        for t in toks:
            a, b = t.start, t.start + t.len
            tag = "NNBC" if (t.tag == "NNB" and t.form in ("개", "명", "잔", "병", "권", "장", "시", "분", "살", "번", "마리", "대")) else t.tag
            if groups and (a < groups[-1][1] or t.len == 0):
                groups[-1][1] = max(groups[-1][1], b); groups[-1][2].append(tag)
            else:
                groups.append([a, b, [tag]])
        out = []
        for a, b, tags in groups:
            surf = s[a:b].replace(" ", "")
            if surf:
                out.append((surf, "+".join(tags)))
        return out

def _load_g2p():
    import g2pk2.g2pk2 as m
    m.G2p.check_mecab = lambda self: None
    m.G2p.get_mecab = lambda self: _KiwiAsMecab()
    with contextlib.redirect_stdout(io.StringIO()):
        return m.G2p()

_g2p = _load_g2p()

# Words whose standard pronunciation tenses a consonant that g2pk2 can't predict: Sino-Korean ㄹ + ㄷ/ㅅ/ㅈ
# (standard pronunciation rule 26) and lexical tensing listed in 표준국어대사전. Word -> how it is said.
TENSED = {
    "일주일": "일쭈일", "결정": "결쩡", "조건": "조껀", "일단": "일딴", "절대": "절때", "일정": "일쩡",
    "물건": "물껀", "글자": "글짜", "결제": "결쩨",
}
_TENSE = {"ㄱ": "ㄲ", "ㄷ": "ㄸ", "ㅂ": "ㅃ", "ㅅ": "ㅆ", "ㅈ": "ㅉ"}
_INIT = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"

def _initial(c):
    return _INIT[(ord(c) - 0xAC00) // 588] if "가" <= c <= "힣" else None

def _with_initial(c, i):
    o = ord(c) - 0xAC00
    return chr(0xAC00 + _INIT.index(i) * 588 + o % 588)

def _tense(t, p):
    """Apply TENSED to the g2p output p of t (same syllables in the same places; linking may change finals)."""
    if len(t) != len(p):
        return p
    p = list(p)
    for w, said in TENSED.items():
        for m in re.finditer(re.escape(w), t):
            for j, (a, b) in enumerate(zip(w, said)):
                if a != b and _initial(b) == _TENSE.get(_initial(a)) and _initial(p[m.start() + j]) == _initial(a):
                    p[m.start() + j] = _with_initial(p[m.start() + j], _initial(b))
    return "".join(p)

def pron(text):
    """How the Hangul string sounds in normal connected speech, written in Hangul."""
    t = re.sub(r"[?!,.…~]", "", text).strip()
    with contextlib.redirect_stdout(io.StringIO()):
        return _tense(t, _g2p(t))

from korean_romanizer.romanizer import Romanizer
def rom(said):
    """Revised Romanization of the pronounced form (spaces kept)."""
    r = Romanizer(said).romanize()
    r = r.replace("lr", "ll")
    r = re.sub(r"([kpt])\1\1", r"\1\1", r)
    return r

def strip(s):
    return re.sub(r"[?!,.…~\s]", "", s)

if __name__ == "__main__":
    for s in sys.argv[1:] or ["내일 비가 올 거예요", "이따가 전화할게요", "좀 도와주실 수 있어요?", "밥 먹었어요?",
                              "한국 사람이에요", "아직 한국어를 잘 못해요", "감사합니다", "맛있어요", "같이 먹어요", "읽어요", "십육", "몇 시예요?"]:
        p = pron(s); print(s, "->", p, "|", rom(p))
