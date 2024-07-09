import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells equals the count and the count is not zero,
        # all cells in the set are known to be mines.
        if self.count == len(self.cells) and self.count != 0:
            return self.cells
        # Otherwise, return an empty set indicating no known mines.
        return set()
    
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is zero, all cells in the set are known to be safe
        if self.count == 0:
            return self.cells
        # Otherwise, return an empty set indicating no known safe cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # Remove the cell from the set.
            self.cells.remove(cell)
            # Decrease the count of mines by one
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Remove the cell from the set if cell is in the set of cells for this sentence
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1. Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2. Mark the cell as safe
        self.mark_safe(cell)

        # 3. Add a new sentence to the AI's knowledge base
        # Initialize an empty set to store neighboring cells
        new_cells = set()

        # Unpack the coordinates of the current cell
        row, col = cell
        known_mines_count = 0

        # Iterate over the neighboring cells
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                # Skip the current cell itself
                if drow == 0 and dcol == 0:
                    continue
                
                # Calculate the coordinates of the neighboring cell
                neighbor = (row + drow, col + dcol)
                # Check if the neighboring cell is within the bounds of the board
                if 0 <= neighbor[0] < self.height and 0 <= neighbor[1] < self.width:
                    # Check if the neighboring cell is a known mine
                    if neighbor in self.mines:
                        known_mines_count += 1
                    # Add the neighboring cell to the set if it is not already known to be safe
                    elif neighbor not in self.safes:
                        new_cells.add(neighbor)
        
        if new_cells:
            # Create a new sentence with the neighboring cells and the mine count
            new_sentence = Sentence(new_cells, count - known_mines_count)
            # Add the new sentence to the AI's knowledge base
            self.knowledge.append(new_sentence)

         # 4. Mark any additional cells as safe or as mines
        self.update_knowledge()

        # 5. Add any new sentences to the AI's knowledge base
        self.infer_new_sentences()

    def update_knowledge(self):
        """
        Update the AI's knowledge base, marking any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base.
        """
        knowledge_updated = True
        while knowledge_updated:
            knowledge_updated = False
            safes = set()
            mines = set()
            
            # Identify known safes and mines from current knowledge
            for sentence in self.knowledge:
                safes = safes.union(sentence.known_safes())
                mines = mines.union(sentence.known_mines())
            
            # Mark identified safes and mines
            if safes:
                knowledge_updated = True
                for safe in safes:
                    self.mark_safe(safe)

            if mines:
                knowledge_updated = True
                for mine in mines:
                    self.mark_mine(mine)

            # Remove empty sentences from knowledge base
            self.knowledge = [sentence for sentence in self.knowledge if sentence.cells]


    def infer_new_sentences(self):
        """
        Infer new sentences based on existing knowledge.
        """
        new_knowledge = []
        # Iterate over pairs of sentences
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2:
                    continue
                # If one sentence is a subset of another, create a new inferred sentence
                if sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in new_knowledge:
                        new_knowledge.append(new_sentence)
        # Add inferred sentences to knowledge base
        self.knowledge.extend(new_knowledge)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Return the first safe move that has not been made
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Initialize an empty list to store potential moves
        choices = []

        # Iterate over all cells in the board
        for i in range(self.height):
            for j in range(self.width):
                # If the cell has not been chosen and is not known to be a mine,
                # add it to the list of potential moves
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                    choices.append((i,j))
        
        # If there are potential moves available, choose one randomly
        if choices:
            return random.choice(choices)
        
        # If no valid moves are available, return None
        return None