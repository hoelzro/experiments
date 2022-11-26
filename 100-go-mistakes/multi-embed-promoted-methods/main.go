package main

import "fmt"

type foo struct {
	value int
}

func (f *foo) Method() {
	fmt.Println("in foo.Method")
}

type bar struct {
	value int
}

func (b *bar) Method() {
	fmt.Println("in bar.Method")
}

type baz struct {
	foo
	bar
}

func main() {
	b := baz{}
	b.Method()
}
