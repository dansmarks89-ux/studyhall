# Verb lessons — content spec (Clinic Spanish, Study Hall)

The owner (an American doctor learning Latin American Spanish) asked for a lesson type built on ONE verb: the verb in
different tenses and different sentence structures, so he really learns how the verb and the tenses work. Every few
lessons on his learning path is now a verb lesson. You write the material for a batch of verbs. Accuracy matters more than
anything: every sentence is shown as a model to copy and is graded against. If you are not completely sure a sentence is
natural, correct Latin American Spanish, write a different one.

## What a verb lesson does with your material
1. **Meet the verb**: the infinitive, `en` (meaning), `note` (how it conjugates), `uses` (its 2–3 most useful patterns, each with an example).
2. **Tense by tense** (only tenses the learner has reached): the five forms, then: pick a form, type a form, and fill the verb into one of your sentences of that tense (the sentence with `f` blanked out and the English shown).
3. **Sentence types**: build your question sentence from word tiles, hear your negative sentence and pick its meaning, build an object-pronoun sentence from tiles, fill in a command.
4. **Which tense?**: your `stmt` sentence with the verb blanked and NO English shown; options = the right form plus the same person's form in some of the tenses you list in `wrong`. The `clue` (a time word or trigger) is what decides it. So `wrong` must only list tenses that are clearly wrong in that sentence.
5. **Say it**: the learner sees your English and says the Spanish.

## Output
One JSON file, an object keyed by the verb exactly as given (e.g. `"tener"`, `"sentarse"`):
```json
"tener": {
  "en": "to have",
  "note": "Irregular. Present: *tengo*, and e→ie in *tienes, tiene, tienen*. Preterite stem *tuv-* (*tuve, tuvo*); future *tendré*; command *ten* / *tenga*.",
  "uses": [
    {"es": "tener que + infinitive", "en": "to have to", "x": "Tengo que trabajar mañana.", "xen": "I have to work tomorrow."},
    {"es": "tener … años", "en": "to be … years old", "x": "Mi hija tiene seis años.", "xen": "My daughter is six years old."},
    {"es": "tener dolor / fiebre / hambre", "en": "to have pain / a fever / to be hungry", "x": "¿Tiene fiebre?", "xen": "Do you have a fever?"}
  ],
  "cmd": "both",
  "s": [
    {"t": "Present", "p": 0, "k": "stmt", "es": "Todos los días tengo clase a las ocho.", "en": "Every day I have class at eight.", "f": "tengo", "clue": "Todos los días", "wrong": ["Preterite", "Future", "Conditional", "Imperfect subjunctive"]},
    {"t": "Present", "p": 2, "k": "q", "es": "¿Tiene alergia a algún medicamento?", "en": "Are you allergic to any medication?", "f": "Tiene"},
    {"t": "Present", "p": 4, "k": "neg", "es": "Mis padres no tienen carro.", "en": "My parents don't have a car.", "f": "tienen"},
    {"t": "Preterite", "p": 0, "k": "obj", "es": "La tuve en la mano un segundo.", "en": "I had it in my hand for a second.", "f": "La tuve"},
    {"t": "Command (+)", "p": 2, "k": "cmd", "es": "Tenga paciencia, ya viene la doctora.", "en": "Be patient, the doctor is coming.", "f": "Tenga"}
  ]
}
```
(The example is shortened: a real entry has all the sentences listed below.)

### Fields
- `en`: dictionary-style meaning(s), ≤ 60 characters (`"to take; to drink"`).
- `note`: 1–2 sentences, ≤ 260 characters: is it regular / stem-changing / irregular, and which forms the learner must memorize (only true, checkable facts that match the table you were given). Spanish words in `*asterisks*`. No tense in the note that the table contradicts.
- `uses`: 2 or 3 of the verb's most useful patterns or collocations (`es` pattern, `en` meaning, `x` example sentence, `xen` its translation). Examples follow the same sentence rules below.
- `cmd`: which commands are natural to say to someone: `"both"` (affirmative and negative, the usual case), `"neg"` (only negative commands make sense: *no se desmaye*, *no se caiga*; affirmative *desmáyese* is absurd), `"none"` (no command makes sense: *nacer*, *latir*, *doler*, *gustar*, *haber*, *soler*, *parecer*…).
- `s`: the sentences:
  - For EACH of these 10 tenses exactly 3 sentences: one `"k": "stmt"` (statement), one `"q"` (question, ¿…?), one `"neg"` (negative: *no* (or *nunca*) belongs to this verb, right before it or its pronouns).
    Tenses (use these exact names): `Present`, `Preterite`, `Imperfect`, `ir a` (ir a + infinitive), `Future`, `Conditional`, `Present perfect`, `Pluperfect`, `Present subjunctive`, `Imperfect subjunctive`.
  - Commands (`"k": "cmd"`), tense `Command (+)` / `Command (−)`: if `cmd` is `both`: 2 affirmative (one usted p 2, one tú p 1) and 1 negative (usted); if `neg`: 2 negative (usted and tú); if `none`: no commands.
  - Object pronouns (`"k": "obj"`): 2 sentences where an object pronoun goes with the verb (*lo / la / los / las / le / les / se lo / me lo…*), in Present, Preterite, Imperfect, Future, Present perfect, Present subjunctive or a command. Leave them out (0) only for verbs that never take an object (*llegar*, *nacer*, *sudar*, *latir*…). Clinic verbs: a command with an attached pronoun is ideal (*Tómela con agua.*).
  - So a typical verb has 30 + 3 + 2 = 35 sentences.
