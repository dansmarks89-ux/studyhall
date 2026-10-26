"""Written accents when pronouns are attached to a verb form (used by conj2.py and verbs/check.py)."""
import re


def stressed_vowel(word):
    """Index of the vowel carrying the stress (diphthongs: the strong vowel, or the second of ui/iu)."""
    acc = [i for i, c in enumerate(word) if c in "áéíóú"]
    if acc:
        return acc[0]
    w = re.sub(r"(?<=[qg])u(?=[ei])", "#", word)   # silent u
    syl = [m.span() for m in re.finditer(r"[iuü]?[aeo][iu]?|[iuü][iu]?", w)]
    a, b = syl[-2] if w[-1] in "aeiouns" and len(syl) > 1 else syl[-1]
    nucleus = w[a:b]
    k = next((i for i, c in enumerate(nucleus) if c in "aeo"), len(nucleus) - 1)
    return a + k


def enclitic(form, pron):
    """form + pron with the written accent the new word needs (levanta+te -> levántate, detén+te -> detente)."""
    i = stressed_vowel(form)
    plain = form[:i] + form[i].translate(str.maketrans("áéíóú", "aeiou")) + form[i + 1:]
    word = plain + pron
    after = re.sub(r"(?<=[qg])u(?=[ei])", "#", word[i + 1:])
    after = re.sub(r"^[iu](?![aeo])", "", after) if form[i] in "aeoáéó" else after   # rest of the nucleus
    later = len(re.findall(r"[iuü]?[aeo][iu]?|[iuü][iu]?", after))
    hiatus = form[i] in "íú" and bool(re.search("[aeiou]", form[i - 1:i] + form[i + 1:i + 2]))
    if later >= 2 or hiatus:
        word = word[:i] + "áéíóú"["aeiou".index(word[i])] + word[i + 1:]
    return word
