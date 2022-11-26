package main

import "fmt"

type lock struct{}

func (l *lock) Lock() {
	fmt.Println("locking")
}

func (l *lock) Unlock() {
	fmt.Println("unlocking")
}

type lockNoMethods lock

type protectedValue struct {
	lockNoMethods
	value int
}

func (pv *protectedValue) Get() int {
	pv.lockNoMethods.Lock()
	defer pv.lockNoMethods.Unlock()

	return pv.value
}

func main() {
	pv := protectedValue{value: 17}
	fmt.Println(pv.Get())
}
