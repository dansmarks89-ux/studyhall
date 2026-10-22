# Korean content, polite everyday style (해요체). level|topic|english|korean|note
PHRASES = r"""
1|Basics|Hello|안녕하세요|The all-purpose greeting, any time of day.
1|Basics|Thank you (formal)|감사합니다|The safe default with strangers, staff and elders.
1|Basics|Thank you (polite, softer)|고마워요|Friendly but still polite.
1|Basics|I'm sorry (formal)|죄송합니다|For a real apology or to someone senior.
1|Basics|Sorry (polite)|미안해요|Everyday apology.
1|Basics|Yes|네|Also used like "uh-huh, I'm listening".
1|Basics|No|아니요|
1|Basics|It's okay / I'm fine / No thanks|괜찮아요|Very common. Also a polite way to decline an offer.
1|Basics|Goodbye (to someone who is leaving)|안녕히 가세요|Literally "go in peace". Say it when the other person leaves.
1|Basics|Goodbye (when you are leaving)|안녕히 계세요|Literally "stay in peace". Say it when you leave and they stay.
1|Basics|Excuse me! (to get attention)|저기요|How you call a server in a restaurant.
1|Basics|Just a moment|잠깐만요|
1|Basics|I don't know / I don't understand|모르겠어요|
1|Basics|Please say that once more|다시 한 번 말해 주세요|-아/어 주세요 = "please do … for me".
1|Basics|Please speak slowly|천천히 말해 주세요|
1|Basics|I speak a little Korean|한국어 조금 해요|해요 = do / speak.
1|Basics|Before eating: thank you for the meal|잘 먹겠습니다|Said before eating, especially when someone else is paying or cooked.
1|Basics|After eating: that was great, thank you|잘 먹었습니다|Said after the meal to the host or whoever paid.
1|Basics|Really?|진짜요?|
1|Numbers (Sino-Korean)|one|일|Sino-Korean numbers: used for money, minutes, dates, phone numbers.
1|Numbers (Sino-Korean)|two|이|
1|Numbers (Sino-Korean)|three|삼|
1|Numbers (Sino-Korean)|four|사|
1|Numbers (Sino-Korean)|five|오|
1|Numbers (Sino-Korean)|six|육|
1|Numbers (Sino-Korean)|seven|칠|
1|Numbers (Sino-Korean)|eight|팔|
1|Numbers (Sino-Korean)|nine|구|
1|Numbers (Sino-Korean)|ten|십|
1|Numbers (Sino-Korean)|one hundred|백|
1|Numbers (Sino-Korean)|one thousand|천|
1|Numbers (Sino-Korean)|ten thousand|만|Korean counts big numbers in ten-thousands: 만 원 = 10,000 won.
1|Numbers (native)|one (counting things)|하나|Native Korean numbers: used to count things and people, and for the hour. Before a counter word it shortens to 한.
1|Numbers (native)|two (counting things)|둘|Shortens to 두 before a counter: 두 명 = two people.
1|Numbers (native)|three (counting things)|셋|Shortens to 세: 세 시 = three o'clock.
1|Numbers (native)|four (counting things)|넷|Shortens to 네: 네 개 = four items.
1|Numbers (native)|five (counting things)|다섯|
1|Numbers (native)|six (counting things)|여섯|
1|Numbers (native)|seven (counting things)|일곱|
1|Numbers (native)|eight (counting things)|여덟|The ㄹㅂ at the end is said as just ㄹ.
1|Numbers (native)|nine (counting things)|아홉|
1|Numbers (native)|ten (counting things)|열|
2|People|I / me (polite)|저|Use 저 with people you don't know well. 나 is casual.
2|People|My name is Dan|제 이름은 댄이에요|제 = my (polite). 이에요 / 예요 = "am / is".
2|People|What's your name?|이름이 뭐예요?|
2|People|Nice to meet you|만나서 반가워요|
2|People|Where are you from?|어디에서 왔어요?|
2|People|I'm from the US|미국에서 왔어요|
2|People|I'm American|저는 미국 사람이에요|사람 = person.
2|People|I'm a doctor|저는 의사예요|
2|People|I live in Chicago|시카고에 살아요|에 = in / at.
2|People|How are you doing?|잘 지내요?|Literally "are you living well?"
2|People|I'm doing well|잘 지내요|Same words; your tone of voice makes it a statement.
2|People|What do you do for work?|무슨 일 해요?|
2|People|family|가족|
2|People|wife|아내|
2|People|husband|남편|
2|People|mom|엄마|Like "mom". 어머니 is the more respectful word.
2|People|dad|아빠|Like "dad". 아버지 is the more respectful word.
2|People|friend|친구|
2|People|child|아이|
2|People|person|사람|
2|People|This is my wife|제 아내예요|
2|People|I'm married|결혼했어요|
3|Food|water|물|
3|Food|rice / a meal|밥|"Have you eaten?" in Korean literally asks about 밥.
3|Food|meat|고기|
3|Food|beef|소고기|
3|Food|pork|돼지고기|
3|Food|chicken (as food)|닭고기|Fried chicken is 치킨.
3|Food|beer|맥주|
3|Food|coffee|커피|
3|Food|menu|메뉴|
3|Food|chopsticks|젓가락|
3|Food|spoon|숟가락|
3|Food|This one, please|이거 주세요|주세요 = "please give me". Point and say it.
3|Food|Water, please|물 좀 주세요|좀 softens a request, like "a bit / please".
3|Food|The check, please|계산해 주세요|
3|Food|It's delicious|맛있어요|
3|Food|It's not good (taste)|맛없어요|
3|Food|I'm hungry|배고파요|
3|Food|I'm full|배불러요|
3|Food|It's spicy|매워요|
3|Food|Not spicy, please|안 맵게 해 주세요|안 before a verb = not.
3|Food|How much is it?|얼마예요?|
3|Food|There are two of us|두 명이에요|명 = counter for people.
3|Food|Cheers!|건배!|
3|Food|What will you drink?|뭐 마실래요?|-ㄹ래요 = "would you like to / I'll …".
3|Food|Let's eat together|같이 먹어요|The -요 ending can also mean "let's" depending on context.
4|Getting around|Where is it?|어디예요?|
4|Getting around|Where's the restroom?|화장실이 어디예요?|
4|Getting around|here|여기|
4|Getting around|there (near you)|거기|
4|Getting around|over there|저기|
4|Getting around|left side|왼쪽|
4|Getting around|right side|오른쪽|
4|Getting around|Go straight|쭉 가세요|
4|Getting around|taxi|택시|
4|Getting around|subway|지하철|
4|Getting around|airport|공항|
4|Getting around|To the airport, please|공항으로 가 주세요|으로 = to / toward. Tell this to a taxi driver.
4|Getting around|It's far|멀어요|
4|Getting around|It's close|가까워요|
4|Getting around|How long does it take?|얼마나 걸려요?|
4|Shopping|It's expensive|비싸요|
4|Shopping|It's cheap|싸요|싸요 (cheap) has a tense ㅆ; 사요 (I buy) has a plain ㅅ.
4|Shopping|I'd like to buy this|이거 사고 싶어요|-고 싶어요 = "I want to …".
4|Shopping|Can I pay by card?|카드 돼요?|Literally "card works?"
4|Shopping|Just looking|그냥 보는 거예요|
4|Shopping|Please give me a discount|좀 깎아 주세요|Normal at markets, not in department stores.
4|Time|now|지금|
4|Time|today|오늘|
4|Time|tomorrow|내일|
4|Time|yesterday|어제|
4|Time|What time is it now?|지금 몇 시예요?|
4|Time|It's three o'clock|세 시예요|Hours use native numbers (세), minutes use Sino-Korean (삼십 분 = 30 minutes).
4|Time|half past three|세 시 반|
4|Time|weekend|주말|
4|Time|morning|아침|Also means breakfast.
4|Time|evening|저녁|Also means dinner.
5|Small talk|weather|날씨|
5|Small talk|It's hot today|오늘 더워요|
5|Small talk|It's cold|추워요|
5|Small talk|It's raining|비가 와요|Literally "rain comes".
5|Small talk|I like it|좋아해요|좋아해요 = I like (something). 좋아요 = it's good.
5|Small talk|Do you like Korean food?|한국 음식 좋아해요?|
5|Small talk|It's good / Sounds good|좋아요|
5|Small talk|Are you free? (Do you have time?)|시간 있어요?|있어요 = there is / I have. 없어요 = there isn't / I don't have.
5|Small talk|I'm busy|바빠요|
5|Small talk|I'm tired|피곤해요|
5|Small talk|It's fun|재미있어요|
5|Small talk|What are you doing?|뭐 해요?|
5|Small talk|Long time no see|오랜만이에요|
5|Small talk|See you again|또 만나요|
5|Small talk|Good night|잘 자요|
5|Small talk|Great!|좋네요!|-네요 adds "oh, I see that …" surprise or agreement.
5|Small talk|That's right|맞아요|
5|Small talk|I don't know|몰라요|Blunter than 모르겠어요.
5|Small talk|I'm going to work|출근해요|
5|Small talk|I'm going home|집에 가요|집 = home.
5|Small talk|What is this?|이거 뭐예요?|
6|Sentences|I ate (already)|먹었어요|-었어요 / -았어요 = past tense.
6|Sentences|Have you eaten?|밥 먹었어요?|A common friendly greeting.
6|Sentences|Not yet|아직이요|
6|Sentences|Have you ever been to Korea?|한국에 가 본 적 있어요?|-아/어 본 적 있어요 = "have you ever …".
6|Sentences|I'm learning Korean|한국어를 배우고 있어요|-고 있어요 = "-ing, right now".
6|Sentences|I want to go to Korea|한국에 가고 싶어요|
6|Sentences|It will rain tomorrow|내일 비가 올 거예요|-ㄹ 거예요 = will.
6|Sentences|I'm tired, so I want to go home|피곤해서 집에 가고 싶어요|-아서 / -어서 / -해서 = "so / because".
6|Sentences|If you have time, let's eat together|시간 있으면 같이 밥 먹어요|-으면 / -면 = if.
6|Sentences|Want to get coffee together?|같이 커피 마실래요?|
6|Sentences|You speak Korean really well|한국어 정말 잘하시네요|-시- shows respect to the person you praise.
6|Sentences|My Korean isn't very good yet|아직 한국어를 잘 못해요|못 = can't / not able to.
6|Sentences|I just arrived|방금 도착했어요|
6|Sentences|Sorry, I'm a bit late|미안해요, 조금 늦었어요|
6|Sentences|What time shall we meet?|몇 시에 만날까요?|-ㄹ까요 = "shall we …?"
6|Sentences|I'll call you later|이따가 전화할게요|-ㄹ게요 = "I'll (promise to) …".
6|Sentences|That was really delicious|정말 맛있었어요|
6|Sentences|Could you help me?|좀 도와주실 수 있어요?|
6|Sentences|What did you do on the weekend?|주말에 뭐 했어요?|
6|Sentences|I went out to eat with friends|친구들이랑 밥 먹으러 갔어요|-랑 = with (casual). -으러 가다 = go (in order) to.
6|Sentences|Who?|누구요?|
6|Sentences|Why?|왜요?|
6|Sentences|How?|어떻게요?|
6|Sentences|When?|언제요?|
"""

