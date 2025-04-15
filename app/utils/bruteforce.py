import itertools
import string

def brute_force_password(target_password, max_length=5):
    chars = string.ascii_lowercase + string.digits
    for length in range(1, max_length + 1):
        for attempt in itertools.product(chars, repeat=length):
            attempt_password = ''.join(attempt)
            if attempt_password == target_password:
                return attempt_password
    return None