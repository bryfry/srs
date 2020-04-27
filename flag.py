import random

# TODO overwrite value from ENV
FLAG = "IF ONLY IT WERE THAT EASY"


def random_flag_index():
    flag_index = random.randrange(len(FLAG))
    value = FLAG[flag_index]
    return {"index": flag_index, "value": value}
