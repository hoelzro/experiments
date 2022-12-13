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

//export generateSudoku
func (g *sudokuGrid) generate(seed int64) {
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
}
