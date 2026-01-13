import string
import random
import datetime

LENGTH = 12


async def get_random_password():
    timestamp = str(datetime.datetime.timestamp(datetime.datetime.now()))
    return (
        "".join(
            random.choice(
                timestamp
                + string.ascii_lowercase
                + string.ascii_uppercase
                + string.punctuation
            )
            for _ in range(LENGTH)
        )
        + timestamp[9:20]
    )
