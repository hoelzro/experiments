//go:build !js

package main

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

func main() {
	var seed int64

	if len(os.Args) > 1 {
		var err error
		seed, err = strconv.ParseInt(os.Args[1], 10, 64)
		if err != nil {
			panic(err)
		}
	} else {
		seed = time.Now().Unix()
	}

	g := &sudokuGrid{}
	g.generate(seed, 1)
	fmt.Println(g)
	fmt.Println(seed)
}
