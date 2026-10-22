import json, re, sys
sys.path.insert(0, '.')
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); import yue_data as Y
import os as _os; T = open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'template.html')).read()

def say(tg, rom='', mean=''):
    r = f' <span class="r" data-rom="{rom}">{rom}</span>' if rom else ''
    m = f' <span class="r">{mean}</span>' if mean else ''
    return f'<button class="say" type="button" data-say="{tg}"><span class="cjk">{tg}</span>{r}{m}</button>'

# ======================= CANTONESE GUIDE =======================
INIT = [('b','p in “spin” (no puff of air)','杯','bui1'),('p','p in “pin” (with a puff)','平','peng4'),('m','m','媽','maa1'),
('f','f','飯','faan6'),('d','t in “stop” (no puff)','多','do1'),('t','t in “top” (with a puff)','天','tin1'),
('n','n (many people say it as l)','你','nei5'),('l','l','六','luk6'),('g','k in “skin” (no puff)','九','gau2'),
('k','k in “kin” (with a puff)','球','kau4'),('ng','ng in “sing”, but at the start','我','ngo5'),('h','h','好','hou2'),
('gw','gw in “Gwen” (no puff)','貴','gwai3'),('kw','qu in “queen”','裙','kwan4'),('w','w','黃','wong4'),
('z','ts in “cats”, or a soft j','早','zou2'),('c','ts with a puff, close to ch in “church”','茶','caa4'),
('s','s','三','saam1'),('j','y in “yes” (not English j)','一','jat1')]
VOW = [('aa','a in “father”, held long','茶','caa4'),('a','u in “cup”, short; always followed by another letter','心','sam1'),
('e','e in “bed”, held long','車','ce1'),('i','ee in “see”','詩','si1'),('o','aw in “law”','我','ngo5'),('u','oo in “food”','苦','fu2'),
('yu','say “ee” while rounding your lips (French u)','書','syu1'),('oe','e in “her”, with rounded lips','香','hoeng1'),
('eo','a short oe; only in eoi, eon, eot','去','heoi3'),('ei','ay in “day”','四','sei3'),('ou','o in “go”','好','hou2'),
('oi','oy in “boy”','開','hoi1'),('ai','i in “bite”, quick','雞','gai1'),('aai','“eye”, held long','買','maai5'),
('au','ow in “now”, quick','九','gau2'),('aau','ow in “now”, held long','包','baau1'),('iu','“ee-oo” run together','小','siu2'),
('ui','“oo-ee” run together','杯','bui1'),('eoi','“uh-ee” with rounded lips','去','heoi3')]
TONE_TXT = {1:'High and flat. Hold a high note.',2:'Rises from the middle to high, like a surprised “huh?”',
3:'Middle and flat. Your relaxed speaking pitch.',4:'The lowest. Starts low and sinks a little.',
5:'Rises a little from low. A smaller rise than tone 2.',6:'Low and flat, between tone 3 and tone 4.'}
TONE_EX = {1:('詩','poem'),2:('史','history'),3:('試','try'),4:('時','time'),5:('市','market'),6:('事','matter')}

