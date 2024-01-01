package main

import (
	"fmt"
)

func main() {
	dumbThing := map[string]int{
		"foo": 17,
	}

	dump(dumbThing)
	fmt.Println(dumbThing)
}
