"""How the pages cut a unit's words into lessons (spanish and lang app.html parts()), for the builds to place grammar notes."""


def page_parts(n, size):
    """The page's lessons over n words of a unit with nothing taught: index ranges of size words, a single one left at
    the end joining the lesson before."""
    out = [range(i, min(i + size, n)) for i in range(0, n, size)]
    if len(out) > 1 and len(out[-1]) == 1:
        out[-2:] = [range(out[-2].start, n)]
    return out


def overlap_start(old, n):
    """The first index of old (a range of word indexes) inside the page's 5-word lesson that shares the most of it
    (the earlier lesson on a tie)."""
    best = max(page_parts(n, 5), key=lambda p: (len(set(p) & set(old)), -p.start))
    return min(set(best) & set(old))