def yue_guide():
    tones = ''.join(f'''<div class="tone"><div class="top"><span class="n">{t}</span><span data-contour="{t}"></span>
      {say(TONE_EX[t][0], 'si'+str(t), TONE_EX[t][1])}</div><p>{TONE_TXT[t]}</p></div>''' for t in range(1,7))
    init = ''.join(f'<tr><td class="k">{k}</td><td>{d}</td><td>{say(c,r)}</td></tr>' for k,d,c,r in INIT)
    vow = ''.join(f'<tr><td class="k">{k}</td><td>{d}</td><td>{say(c,r)}</td></tr>' for k,d,c,r in VOW)
    return f'''
<section><h2>How to read the sound spelling</h2>
<p>Every Chinese character is one syllable. The cards spell each syllable in <b>Jyutping</b>, the standard system used by Hong Kong dictionaries and phone keyboards. Each syllable is a start sound, a vowel part, and a tone number from 1 to 6.</p>
<p>Example: {say('你','nei5','you')} is <code>n</code> + <code>ei</code> + tone <code>5</code>. You don't say the number. It tells you the pitch. Every syllable on the cards also has a small pitch line after it so you can see the tone at a glance.</p>
<p class="callout">Characters don't tell you how to say them. The Jyutping does. Read the Jyutping, play the audio, and copy it out loud.</p></section>

<section><h2>The six tones</h2>
<p>Tone changes meaning. The six syllables below are all “si”; only the pitch differs. Play them in order and copy each one.</p>
<div class="tones">{tones}</div>
<p>Think of tones 3, 6 and 4 as three steps down a staircase: middle, low, lowest. Tones 2 and 5 both rise; 2 rises high, 5 rises only a little. Beginners most often mix up 3 with 6, and 2 with 5, so give those pairs extra attention.</p>
<p>Pitch is relative to your own voice. What matters is the shape of each tone and the difference between them.</p></section>

<section><h2>Start sounds</h2>
<p>Hold your hand in front of your mouth. <code>p t k c</code> should puff air onto it; <code>b d g z</code> should not. English speakers puff by habit, so practice keeping b, d and g soft.</p>
<div class="tblwrap"><table><thead><tr><th>Jyutping</th><th>Close to</th><th>Example</th></tr></thead><tbody>{init}</tbody></table></div>
<p class="callout">Jyutping <code>j</code> is the y in “yes”: {say('飲','jam2','drink')} sounds like “yum”.</p></section>

<section><h2>Vowel parts</h2>
<div class="tblwrap"><table><thead><tr><th>Jyutping</th><th>Close to</th><th>Example</th></tr></thead><tbody>{vow}</tbody></table></div>
<p>Long <code>aa</code> and short <code>a</code> are different words: {say('三','saam1','three')} vs {say('心','sam1','heart')}.</p></section>

<section><h2>Endings</h2>
<p><code>-m -n -ng</code> work as in English.</p>
<p><code>-p -t -k</code> are cut off: put your lips or tongue in place but don't release any air. These syllables sound short and clipped. {say('十','sap6','ten')} ends with closed lips, {say('八','baat3','eight')} with the tongue behind the teeth, {say('六','luk6','six')} with the back of the tongue raised.</p></section>

<section><h2>Two syllables with no vowel</h2>
<p>{say('唔','m4','not')} is a hummed “m” on the lowest tone. {say('五','ng5','five')} is a hummed “ng” with a small rise. Both are very common.</p></section>

<section><h2>Things that surprise beginners</h2>
<ul>
<li><b>Changed tones.</b> Some words rise to tone 2 in everyday speech: 話 is waa6 in the dictionary but {say('廣東話','gwong2 dung1 waa2','Cantonese')}. The cards always show the tone people actually say.</li>
<li><b>Relaxed pronunciation.</b> Many Hong Kongers say n as l (你 lei5) and drop a starting ng (我 o5). Learn to recognize both; either is fine to use.</li>
<li><b>Ending particles.</b> Small words at the end of a sentence, like <span class="cjk">呀 啦 喇 㗎</span>, carry tone of voice: softening, suggesting, explaining. Leaving them out sounds blunt.</li>
<li><b>Spoken vs written.</b> Spoken Cantonese is different from standard written Chinese. Characters like <span class="cjk">唔 佢 冇 嘅 咗</span> only exist in spoken Cantonese. This app teaches the spoken language.</li>
</ul></section>

<section><h2>How to study</h2>
<ol>
<li>Play every example on this page and copy it out loud.</li>
<li>In <b>Tones</b>, train your ear: each card plays a syllable and you name the tone. Start with the six “si” cards.</li>
<li>In <b>Words &amp; phrases</b>, start with <b>See &amp; hear</b>: you see the characters, hear the audio, and say the meaning. New cards arrive in level order, so harder language comes later on its own.</li>
<li>Once a level feels easy there, move it to <b>Listen only</b> (no text, just sound), then to <b>Say it</b> (English to Cantonese).</li>
<li>Always answer out loud before you reveal, then play the audio and copy it.</li>
<li>15 to 20 minutes every day works better than one long session a week.</li>
</ol></section>
<section><h2>Character reference</h2>
<p>You won't be tested on these. They're common characters you'll keep seeing on the cards and on signs. Tap one to hear it.</p>
<div class="tblwrap"><table><thead><tr><th>Character</th><th>Sound</th><th>Meaning</th><th>Where you'll see it</th></tr></thead><tbody>'''+''.join(f'<tr><td class="h">{say(c)}</td><td><span data-rom="{j}">{j}</span></td><td>{m}</td><td>{e}</td></tr>' for c,j,m,e in (l.split('|') for l in Y.CHARS.strip().split('\n')))+'''</tbody></table></div></section>'''

