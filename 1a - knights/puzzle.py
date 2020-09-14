from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Puzzle 0
# A says "I am both a knight and a knave."
Asays0 = And(AKnight, AKnave)

knowledge0 = And(
    # Rule
    Not(Biconditional(AKnight, AKnave)),

    # Sentences
    Implication(AKnight, Asays0),
    Implication(AKnave, Not(Asays0))
)


# Puzzle 1
# A says "We are both knaves."
Asays1 = And(AKnave, BKnave)

# B says nothing.
knowledge1 = And(
    # Rules
    Not(Biconditional(AKnight, AKnave)),
    Not(Biconditional(BKnight, BKnave)),

    # Sentences
    Implication(AKnight, Asays1),
    Implication(AKnave, Not(Asays1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
Asays2 = Or(And(AKnave, BKnave), And(AKnight, BKnight))
Bsays2 = Or(And(AKnave, BKnight), And(AKnight, BKnave))

knowledge2 = And(
    # Rules
    Not(Biconditional(AKnight, AKnave)),
    Not(Biconditional(BKnight, BKnave)),

    # Sentences
    Implication(AKnight, Asays2),
    Implication(AKnave, Not(Asays2)),
    Implication(BKnight, Bsays2),
    Implication(BKnave, Not(Bsays2))

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

Asays3 = Or(AKnight, AKnave)
BsaysA = AKnave
Bsays3a = Or(Implication(BsaysA, AKnight),
             Implication(Not(BsaysA), AKnave))
Bsays3b = CKnave
Csays3 = AKnight

knowledge3 = And(
    # Rules
    Not(Biconditional(AKnight, AKnave)),
    Not(Biconditional(BKnight, BKnave)),
    Not(Biconditional(CKnight, CKnave)),

    # Sentences
    Implication(AKnight, Asays3),
    Implication(AKnave, Not(Asays3)),
    Implication(BKnight, And(Bsays3a, Bsays3b)),
    Implication(BKnave, Not(And(Bsays3a, Bsays3b))),
    Implication(CKnight, Csays3),
    Implication(CKnave, Not(Csays3))

)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")




if __name__ == "__main__":
    main()
