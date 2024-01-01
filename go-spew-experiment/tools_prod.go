//go:build prod

package main

import "fmt"

func dump(value any) {
	fmt.Println(value)
}
