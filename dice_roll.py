#!/bin/python3
import argparse
import random
from copy import deepcopy

# Set constants.
INSTRCTN_ARR: list[str] = ['d', 'r', 't', 'l', 'h', 'A', 'D', 'E'] # instrctns.
SPEC_ARR: list[str] = ['r', 't', 'l', 'h'] # list of specs.
SPEC_DEFS: dict[str, int] = {spec: 0 for spec in SPEC_ARR} # spec def. values.
N_FREQTEST: int = int(1e5) # Number of rolls for a frequentist test.
REGULAR_POLYHEDRA: list[int] = [4, 6, 8, 10, 12, 20, 100] # regular polyhedra.

class dice:
    """
    Class for the dice to be rolled.

    args:
        n_faces           : Number of faces in the die.
        n_rolls           : Number of dice to be rolled.
        n_rerolls         : Maximum number of allowed re-rolls, set to -1 for
                            unlimited.
        reroll_threshold  : If roll is equal or lower than this number, re-roll.
        n_lowest_dropped  : Number of the minimum rolls to drop.
        n_highest_dropped : Number of the maximum rolls to drop.
    """
    n_faces: int
    n_rolls: int
    n_rerolls: int = SPEC_DEFS['r']
    reroll_threshold: int = SPEC_DEFS['t']
    n_lowest_dropped: int = SPEC_DEFS['l']
    n_highest_dropped: int = SPEC_DEFS['h']

    def __init__(self, roll: str):
        # Format and sanitize input string.
        dice_arr: list[str] = roll.split('d')
        if dice_arr[0] == '': dice_arr[0] = '1'
        if len(dice_arr) != 2 or not all(map(str.isdigit, dice_arr)):
            raise ValueError("Roll %s is badly formatted." % roll)

        # Initialize dice.
        self.n_rolls, self.n_faces = list(map(int, dice_arr))

    def get(self, s: str) -> int:
        """Get a dice parameter using a char."""
        if s == 'r': return self.n_rerolls
        if s == 't': return self.reroll_threshold
        if s == 'l': return self.n_lowest_dropped
        if s == 'h': return self.n_highest_dropped
        raise ValueError("Invalid spec %s." % s)

    def set(self, s: str, v: int):
        """Set a dice parameter using a char."""
        if s == 'r' and v == 0: self.n_rerolls = -1
        elif s == 'r': self.n_rerolls         = v
        elif s == 't': self.reroll_threshold  = v
        elif s == 'l': self.n_lowest_dropped  = v
        elif s == 'h': self.n_highest_dropped = v
        else: raise ValueError("Invalid spec %s." % s)

    def add_spec(self, spec: str):
        """Define a spec for the dice, checking for errors along the way."""
        val_arr: list[bool] = [bool(spec.find(x)+1) for x in SPEC_ARR]
        if not any(val_arr) or sum(val_arr) != 1:
            raise ValueError("Spec %s is invalid." % spec)
        val: str = SPEC_ARR[val_arr.index(True)]

        if self.get(val) != SPEC_DEFS[val]:
            raise ValueError("Invalid roll. `%s` is set twice." % val)

        spec_arr: list[str] = spec.split(val)
        if len(spec_arr) != 2 or not str.isdigit(spec_arr[1]):
            raise ValueError("Spec %s is badly formatted." % spec)

        self.set(val, int(spec_arr[1]))

    def sanitize(self):
        """Perform a sanitization check on dice."""
        # n_faces.
        if self.n_faces not in (4, 6, 8, 10, 12, 20, 100):
            print("Warning: die is not a regular polyhedron.")

        # n_rolls.
        if self.n_rolls <= 0:
            raise ValueError("Number of rolls should be greater than 0.")

        # n_rerolls and threshold.
        if bool(self.n_rerolls) != bool(self.reroll_threshold):
            raise ValueError("To allow rerolls, set both r and t specs.")
        if self.reroll_threshold >= self.n_faces:
            raise ValueError("Reroll threshold cannot be higher than n_faces.")

        # dropped dice.
        if bool(self.n_lowest_dropped) and bool(self.n_highest_dropped):
            print("Warning: dropping lowest and highest dice. Is that ok?")
        if self.n_lowest_dropped + self.n_highest_dropped > self.n_rolls:
            raise ValueError("More dice dropped than total dice rolled.")

    def roll(self) -> int:
        """Roll one die from the dice object."""
        # Roll the die.
        x: int = random.choice(range(self.n_faces)) + 1

        # Re-roll if needed.
        if x <= self.reroll_threshold and self.n_rerolls != 0:
            self.n_rerolls -= 1
            x = self.roll()

        return x

    def roll_n(self) -> int:
        """Roll all dice in the object."""
        # Roll the dice.
        rolls: list[int] = [self.roll() for _ in range(self.n_rolls)]

        # Remove lowest or highest if needed and rerolls remain.
        for _ in range(self.n_lowest_dropped):  rolls.remove(min(rolls))
        for _ in range(self.n_highest_dropped): rolls.remove(max(rolls))

        # Return sum of rolls.
        return sum(rolls)

    def print(self):
        """Print the dice parameters."""
        print("Dice is:")
        print("  * n_faces           : %d" % self.n_faces)
        print("  * n_rolls           : %d" % self.n_rolls)
        print("  * n_rerolls         : %d" % self.n_rerolls)
        print("  * reroll_threshold  : %d" % self.reroll_threshold)
        print("  * n_lowest_dropped  : %d" % self.n_lowest_dropped)
        print("  * n_highest_dropped : %d" % self.n_highest_dropped)

