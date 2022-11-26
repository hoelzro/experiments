package main

import (
	"fmt"
	"runtime"
)

type something struct {
	index int
}

func finalizeSomething(s *something) {
	fmt.Printf("finalizing member at %d\n", s.index)
}

type datum struct {
	ptr *something
}

func main() {
	slice := make([]datum, 5)

	for i := 0; i < 5; i++ {
		slice[i].ptr = &something{
			index: i,
		}
	}

	for _, v := range slice {
		runtime.SetFinalizer(v.ptr, finalizeSomething)
	}

	/*
		{
			// keep member 1 alive - or perhaps the whole slice!
			datumPointer := &slice[1]

			fmt.Println("running GC")
			runtime.GC()
			fmt.Println("done running GC")

			runtime.KeepAlive(datumPointer)
		}
	*/

	/*
		{
			// make a subset of the slice reachable
			slice = slice[:1]
			fmt.Println("running GC")
			runtime.GC()
			fmt.Println("done running GC")

			runtime.KeepAlive(slice)
		}
	*/

	{
		// make a subset of the slice reachable
		slice = slice[:1:1]
		fmt.Println("running GC")
		runtime.GC()
		fmt.Println("done running GC")

		runtime.KeepAlive(slice)
	}
}
