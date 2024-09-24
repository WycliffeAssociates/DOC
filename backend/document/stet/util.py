def is_valid_int(text: str) -> bool:
    try:
        int(text)
        return True
    except ValueError:
        return False
