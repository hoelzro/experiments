package main

import (
	"fmt"
	"strconv"
)

type convertor[T, U any] interface {
	Convert(T) U
}

type intStrConvertor struct{}

func (*intStrConvertor) Convert(value int) string {
	return strconv.Itoa(value)
}

func convert[T, U any](conv convertor[T, U], values []T) []U {
	newValues := make([]U, len(values))

	for i, value := range values {
		newValues[i] = conv.Convert(value)
	}

	return newValues
}

func main() {
	ints := []int{1, 1, 2, 3, 5, 8}
	strs := convert[int, string](&intStrConvertor{}, ints)
	fmt.Println(strs)
}
