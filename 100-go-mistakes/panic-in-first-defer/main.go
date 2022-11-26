package main

import "fmt"

func foo() {
	panic("dang")
}

func bar() {
	defer func() {
		fmt.Println("In first bar defer")
	}()

	defer func() {
		fmt.Println("In second bar defer")
		panic("crap")
	}()

	foo()
}

func baz() {
	defer func() {
		fmt.Println("In baz defer")
	}()

	bar()
}

func main() {
	baz()
}
