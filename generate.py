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
        # Loop thru all keys in self.domains dictionary
        for var in self.domains:
            # Loop thru all values in the keys and remove inconsistent values
            for word in self.domains[var].copy():
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]
        if overlap != None:
            for x_word in self.domains[x].copy(): # Must use a copy to avoid changing the original while iterating
                count = 0
                for y_word in self.domains[y]:
                    if x_word[overlap[0]] == y_word[overlap[1]]:
                        break
                    else:
                        count += 1
                        continue
                if count == len(self.domains[y]):
                    self.domains[x].remove(x_word)
                    revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Create a list of arcs if None have been provided
        if arcs == None:
            arcs = []
            for key, value in self.crossword.overlaps.items():
                if value != None:
                    arcs.append(key)

        # Make every item in arcs consistent and add new arcs as needed
        while len(arcs) != 0:
            (x,y) = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.crossword.variables) == len(assignment.keys()):
            return True
        else:
            return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check that all values are unique:
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # Check that every value is the correct length
        for key, value in assignment.items():
            if key.length != len(value):
                return False

        # Check that the letters are the same in neighboring values
        overlaps = self.crossword.overlaps
        for var1 in assignment:
            for var2 in assignment:
                if var1 == var2:
                    continue
                overlap = self.crossword.overlaps[var1, var2]
                if overlap != None:
                    if assignment[var1][overlap[0]] != assignment[var2][overlap[1]]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # First, make a list of values from domains
        # Then, find if variable has any neighbors
        # Next, find overlap in variables using self.crossword.overlaps
        # *Don't count any neighboring variable already in "assignment"
        # Last, return a list of values that rules out the fewest values among neighbors in ascending order

        # Make a dictionary for words in domains. Key is word, value is number of eliminations
        values = {}
        neighbors = list(self.crossword.neighbors(var))
        for word in self.domains[var]:
            count = 0
            for neighbor in neighbors:
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for neighbor_word in self.domains[neighbor]:
                        if word[i] != neighbor_word[j]:
                            count +=1
            values[word] = count

        # Sort by ascending order
        sorted_values = sorted(values.items(), key=lambda x:x[1]) # lambda returns a list of tuples as (key, value)
        values_list = []
        for value in sorted_values:
                values_list.append(value[0])

        return values_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # First, need a list of all var's yet assigned
        # Next, need variables with the least number of words in domain
        # Last, sort the variables by the highest number of neighbors
        # Return the key with the least number of words and the highest number of neighbors

        # Make dictionary, key is variables with lowest domain, value is # of neighbors
        neighbors = {}

        # Arbitrary high number to set the initial domain count at
        dom_count = 3000

        # Look for variables not already assigned
        for var in self.crossword.variables:
            if var not in assignment.keys():

                # Count the number of remaining domains
                rem_doms = len(self.domains[var])

                # If variable has the same domains as the lowest, add to dictionary
                if rem_doms == dom_count:
                    neighbors[var] = len(self.crossword.neighbors(var))

                # If there is a new low in domains, clear the dictionary and add the variable
                elif rem_doms < dom_count:
                    neighbors.clear()
                    neighbors[var] = len(self.crossword.neighbors(var))
                    dom_count = rem_doms

        # Sort and select the variable with the highest number of neighbors
        sorted_neighbors = sorted(neighbors.items(), key=lambda x:x[1], reverse=True) # lambda returns a list of tuples as (key, value)

        return sorted_neighbors[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, return assignment
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Consider all the values in this variable's domain
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            del assignment[var]

        return None


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
