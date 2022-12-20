//go:build js

package main

import (
	"syscall/js"
)

func generateWrapper(this js.Value, args []js.Value) interface{} {
	seed := args[0].Int()
	numBlanks := args[1].Int()
	g := &sudokuGrid{}
	g.generate(int64(seed), numBlanks)

	jsFriendlyCells := make([]interface{}, 9)

	for i, row := range g.cells {
		jsFriendlyRow := make([]interface{}, 9)
		jsFriendlyCells[i] = jsFriendlyRow
		for j, value := range row {
			jsFriendlyRow[j] = value
		}
	}

	return jsFriendlyCells
}

func main() {
	js.Global().Set("generateSudoku", js.FuncOf(generateWrapper))
	<-make(chan int)
}