def run_parser() -> argparse.Namespace:
    """Setup and run the program's parser."""
    DESC: str = ""
    with open("readme.md", 'r') as f:
        DESC = f.read()
    HELP_0: str = "string of rolls to be performed."
    HELP_T: str = "number of times the roll should be performed."
    HELP_F: str = "set this flag to test with 100k rolls."
    parser = argparse.ArgumentParser(
        prog = "dice_roller",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = DESC
    )
    parser.add_argument("rolls", help = HELP_0, type = str, nargs = '+')
    parser.add_argument("-t", "--ntests", help = HELP_T, type = int)
    parser.add_argument("-f", "--freqtest", help = HELP_F, action="store_true")
    return parser.parse_args()

def main() -> int:
    # Parse arguments.
    args: argparse.Namespace = run_parser()

    # Sanitize & Process optional arguments.
    if args.freqtest and args.ntests is not None:
        raise ValueError("--freqtest and --ntests are incompatible args.")
    n_tests: int = 1
    if args.ntests is not None: n_tests = args.ntests
    if args.freqtest:           n_tests = N_FREQTEST

    # Process rolls string.
    dice_arr: list[dice] = []
    for spec in args.rolls:
        # Get instruction.
        instruction: list[bool] = [bool(spec.find(x)+1) for x in INSTRCTN_ARR]

        # Process instruction.
        if sum(instruction) != 1:
            raise ValueError("Input roll is malformed.")
        elif instruction[0]: # 'd'
            dice_arr.append(dice(spec))
        elif len(dice_arr) == 0:
            raise ValueError("Define dice before adding specs to it.")
        elif any(instruction[1:5]): # 'r', 't', 'l', and 'h'.
            dice_arr[-1].add_spec(spec)
        elif any(instruction[5:7]) and dice_arr[-1].n_rolls != 1:
            raise ValueError("A, D, and E only work if n_rolls is 1.")
        elif instruction[5]: # 'A'.
            dice_arr[-1].n_rolls = 2
            dice_arr[-1].add_spec("l1")
        elif instruction[6]: # 'D'.
            dice_arr[-1].n_rolls = 2
            dice_arr[-1].add_spec("h1")
        elif instruction[7]: # 'E'.
            dice_arr[-1].n_rolls = 3
            dice_arr[-1].add_spec("l2")

    # Sanitize dice.
    for d in dice_arr:
        d.sanitize()

    # Print header.
    print("        | ", end = '')
    for d in dice_arr:
        print("%5s " % ("%dd%d" % (d.n_rolls, d.n_faces)), end = '')

    # Roll and print results.
    if n_tests == N_FREQTEST:
        sum_arr: list[int] = [0 for _ in dice_arr]
        # Make rolls and update sum.
        for i_test in range(n_tests):
            for i_die, d in enumerate(dice_arr):
                sum_arr[i_die] += deepcopy(d).roll_n()

        # Print frequentist test result.
        if n_tests == N_FREQTEST:
            print("\nAverage | ", end = '')
            for result in sum_arr:
                print("%5.1f " % (result / n_tests), end = '')

    # Otherwise, roll and print result.
    else:
        for i_test in range(n_tests):
            print("\nRoll %2d | " % (i_test+1), end = '')
            for result in [d.roll_n() for d in deepcopy(dice_arr)]:
                print("%5d " % result, end = '')

    # End the line.
    print('')

    return 0

if __name__ == "__main__":
    main()