- Each sentence:
  - `t`: tense (names above), `p`: person index **0 yo, 1 tú, 2 usted / él / ella, 3 nosotros, 4 ustedes / ellos / ellas** (commands: 1 tú, 2 usted, 3 nosotros, 4 ustedes).
  - `f`: the verb form exactly as it appears in `es` and exactly as in the table you were given for that tense and person (the app blanks it out and checks the learner's answer against it). Special cases:
    - `ir a`: the whole chunk, *voy a tener*; reflexive verbs: *me voy a sentar* or *voy a sentarme*.
    - `Command (−)`: include the *no*: *no tome*, *no se siente*.
    - `obj`: the pronoun(s) plus the verb as one chunk: *lo tengo*, *se lo di*, *lo he tomado*, *me lo pongo*, *no la tome*; an affirmative command with the pronoun attached: *tómela*, *siénteselo* (written accent as the checker says).
    - Other negatives: the *no* is NOT part of `f` (*No tengo tiempo.* → `f` = *tengo*).
    - Capital letter at the start of a sentence is fine (`"f": "Tiene"`).
  - `es`: the Spanish sentence; `en`: natural American English with the same meaning, making the person clear (the learner fills the blank from the English).
  - `stmt` sentences only: `clue` = the exact words in `es` that tell you which tense it must be (time word or trigger), and `wrong` = at least 3 tenses (from the 10 names, not commands) whose same-person form would be **clearly wrong** in this exact sentence. Only list tenses a native speaker would reject. Careful: *Ayer tenía fiebre* is fine, so with *ayer* the Imperfect is not wrong; *Mañana tengo cita* is fine, so with *mañana* the Present is not wrong; *Si tuviera…* clauses, *quiero que* + subjunctive, *cuando* + subjunctive for the future, *todavía no* + present perfect are good clues. Good clue words by tense:
    Present *todos los días, normalmente, ahora, siempre*; Preterite *ayer, anoche, el lunes pasado, hace dos días*; Imperfect *de niño, antes (siempre), cuando era joven, todos los veranos*; ir a *mañana, esta tarde, el próximo fin de semana*; Future *algún día, el próximo año, dentro de un mes, seguramente*; Conditional *en tu lugar, me dijo que, si pudiera… (main clause)*; Present perfect *hoy, esta semana, alguna vez, todavía no, ya*; Pluperfect *cuando llegué, ya …; nunca antes …*; Present subjunctive *quiero que, es importante que, ojalá, para que, cuando (future)*; Imperfect subjunctive *si (hypothetical), quería que, me pidió que, como si*.

## Sentence rules
- Natural, everyday **Latin American** Spanish (Mexico / Central America as the default: *carro, celular, manejar, platicar*, *ustedes* for plural you). **Never vosotros / os / vos.** No Spain-only words.
- **usted** with patients, strangers, the doctor; **tú** with friends, family, children. A clinic sentence to a patient uses usted.
- Short and clear: ≤ 12 words (14 at most). Common words a learner meets in the first year; avoid rare vocabulary, idioms and slang. Each sentence its own situation; don't repeat the same frame.
- Mix contexts: about a third clinic (doctor–patient, symptoms, appointments, medication, hospital), the rest everyday life (family, work, food, travel, plans, friends). For clinic verbs (the batch file marks them), about two thirds clinic.
- Within one tense, the 3 sentences use 3 different persons; over the whole verb every person (0–4) appears several times. Gustar-type verbs (*gustar, encantar, doler, importar, interesar*): the verb agrees with the thing (p 2 singular / p 4 plural) and the pronoun (*me, te, le, nos, les*) varies.
- Reflexive verbs (keyed with *-se*): the pronoun is part of every form; keep the right meaning (*quedarse* = to stay, not *quedar*).
- Use the tense correctly and idiomatically (preterite vs imperfect, subjunctive triggers, *si* + imperfect subjunctive + conditional). Present perfect as Latin Americans use it (experience, *todavía no*, *ya*, *alguna vez*, *hoy* is ok), not for a finished past event with *ayer*.
- The verb appears ONCE in its sentence (the blank must be unambiguous); it may not also appear in another form in the same sentence.
- Punctuation: capital (or ¿ ¡) at the start, final . ? or !, paired ¿? ¡!, accents always right.
- English: natural, not word-for-word; American spelling.

## Check your file
Run `python3 /tmp/studyhall/src/spanish/content/verbs/check.py YOUR_FILE.json` and fix every ERROR (warnings are worth fixing too). It checks the forms against the tables, counts, fields and punctuation; it cannot check meaning or naturalness. That's your job.

## Added after the first drafts (reviewers apply these)
- `cmd` may also be `"pos"`: only affirmative commands are natural (*cálmese*, *alíviese pronto*, *disfrute*); then 2 affirmative commands (usted, tú) and no negative ones. Use it instead of a contrived negative command (*No se calme con alcohol*, *No disfrute del sol sin bloqueador*).
- `"third": true` (optional): the verb is said of things or body parts, not people (*latir*, *arder*, *costar*, *ocurrir*…): every non-command sentence uses person 2 or 4 and the lesson only practices those forms. (gustar, encantar, doler, importar, interesar, fascinar, apetecer count as third automatically.)
- In "Which tense?" the options are the same person's forms in the `wrong` tenses: a listed tense whose form would be acceptable in that sentence (in any common Latin American usage) makes a correct answer look wrong. That is the worst possible error in this content.
