# core/utils.py
import random
import string

def generate_random_password(length=8):
    """Rastgele 8 karakterli, harf ve rakam içeren şifre üretir."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))