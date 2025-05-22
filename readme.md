# Dice roller
Perform a number of rolls following common ttrpg rules. The
rolls should be given to the program as a string, which is
formatted as

        AdX [...] BdY [...] CdZ [...]

where this roll would be of A X-sided dice, B Y-sided dice,
and C Z-sided dice. If you only want to roll one dice, you
can ignore the first number (A, B, and C in the example).

In addition to the dice roll itself, the string accepts a
number of different arguments, such that one roll can be:

AdX [rR] [tT] [lL] [hH] [A] [D] [E]
* AdX   : Roll a number of A X-sided dice.
* rR tT : Re-roll all rolls that result in a number equal or
          lower than T. The maximum number of rerolls allow-
          ed is R. You can set R to 0 to allow for infinite
          re-rolls.
* lL    : Drop the L lowest dice in the roll.
* hH    : Drop the H highest dice in the roll.
* The following optional arguments are mutually exclusive,
and are only available if the roll is a d20/1d20:
    * A : Roll with advantage (2d20 l1).
    * D : Roll with disadvantage (2d20 h1).
    * E : Roll with advantage + the Elven Accuracy feat
          (3d10 l3).
