import random
import string

def get_random_string(length=4):
    # Includes a-z, A-Z, and 0-9
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))