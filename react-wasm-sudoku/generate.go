package main

import (
	"math/rand"
	"sort"
	"strconv"
	"strings"
)

type position struct {
	i int
	j int
}

var Neighbors map[position][]position

func neighbors(x, y int) []position {
	n := make([]position, 0, 20) // 20 happens to be the maximum number of neighbors you can have

	for otherX := 0; otherX < 9; otherX++ {
		for otherY := 0; otherY < 9; otherY++ {
			if x == otherX && y == otherY {
				continue
			}

			if x == otherX {
				n = append(n, position{otherX, otherY})
				continue
			}

			if y == otherY {
				n = append(n, position{otherX, otherY})
				continue
			}

			if (otherX/3) == (x/3) && (otherY/3) == (y/3) {
				n = append(n, position{otherX, otherY})
				continue
			}
		}
	}

	return n
}

func init() {
	Neighbors = make(map[position][]position)

	for x := 0; x < 9; x++ {
		for y := 0; y < 9; y++ {
			Neighbors[position{x, y}] = neighbors(x, y)
		}
	}
}

type sudokuGrid struct {
	cells [9][9]int
}

func (g *sudokuGrid) String() string {
	lines := make([]string, 9)

	for i := 0; i < 9; i++ {
		cols := make([]string, 9)
		for j := 0; j < 9; j++ {
			if g.cells[i][j] == 0 {
				cols[j] = " "
			} else {
				cols[j] = strconv.Itoa(g.cells[i][j])
			}
		}
		lines[i] = strings.Join(cols, "")
	}

	return strings.Join(lines, "\n")
}

func (g *sudokuGrid) generateHelper(cells []position) bool {
	remainder := make([]position, 0, 81)
	for _, cell := range cells {
		if g.cells[cell.i][cell.j] == 0 {
			remainder = append(remainder, cell)
		}
	}

	if len(remainder) == 0 {
		return true
	}

	validValues := make(map[position]map[int]struct{})
	for _, cell := range remainder {
		cellValues := map[int]struct{}{
			1: {},
			2: {},
			3: {},
			4: {},
			5: {},
			6: {},
			7: {},
			8: {},
			9: {},
		}

		for _, otherCell := range Neighbors[cell] {
			delete(cellValues, g.cells[otherCell.i][otherCell.j])
		}

		validValues[cell] = cellValues
	}

	var nextCell position
	lowestValidValues := 10
	for _, cell := range remainder {
		cellValues := validValues[cell]
		if len(cellValues) < lowestValidValues {
			nextCell = cell
			lowestValidValues = len(cellValues)
		}
	}

	candidates := make([]int, 0, len(validValues[nextCell]))
	for v := range validValues[nextCell] {
		candidates = append(candidates, v)
	}

	sort.Ints(candidates)

	for _, value := range candidates {
		g.cells[nextCell.i][nextCell.j] = value

		if g.generateHelper(cells) {
			return true
		}
	}

	g.cells[nextCell.i][nextCell.j] = 0

	return false
}

func (g *sudokuGrid) generate(seed int64, numBlanks int) {
	r := rand.New(rand.NewSource(seed))
	cells := make([]position, 0, 81)
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			cells = append(cells, position{i, j})
		}
	}

	r.Shuffle(len(cells), func(i, j int) {
		cells[i], cells[j] = cells[j], cells[i]
	})

	// XXX assert it's true?
	g.generateHelper(cells)

	i := 0
	for numBlanks > 0 {
		cell := cells[i]
		oldValue := g.cells[cell.i][cell.j]
		g.cells[cell.i][cell.j] = 0

		i++

		// if there's more than one solution it's not a valid puzzle, so restore the old value
		// and move on to the next
		if g.numSolutions() > 1 {
			g.cells[cell.i][cell.j] = oldValue
			continue
		}

		numBlanks--
	}
}

func (g *sudokuGrid) numSolutions() int {
	return len(g.findAllSolutions())
}

func (g *sudokuGrid) findAllSolutionsHelper(accum *[]sudokuGrid) {
	// find cells that still need a value
	blankCells := make([]position, 0)
	for i, row := range g.cells {
		for j, value := range row {
			if value == 0 {
				blankCells = append(blankCells, position{i, j})
			}
		}
	}

	// if there are none, we've found a solution
	if len(blankCells) == 0 {
		solution := sudokuGrid{}
		for i, row := range g.cells {
			for j, value := range row {
				solution.cells[i][j] = value
			}
		}

		*accum = append(*accum, solution)
		return
	}

	// calculate valid values for each one
	validValues := make(map[position]map[int]struct{})
	for _, cell := range blankCells {
		cellValues := map[int]struct{}{
			1: {},
			2: {},
			3: {},
			4: {},
			5: {},
			6: {},
			7: {},
			8: {},
			9: {},
		}

		for _, otherCell := range Neighbors[cell] {
			delete(cellValues, g.cells[otherCell.i][otherCell.j])
		}

		validValues[cell] = cellValues
	}

	// find the cell that has the lowest number of valid values
	var nextCell position
	lowestValidValues := 10
	for _, cell := range blankCells {
		cellValues := validValues[cell]
		if len(cellValues) < lowestValidValues {
			nextCell = cell
			lowestValidValues = len(cellValues)
		}
	}

	// for each value, fill in the cell with it and recurse to move on to the next
	for value := range validValues[nextCell] {
		g.cells[nextCell.i][nextCell.j] = value

		g.findAllSolutionsHelper(accum)
	}

	// restore the blank value before returning control to caller to backtrack
	g.cells[nextCell.i][nextCell.j] = 0
}

func (g *sudokuGrid) findAllSolutions() []sudokuGrid {
	var solutions []sudokuGrid

	g.findAllSolutionsHelper(&solutions)

	return solutions
}
