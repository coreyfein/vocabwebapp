def strip_whitespace_and_more(string_to_strip, non_whitespace_chars_to_strip=""):
    stripped_str = string_to_strip.strip()
    stripped_str = stripped_str.strip(non_whitespace_chars_to_strip)
    while "  " in stripped_str:
        stripped_str = stripped_str.replace("  ", " ")
    return stripped_str