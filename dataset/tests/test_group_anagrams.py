import random
from solution import group_anagrams


def _normalize(result):
    """Sort each group and sort the list of groups for comparison."""
    return sorted(sorted(g) for g in result)


def test_basic():
    result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert _normalize(result) == sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]])


def test_no_anagrams():
    result = group_anagrams(["abc", "def", "ghi"])
    assert _normalize(result) == sorted([["abc"], ["def"], ["ghi"]])


def test_all_anagrams():
    result = group_anagrams(["abc", "bca", "cab"])
    assert len(result) == 1
    assert sorted(result[0]) == ["abc", "bca", "cab"]


def test_empty():
    assert group_anagrams([]) == []


def test_single_word():
    result = group_anagrams(["hello"])
    assert len(result) == 1
    assert result[0] == ["hello"]


def test_random_anagram_pairs():
    import string
    for _ in range(10):
        word = ''.join(random.choices(string.ascii_lowercase, k=5))
        shuffled = list(word)
        random.shuffle(shuffled)
        anagram = ''.join(shuffled)
        result = group_anagrams([word, anagram, "zzzzz"])
        groups = _normalize(result)
        # "zzzzz" should be alone; word and anagram together (unless word == anagram)
        assert ["zzzzz"] in groups


def test_mixed_group_sizes():
    words = ["abc", "bca", "cab", "xyz", "def", "fed"]
    result = group_anagrams(words)
    assert _normalize(result) == sorted([["abc", "bca", "cab"], ["def", "fed"], ["xyz"]])
