import sys

from crossword import *

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #  self.domains is dict item, (key, value) = (Variable obj, possible words)
        for v in self.domains:
            for x in self.domains[v].copy():
                if len(x) != v.length:
                    self.domains[v].remove(x)

    def revise(self, x, y, assignment):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        constraint = self.crossword.overlaps[x, y]
        if constraint is not None:

            for x_word in self.domains[x].copy():
                count = 0
                if assignment is not None and y in assignment:
                    y_word = assignment[y]
                    if x_word[constraint[0]] == y_word[constraint[1]]:
                        count += 1
                else:
                    for y_word in self.domains[y]:
                        if x_word[constraint[0]] == y_word[constraint[1]]:
                            count += 1
                if count == 0:
                    self.domains[x].remove(x_word)
                    revised = True
        return revised

    def ac3(self, assignment=None, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [i for i in self.crossword.overlaps if self.crossword.overlaps[i] is not None]
        while not not arcs:
            choice = arcs.pop(-1)
            if self.revise(choice[0], choice[1], assignment):
                if not self.domains[choice[0]]:
                    return False
                self.crossword.neighbors(choice[0]).remove(choice[1])
                for neighbor in self.crossword.neighbors(choice[0]):
                    arcs.append((neighbor, choice[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if not assignment:
            return False
        k = 0
        for key in assignment:
            if assignment[key] is not None:
                k += 1
        if len(self.domains) != k:
            return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        set_assignment = set()
        num_assignment = 0
        constraint = self.crossword.overlaps
        overlaps = [i for i in constraint if constraint[i] is not None]
        for key in assignment:
            if not not assignment[key]:
                num_assignment += 1
                if len(assignment[key]) != key.length:
                    return False
                set_assignment.add(assignment[key])
        if len(set_assignment) != num_assignment:
            return False

        for overlap in overlaps:
            x, y = constraint[overlap]
            var1, var2 = overlap
            if var1 in assignment and var2 in assignment:
                if assignment[var1][x] != assignment[var2][y]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        choicedict = dict.fromkeys(self.domains[var], None)
        for x_choice in choicedict:
            ruled_out = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment and assignment[neighbor] is not None:
                    continue
                x, y = self.crossword.overlaps[var, neighbor]
                for y_choice in self.domains[neighbor]:
                    if x_choice[x] != y_choice[y]:
                        ruled_out += 1
            choicedict[x_choice] = ruled_out

        sorted_dict = sorted(choicedict.items(), key=lambda x: x[1])
        sorted_list = [i[0] for i in sorted_dict]

        return sorted_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [key for key in self.domains if key not in assignment]
        unassigned_dict = dict.fromkeys(unassigned, None)
        for key in unassigned_dict:
            unassigned_dict[key] = len(self.domains[key])
        sorted_dict = sorted(unassigned_dict.items(), key=lambda x: x[1])
        choicelist = [sorted_dict[0][0]]
        for i in sorted_dict:
            if i[-1] == sorted_dict[0][-1]:
                choicelist.append(i[0]) if i[0] not in choicelist else None

        if len(choicelist) > 1:
            shortlist = dict.fromkeys(choicelist, None)
            for key in shortlist:
                shortlist[key] = len(self.crossword.neighbors(key))
            choicelist = sorted(shortlist.items(), key=lambda x: x[1], reverse=True)
            choicelist = [key[0] for key in choicelist]
        return choicelist[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            c_assignment = assignment.copy()
            c_assignment[var] = value
            if self.consistent(c_assignment):
                assignment[var] = value
                new_arcs = [i for i in self.crossword.overlaps if self.crossword.overlaps is not None]
                for i in assignment:
                    for arc in new_arcs:
                        new_arcs.remove(arc) if i not in arc else None
                self.ac3(assignment=assignment, arcs=new_arcs)
                result = self.backtrack(assignment)
                if result is not False:
                    return result
                del assignment[var]
        return False


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