# ======================= KOREAN GUIDE =======================
def ko_guide():
    def block(tg, parts, rom, mean): return f'<div class="block"><span class="tgs">{tg}</span><span class="parts">{parts}</span>{say(tg, rom, mean)}</div>'
    def ex(w, said, mean): return f'<li>{say(w)} → <span class="cjk">{said}</span> <span class="sub">({mean})</span></li>'
    trio = [('가','카','까'),('다','타','따'),('바','파','빠'),('자','차','짜'),('사','','싸')]
    rows = ''.join('<tr>' + ''.join(f'<td>{say(x) if x else "–"}</td>' for x in t) + '</tr>' for t in trio)
    vowels = ' '.join(say(v, r) for v, r in [('아','a'),('어','eo'),('오','o'),('우','u'),('으','eu'),('이','i'),('애','ae')])
    return f'''
<section><h2>How Hangul works</h2>
<p>Hangul is an alphabet with 24 basic letters. Letters stack into square blocks, and each block is one syllable. A block always starts with a consonant; when a syllable starts with a vowel, the silent letter <span class="cjk">ㅇ</span> holds the place.</p>
<p>Tall vowels sit to the right of the consonant. Flat vowels sit underneath. A final consonant, if there is one, goes at the bottom.</p>
<div class="blocks">{block('가','ㄱ + ㅏ','ga','')}{block('고','ㄱ + ㅗ','go','')}{block('한','ㅎ + ㅏ + ㄴ','han','')}{block('국','ㄱ + ㅜ + ㄱ','guk','')}</div>
<p>Put the last two together: {say('한국','hanguk','Korea')}.</p></section>

<section><h2>Consonants come in three kinds</h2>
<p>The hardest consonant skill in Korean is telling three versions of the same sound apart. Hold your hand in front of your mouth.</p>
<div class="tblwrap"><table><thead><tr><th>Plain: light, small breath</th><th>Puffed: strong burst of air</th><th>Tight: no air, tense throat</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>At the start of a word, plain <span class="cjk">ㄱ ㄷ ㅂ ㅈ</span> sound close to k, t, p, ch to English ears. Between vowels they soften to g, d, b, j. That's why {say('고기','gogi','meat')} has two different-sounding g's.</p>
<p>The rest are easy: <span class="cjk">ㄴ</span> n, <span class="cjk">ㅁ</span> m, <span class="cjk">ㅎ</span> h, <span class="cjk">ㅇ</span> silent at the start and “ng” at the end. <span class="cjk">ㄹ</span> is a quick tap between vowels (like the tt in American “butter”) and an “l” at the end of a syllable.</p></section>

<section><h2>Vowels</h2>
<p>{vowels}</p>
<p>Add a short stroke and a vowel gains a y-sound: <span class="cjk">ㅏ→ㅑ, ㅓ→ㅕ, ㅗ→ㅛ, ㅜ→ㅠ</span>. Combine two and you get a w-sound: <span class="cjk">ㅗ+ㅏ = ㅘ</span> (wa), <span class="cjk">ㅜ+ㅓ = ㅝ</span> (wo).</p>
<p class="callout">Two need care. <span class="cjk">ㅓ</span> (written eo) is an open “uh”, like the u in “but”. It is not “e-o”. <span class="cjk">ㅡ</span> (eu) is “oo” said with your lips spread flat.</p>
<p>Most people today say <span class="cjk">ㅐ</span> and <span class="cjk">ㅔ</span> the same way, like the e in “bed”. Likewise <span class="cjk">ㅙ ㅚ ㅞ</span> all sound like “we” in “wet”.</p></section>

<section><h2>Final consonants: only seven sounds</h2>
<p>At the end of a syllable every consonant is said as one of seven sounds, and the ending is held, not released.</p>
<div class="tblwrap"><table><thead><tr><th>Written at the end</th><th>Said as</th></tr></thead><tbody>
<tr><td class="h">ㄱ ㅋ ㄲ</td><td>k (held)</td></tr><tr><td class="h">ㄴ</td><td>n</td></tr>
<tr><td class="h">ㄷ ㅅ ㅆ ㅈ ㅊ ㅌ ㅎ</td><td>t (held)</td></tr><tr><td class="h">ㄹ</td><td>l</td></tr>
<tr><td class="h">ㅁ</td><td>m</td></tr><tr><td class="h">ㅂ ㅍ</td><td>p (held)</td></tr><tr><td class="h">ㅇ</td><td>ng</td></tr></tbody></table></div>
<ul>{ex('옷','옫','clothes')}{ex('부엌','부억','kitchen')}{ex('닭','닥','chicken; two final letters, only one is said')}</ul></section>

<section><h2>Spelling vs speech</h2>
<p>Korean spelling shows the parts of a word; speech smooths them together. Cards show a “said like” line whenever the sound differs from the spelling. You don't need to memorize these rules now. Notice them as they come up.</p>
<ol>
<li><b>Linking.</b> A final consonant slides into a next syllable that starts with <span class="cjk">ㅇ</span>.<ul>{ex('한국어','한구거','Korean language')}{ex('음악','으막','music')}</ul></li>
<li><b>Nasal change.</b> A p, t or k ending before <span class="cjk">ㄴ</span> or <span class="cjk">ㅁ</span> becomes m, n or ng.<ul>{ex('감사합니다','감사함니다','thank you')}{ex('한국말','한궁말','Korean language')}</ul></li>
<li><b>ㅎ.</b> Next to <span class="cjk">ㄱ ㄷ ㅂ ㅈ</span> it turns them into puffed sounds. Between vowels it usually disappears.<ul>{ex('못해요','모태요',"can't")}{ex('좋아요','조아요','good')}</ul></li>
<li><b>Tightening.</b> After a k, t or p ending, the next plain consonant becomes tight.<ul>{ex('학교','학꾜','school')}{ex('맥주','맥쭈','beer')}</ul></li>
<li><b>ㄴ next to ㄹ</b> becomes ㄹㄹ.<ul>{ex('설날','설랄',"Lunar New Year")}{ex('연락','열락','contact')}</ul></li>
<li><b>ㄷ or ㅌ before 이</b> becomes ㅈ or ㅊ.<ul>{ex('같이','가치','together')}</ul></li>
</ol></section>

<section><h2>Polite speech</h2>
<p>Korean changes verb endings depending on politeness. The cards use the <b>-요</b> style: polite and friendly, the normal choice with adults you don't know well. A few fixed phrases, like <span class="cjk">감사합니다</span> and <span class="cjk">죄송합니다</span>, use the more formal <span class="cjk">-ㅂ니다</span> ending because that's how everyone says them. Dropping <span class="cjk">-요</span> is casual speech for close friends; wait until someone invites you to.</p></section>

<section><h2>Two sets of numbers</h2>
<p><b>Native Korean</b> numbers (<span class="cjk">하나, 둘, 셋</span>…) count things and people, and give the hour. <b>Sino-Korean</b> numbers (<span class="cjk">일, 이, 삼</span>…) are for money, minutes, dates and phone numbers. So 3:30 is {say('세 시 삼십 분','se si samsip bun')}: native for the hour, Sino-Korean for the minutes.</p></section>

<section><h2>How to study</h2>
<ol>
<li>Play every example on this page and copy it out loud.</li>
<li>In <b>Hangul</b>, learn the letters, then the reading-practice words. Most people can read Hangul after a few short sessions.</li>
<li>In <b>Words &amp; phrases</b>, use <b>Recognize</b> first. New cards arrive in level order, so harder language comes later on its own. Switch to <b>Say it</b> once a level feels easy.</li>
<li>Romanization is training wheels. Once you can read Hangul, turn it off on the card front in the settings below.</li>
<li>15 to 20 minutes every day works better than one long session a week.</li>
</ol></section>'''

