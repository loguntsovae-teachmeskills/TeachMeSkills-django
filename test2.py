def is_anagram(s1, s2):
    def without_space(s):
        return s.replace(" ", "").lower()

    s1 = sorted(without_space(s1))
    s2 = sorted(without_space(s2))

    return s1 == s2
    # for i in s1:
    #     if i in s2:
    #         s2 = s2.replace(i, "", count=1)
    #     else:
    #         return False
    # return s2 == ""


assert is_anagram("L  is te n", "Silent")  # true
assert is_anagram("Hello", "Olelh")  # true
assert not is_anagram("Test", "Taste")  # false