# Letters: letter|romanization|example syllable|how to say it|kind
LETTERS = r"""
ㄱ|g / k|가|Light "g", close to "k" at the start of a word. Little or no puff of air.|basic consonant
ㄴ|n|나|"n" as in "no".|basic consonant
ㄷ|d / t|다|Light "d", close to "t" at the start of a word. Little air.|basic consonant
ㄹ|r / l|라|Between vowels: a quick tap like the "tt" in American "butter". At the end of a syllable: "l".|basic consonant
ㅁ|m|마|"m" as in "mom".|basic consonant
ㅂ|b / p|바|Light "b", close to "p" at the start of a word. Little air.|basic consonant
ㅅ|s|사|"s". Before ㅣ and y-vowels it sounds like "sh": 시 = "shee".|basic consonant
ㅇ|silent / ng|아|At the start of a syllable it's silent (a placeholder). At the end it's "ng" as in "sing".|basic consonant
ㅈ|j|자|Light "j", a bit like "ch" without the puff.|basic consonant
ㅊ|ch|차|"ch" with a strong puff of air.|puffed consonant
ㅋ|k|카|"k" with a strong puff of air.|puffed consonant
ㅌ|t|타|"t" with a strong puff of air.|puffed consonant
ㅍ|p|파|"p" with a strong puff of air.|puffed consonant
ㅎ|h|하|"h". Often goes quiet between vowels.|basic consonant
ㄲ|kk|까|Tight "k" with no air, like the k in "sky". Tense your throat.|tight consonant
ㄸ|tt|따|Tight "t" with no air, like the t in "stop".|tight consonant
ㅃ|pp|빠|Tight "p" with no air, like the p in "spin".|tight consonant
ㅆ|ss|싸|Tight, hissing "s".|tight consonant
ㅉ|jj|짜|Tight "j" with no air, like the "ts" in "cats".|tight consonant
ㅏ|a|아|"ah" as in "father".|vowel
ㅑ|ya|야|"yah".|vowel
ㅓ|eo|어|"uh" as in "but", with an open mouth. Not "e-o".|vowel
ㅕ|yeo|여|"yuh".|vowel
ㅗ|o|오|"oh" with rounded lips.|vowel
ㅛ|yo|요|"yo".|vowel
ㅜ|u|우|"oo" as in "food".|vowel
ㅠ|yu|유|"you".|vowel
ㅡ|eu|으|Say "oo" but spread your lips flat, like a grimace. No English match.|vowel
ㅣ|i|이|"ee" as in "see".|vowel
ㅐ|ae|애|"e" as in "bed". Most speakers say ㅐ and ㅔ the same.|vowel
ㅒ|yae|얘|"ye" as in "yes". Rare.|vowel
ㅔ|e|에|"e" as in "bed". Same sound as ㅐ for most speakers.|vowel
ㅖ|ye|예|"ye" as in "yes".|vowel
ㅘ|wa|와|"wa" as in "wander".|vowel
ㅙ|wae|왜|"we" as in "wet". Same sound as ㅚ and ㅞ for most speakers.|vowel
ㅚ|oe|외|"we" as in "wet" in modern speech.|vowel
ㅝ|wo|워|"wuh" as in "won".|vowel
ㅞ|we|웨|"we" as in "wet". Rare.|vowel
ㅟ|wi|위|"wee".|vowel
ㅢ|ui|의|Say ㅡ then ㅣ quickly. Inside words it's often just "ee"; as "of" ('s) it's often "e".|vowel
"""

# Reading practice words (letters only, sound them out): korean|english
READING = r"""
아이|child
오이|cucumber
우유|milk
나무|tree
바다|sea
어머니|mother
사과|apple
커피|coffee
김치|kimchi
서울|Seoul
한국|Korea
사랑|love
친구|friend
물|water
밥|rice / meal
시카고|Chicago
비빔밥|bibimbap
불고기|bulgogi
떡볶이|tteokbokki (spicy rice cakes)
빵|bread
"""
