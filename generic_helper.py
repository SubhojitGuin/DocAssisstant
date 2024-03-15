import re


def extract_session_id(session_str: str):
    match = re.search(r'sessions/(.*?)/contexts', session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""


def get_str_from_food_dict(food_dict: dict):
    result = ", ".join([f"{key}" for key, value in food_dict.items()])
    return result


if __name__ == "__main__":
    print(extract_session_id(
        "/sessions/a572d7b2-24aa-ac32-adfb-2b8e760dca98/contexts/"))  # 123456789
#     print(extract_session_id("/sessions/987654321/contexts/")) # 987654321
#     print(extract_session_id("123456789/contexts/")) # ""
#     print(get_str_from_food_dict({"pizza": 2, "burger": 3}))
