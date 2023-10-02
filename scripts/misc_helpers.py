def strip_whitespace_and_more(string_to_strip, non_whitespace_chars_to_strip=""):
    stripped_str = string_to_strip.strip()
    stripped_str = stripped_str.strip(non_whitespace_chars_to_strip)
    while "  " in stripped_str:
        stripped_str = stripped_str.replace("  ", " ")

    return stripped_str

def remove_parentheses_if_fully_enclosed(raw_str):
    cleaned_split_elements = []
    for split_element in raw_str.split(";"):
        # Some strings will have multiple definitions (e.g.) separated by semicolons, esp. if they originally had {"bc"} tags. 
        # We want to remove the parentheses if they're enclosing an entire section of the string between semicolons
        # (or if there are no semicolons, if they are just enclosing the whole string after stripping whitespace)
        white_space_stripped_split_element = strip_whitespace_and_more(split_element, ",;:-|")
        if white_space_stripped_split_element.count("(") == 1 and white_space_stripped_split_element.count(")") == 1 and white_space_stripped_split_element[0] == "(" and white_space_stripped_split_element[-1] == ")":
            cleaned_split_element = split_element.replace("(", "").replace(")", "")
        else:
            cleaned_split_element = split_element
        cleaned_split_elements.append(cleaned_split_element)
    
    cleaned_str = ";".join(cleaned_split_elements)
    
    return cleaned_str