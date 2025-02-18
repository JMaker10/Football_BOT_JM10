import asyncio
import random

async def free_agent_card_age_rating_price():
    card_age = await free_agent_card_age()
    card_rating = await free_agent_card_rating()
    card_price, discount = await free_agent_card_price(card_rating, card_age)
    return card_age, card_rating, int(card_price), discount

async def free_agent_card_age():
    options = [
        30,
        29,
        28,
        21
    ]
    weights = [
        0.6,  # 30
        0.3,    # 29
        0.999,    # 28
        0.001   # 21
    ]

    card_age = random.choices(options, weights=weights, k=1)[0]
    return card_age   

async def free_agent_card_rating():
    options = [
        "90-99",
        "80-89",
        "70-79",
        "60-69"
    ]
    weights = [
        0.001,  # "90-99"
        0.15,    # "80-89"
        0.65,    # "70-79"
        0.199   # "60-69"
    ]

    first_random = random.choices(options, weights=weights, k=1)[0]

    if first_random == "90-99":
        options = [
            99, 98, 97, 96, 95,
            94, 93, 92, 91, 90
        ]
        weights = [
            0.0,    # "99"
            0.0,    # "98"
            0.0,    # "97"
            0.0,    # "96"
            0.0,    # "95"
            0.0,    # "94"
            0.0,    # "93"
            0.0,    # "92"
            0.01,   # "91"
            0.99    # "90"
        ]

        card_rating = random.choices(options, weights=weights, k=1)[0]
        return card_rating

    elif first_random == "80-89":
        options = [
            89, 88, 87, 86, 85,
            84, 83, 82, 81, 80
        ]
        weights = [
            0.001,  # "89"
            0.009,  # "88"
            0.03,   # "87"
            0.06,   # "86"
            0.1,    # "85"
            0.1,    # "84"
            0.1,    # "83"
            0.1,    # "82"
            0.2,    # "81"
            0.3,    # "80"
        ]

        card_rating = random.choices(options, weights=weights, k=1)[0]
        return card_rating
    elif first_random == "70-79":
        options = [
            79, 78, 77, 76, 75,
            74, 73, 72, 71, 70
        ]
        weights = [
            0.001,  # "79"
            0.1,    # "78"
            0.4,    # "77"
            0.3,    # "76"
            0.3,    # "75"
            0.3,    # "74"
            0.4,    # "73"
            0.3,    # "72"
            0.3,    # "71"
            0.3,    # "70"
        ]

        card_rating = random.choices(options, weights=weights, k=1)[0]
        return card_rating

    else:
        card_rating = random.randint(60, 69)
        return card_rating

async def free_agent_card_price(card_rating, card_age):
    if card_rating <= 70:
        first_price = card_rating * 50
    elif 70 < card_rating >= 75:
        first_price = card_rating * 100
    elif 75 < card_rating >= 80:
        first_price = card_rating * 150
    elif 80 < card_rating >= 85:
        first_price = card_rating * 175
    elif 85 < card_rating > 90:
        first_price = card_rating * 225
    else:
        first_price = card_rating * 300
    second_price = (1 + 0.3 * (31 - card_age)) * first_price
    discount_options = [1, 0.98, 0.97, 0.95, 0.9, 0.8, 0.7, 0.5]
    discount_weights = [0.5, 0.1, 0.1, 0.1, 0.1, 0.6, 0.03, 0.01] 
    discount = random.choices(discount_options, weights=discount_weights, k=1)[0]
    card_price = second_price * discount
    return card_price, discount

    