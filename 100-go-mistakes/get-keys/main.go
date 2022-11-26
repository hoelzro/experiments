package main

import "fmt"

// just seeing if I can get the type parameter to getKeys be the map, rather than the key
func getKeys[M map[K]V, K comparable, V any](m M) []K {
	keys := make([]K, 0, len(m))

	for k := range m {
		keys = append(keys, k)
	}

	return keys
}

func main() {
	m := map[string]int{
		"foo": 17,
		"bar": 18,
		"baz": 19,
	}

	keys := getKeys[map[string]int](m)
	fmt.Println(keys)
}
