import sys
import random

def neighbors(x, y):
    for other_x in range(9):
        for other_y in range(9):
            if x == other_x and y == other_y:
                continue

            if x == other_x:
                yield (other_x, other_y)
                continue

            if y == other_y:
                yield (other_x, other_y)
                continue

            if (other_x // 3) == (x // 3) and (other_y // 3) == (y // 3):
                yield (other_x, other_y)

NEIGHBORS = {}

for x in range(9):
    for y in range(9):
        NEIGHBORS[(x, y)] = list(neighbors(x, y))

class SudokuGrid:
    def __init__(self):
        self.cells = [ [None] * 9 for _ in range(9) ]

    def render(self):
        return '\n'.join(''.join(str(cell) if cell else ' ' for cell in row) for row in self.cells)

    def _generate_helper(self, cell_order):
        # find all cells that still need a value
        remainder = [ cell for cell in cell_order if self.cells[cell[0]][cell[1]] is None ]

        if not remainder:
            return True

        # find the valid values for each
        valid_values = {}
        for cell in remainder:
            cell_values = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            for other_x, other_y in NEIGHBORS[cell]:
                if v := self.cells[other_x][other_y]:
                    if v in cell_values:
                        cell_values.remove(v)
            valid_values[cell] = cell_values

        # find the cell with the lowest valid value count
        next_cell = min(remainder, key=lambda cell: len(valid_values[cell]))

        # find the value that affects the highest number of neighbors
        candidates = []
        for value in valid_values[next_cell]:
            remove_count = 0
            for other_cell in NEIGHBORS[next_cell]:
                if other_cell in valid_values and value in valid_values[other_cell]:
                    remove_count += 1
            candidates.append((value, remove_count))

        candidates.sort(key=lambda c: c[1])
        candidates.reverse()
        candidates = [ c[0] for c in candidates ]

        # recurse, stopping if we found a solution
        for value in candidates:
            self.cells[next_cell[0]][next_cell[1]] = value

            if self._generate_helper(cell_order):
                return True

        self.cells[next_cell[0]][next_cell[1]] = None
        return False

    def generate(self, seed=None):
        rng = random.Random(seed)

        cells_to_fill = [ (x, y) for x in range(9) for y in range(9) ]
        valid_values = { cell:{1, 2, 3, 4, 5, 6, 7, 8, 9} for cell in cells_to_fill }
        rng.shuffle(cells_to_fill)

        #assert self._generate_helper(cells_to_fill, 0, valid_values), 'no solution found'
        assert self._generate_helper(cells_to_fill), 'no solution found'

if len(sys.argv) > 1:
    seed = int(sys.argv[1])
else:
    import time
    seed = int(time.time())

g = SudokuGrid()
g.generate(seed=seed)
print(g.render())
print(seed)

# 1670605882 finishes quickly
# 1670606006 doesn't finish
# 1670608339 finishes in 1s
# 1670608393 finishes in 3s