LANGS = {
 'yue': dict(file='cantonese.html', title='Cantonese Flashcards', h1='Cantonese', h1cjk='廣東話', htmllang='zh-HK',
   cjkfont='Noto+Sans+TC', cjkfamily='Noto Sans TC', cjkfallback='"PingFang HK", "PingFang TC", "Microsoft JhengHei", sans-serif',
   groundname='a faint pitch staff, like the tone diagrams',
   groundcss='background:linear-gradient(180deg,transparent 13px,var(--ground) 13px 14px,transparent 14px 27px,var(--ground) 27px 28px,transparent 28px 41px,var(--ground) 41px 42px,transparent 42px 55px,var(--ground) 55px 56px,transparent 56px 69px,var(--ground) 69px 70px,transparent 70px) 0 6px/100% 98px repeat-y',
   paper='#F8F6F5', ink='#1F1A19', muted='#6B605E', line='#E6DFDD', accent='#B0231A', accentsoft='#F8E7E4', ground='rgba(176,35,26,.08)',
   dpaper='#141112', dpanel='#1C1819', dline='#352C2B', daccent='#FF8A7A', daccentsoft='#3A2422', dground='rgba(255,138,122,.08)',
   soundstab='Tones', soundssub='train your ear', romfront='Show Jyutping on the front of cards',
   audionote='Device Cantonese voices usually get tones right on common words but can slip on single characters. When the audio and the Jyutping disagree, trust the Jyutping; it has been checked against Cantonese dictionaries. On iPhone, if the voice sounds like Mandarin, check Settings → Accessibility → Spoken Content → Voices → Chinese.',
   guide=yue_guide(), data='yue.json',
   config=dict(key='yue-flash', lang='yue', langName='Cantonese', htmlLang='zh-HK', ttsLang='zh-HK',
     voiceRe=r'^(yue|zh[-_](HK|Hant[-_]HK))', voiceNameRe=r'cantonese|粵|粤', voicePrefer=r'sinji|google|premium|enhanced',
     testPhrase='你好，我叫Dan。我學緊廣東話。', soundsNoun='tone cards', dirs=[['rec','See & hear'],['listen','Listen only'],['say','Say it']], recPrompt='Listen and look. What does it mean? Answer out loud, then reveal.',
     voiceHelp='<h3>No Cantonese voice found on this device</h3>The cards still work, but you won’t hear audio until a Hong Kong Cantonese voice is installed.<ol>'
       '<li><b>iPhone or iPad:</b> Settings → Accessibility → Spoken Content → Voices → Chinese. Choose the Cantonese (Hong Kong) voice listed there and download it.</li>'
       '<li><b>Mac:</b> System Settings → Accessibility → Spoken Content. Open the “System voice” menu and choose Manage Voices. Click Chinese in the list, scroll to the Hong Kong (Cantonese) voices, and click the download button next to one.</li>'
       '<li>Reload this page, then open “Audio &amp; display settings” below and press Test voice.</li></ol>')),
 'ko': dict(file='korean.html', title='Korean Flashcards', h1='Korean', h1cjk='한국어', htmllang='ko',
   cjkfont='Noto+Sans+KR', cjkfamily='Noto Sans KR', cjkfallback='"Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
   groundname='a faint manuscript-paper grid (wongoji)',
   groundcss='background-image:linear-gradient(var(--ground) 1px,transparent 1px),linear-gradient(90deg,var(--ground) 1px,transparent 1px);background-size:30px 30px;background-position:-1px -1px',
   paper='#F6F7F5', ink='#18201C', muted='#5F6964', line='#DEE4E0', accent='#2647A8', accentsoft='#E6EBF8', ground='rgba(30,120,80,.10)',
   dpaper='#101413', dpanel='#171C1B', dline='#2A3230', daccent='#8FA8FF', daccentsoft='#1E2742', dground='rgba(120,200,160,.07)',
   soundstab='Hangul', soundssub='letters &amp; reading', romfront='Show romanization on the front of cards',
   audionote='Device Korean voices are generally clear. When the audio and the “said like” line disagree, trust the “said like” line.',
   guide=ko_guide(), data='ko.json',
   config=dict(key='ko-flash', lang='ko', langName='Korean', htmlLang='ko', ttsLang='ko-KR',
     voiceRe=r'^ko', voiceNameRe=r'korean|한국', voicePrefer=r'yuna|google|premium|enhanced',
     testPhrase='안녕하세요. 한국어를 배우고 있어요.', soundsNoun='letter & reading cards', dirs=[['rec','Recognize'],['say','Say it']], recPrompt='What does it mean? Say it out loud first.',
     voiceHelp='<h3>No Korean voice found on this device</h3>The cards still work, but you won’t hear audio until a Korean voice is installed.<ol>'
       '<li><b>iPhone or iPad:</b> Settings → Accessibility → Spoken Content → Voices → Korean. Choose a voice and download it.</li>'
       '<li><b>Mac:</b> System Settings → Accessibility → Spoken Content. Open the “System voice” menu and choose Manage Voices. Click Korean in the list and click the download button next to a voice.</li>'
       '<li>Reload this page, then open “Audio &amp; display settings” below and press Test voice.</li></ol>')),
}

