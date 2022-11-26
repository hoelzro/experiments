package main

import (
	"fmt"
	"strconv"
)

type customInt int

func (i customInt) String() string {
	return "custom: " + strconv.Itoa(int(i))
}

type customConstraint interface {
	int // deliberately not ~int to see what the error message is
	String() string
}

func printer[T customConstraint](value T) {
	fmt.Println(value.String())
}

func main() {
	c := customInt(12)
	printer(c)
}
