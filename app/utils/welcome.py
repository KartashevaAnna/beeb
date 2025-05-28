import random

LOGO = "ˁ(OᴥO)ˀ ✲´*。.❄¨¯`*✲。❄。*。ˁ(OᴥO)ˀ"
STARTUP = "Now loading..."
FILLER = "\n" + "*" * 126 + "\n"
QUOTES = [
    "When it is obvious that the goals cannot be reached, don't adjust the goals, adjust the action steps.",  # noqa
    "The greater danger for most of us isn’t that our aim is too high and miss it, but that it is too low and we reach it.",  # noqa
    "A goal without a plan is just a wish.",
    "However difficult life may seem, there is always something you can do and succeed at.",  # noqa
    "If you don’t know where you are going, you are probably end up somwhere else.",  # noqa
    "You can, you should, and if you are brave enough to start, you will.",
    "Begin with the end in mind.",
    "Set a goal so big that you can’t achive it until you grow into the kind of person who can.",  # noqa
    "Glory lies in the attempt to reach one’s goal and not in reaching it.",
    "You are the grim, goal-oriented ones who will not believe that the joy is in the journey rather than the destination no matter how many times it has been proven to you.",  # noqa
    "It is also a natural thing for a serious young man that he should form for himself as precise an idea as possible of the goal of his desires.",  # noqa
    "Without some goal and some effort to reach it, no man can live. When he has lost all hope, all object in life, man becomes a monster in his misery.",  # noqa
    "Go, speed the stars of Thought On to their shining goals; – The sower scatters broad his seed, The wheat thou strew’st be souls.",  # noqa
    "Make at least one definite move daily toward your goal.",
    "Understand and accept that you will have to make sacrifices to achieve your goal. If you are willing to pay the amount, however high, you may be surprised by what you get in exchange. Pay the amount.",  # noqa
    "Shoot for the moon. Even if you miss, you'll land among the stars.",
    "If you aim at nothing, you will hit it every time.",
]

WELCOME_MESSAGE = (
    FILLER + STARTUP + FILLER + LOGO + FILLER + random.choice(QUOTES) + FILLER
)