if __name__ == '__main__':
  for code, L in LANGS.items():
      h = T
      data = json.load(open(L['data']))
      rep = {'__TITLE__':L['title'],'__H1__':L['h1'],'__H1CJK__':L['h1cjk'],'__HTMLLANG__':L['htmllang'],
             '__CJKFONT__':L['cjkfont'],'__CJKFAMILY__':L['cjkfamily'],'__CJKFALLBACK__':L['cjkfallback'],
             '__GROUNDNAME__':L['groundname'],'__GROUNDCSS__':L['groundcss'],
             '__DPAPER__':L['dpaper'],'__DPANEL__':L['dpanel'],'__DLINE__':L['dline'],'__DACCENTSOFT__':L['daccentsoft'],'__DACCENT__':L['daccent'],'__DGROUND__':L['dground'],
             '__PAPER__':L['paper'],'__INK__':L['ink'],'__MUTED__':L['muted'],'__LINE__':L['line'],'__ACCENTSOFT__':L['accentsoft'],'__ACCENT__':L['accent'],'__GROUND__':L['ground'],
             '__SOUNDSTAB__':L['soundstab'],'__SOUNDSSUB__':L['soundssub'],'__ROMFRONTLABEL__':L['romfront'],'__AUDIONOTE__':L['audionote'],
             '__GUIDE__':L['guide'],
             '__CONFIG__':json.dumps(L['config'], ensure_ascii=False),'__DATA__':json.dumps(data, ensure_ascii=False)}
      for k in sorted(rep, key=len, reverse=True):
          h = h.replace(k, rep[k])
      left = re.findall(r'__[A-Z]+__', h)
      assert not left, left
      open(L['file'], 'w').write(h)
      print(L['file'], len(h))
