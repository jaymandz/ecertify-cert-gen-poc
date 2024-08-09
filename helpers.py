import random
import string

from models import Recipient, db

def generate_token():
    while True:
        token = ''.join(random.choice(string.ascii_letters) for _ in range(13))
        query = db.select(Recipient).where(Recipient.token==token)
        if not db.session.execute(query).scalar_one_or_none():
            break
    return token