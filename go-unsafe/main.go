package main

import (
	"fmt"
	"unsafe"
)

type myDumbStruct struct {
	first  int
	second int
	third  int
}

type intLike int

func intStuff() {
	i := 0xaabbccdd // 170 187 204 221 - 2864434397
	p := unsafe.Pointer(&i)
	b := *(*[8]byte)(p)
	for i := 0; i < 8; i++ {
		fmt.Printf("%d %d\n", i, b[i])
	}
}

func structStuff() {
	s := myDumbStruct{
		first:  0xaabbccdd, // 170 187 204 221 - 2864434397
		second: 0xeeff1122, // 238 255 17 34  - 4009693474
		third:  0x33445566, // 51 68 85 102 - 860116326
	}

	p := unsafe.Pointer(&s)

	b := *(*[24]byte)(p)

	fmt.Println(unsafe.Sizeof(s))
	fmt.Println("")

	for i := 0; i < 24; i++ {
		fmt.Printf("%d %d\n", i, b[i])
	}
}

func newtypeStuff() {
	i := 0xaabbccdd // 170 187 204 221 - 2864434397
	il := intLike(i)

	fmt.Printf("sizeof(int): %d\n", unsafe.Sizeof(i))
	fmt.Printf("sizeof(intLike): %d\n", unsafe.Sizeof(il))

	fmt.Println("")
	fmt.Println("int bytes:")
	{
		p := unsafe.Pointer(&i)
		b := *(*[8]byte)(p)
		for i := 0; i < 8; i++ {
			fmt.Printf("%d %d\n", i, b[i])
		}
	}

	fmt.Println("")
	fmt.Println("intLike bytes:")
	{
		p := unsafe.Pointer(&il)
		b := *(*[8]byte)(p)
		for i := 0; i < 8; i++ {
			fmt.Printf("%d %d\n", i, b[i])
		}
	}
}

func interfaceStuff() {
	i := 0xaabbccdd // 170 187 204 221 - 2864434397
	i2 := 0xddccbbaa
	il := intLike(i)
	il2 := intLike(i2)

	{
		var a any

		a = i
		b := *(*[2]int)(unsafe.Pointer(&a))
		fmt.Println("int-as-any values:")
		fmt.Println("")

		for i, v := range b {
			fmt.Printf("%2d %x\n", i, v)
		}
		fmt.Println("")
		fmt.Printf("value of second int: %x\n", **(**int)(unsafe.Pointer(&b[1])))
	}

	{
		var a any

		a = i2
		b := *(*[2]int)(unsafe.Pointer(&a))
		fmt.Println("")
		fmt.Println("int-as-any values (take 2):")
		fmt.Println("")

		for i, v := range b {
			fmt.Printf("%2d %x\n", i, v)
		}

		fmt.Println("")
		fmt.Printf("value of second int: %x\n", **(**int)(unsafe.Pointer(&b[1])))
	}

	{
		var a any

		a = il
		b := *(*[2]int)(unsafe.Pointer(&a))

		fmt.Println("")
		fmt.Println("intLike-as-any values:")
		fmt.Println("")

		for i, v := range b {
			fmt.Printf("%2d %x\n", i, v)
		}

		fmt.Println("")
		fmt.Printf("value of second int: %x\n", **(**int)(unsafe.Pointer(&b[1])))
	}

	{
		var a any

		a = il2
		b := *(*[2]int)(unsafe.Pointer(&a))

		fmt.Println("")
		fmt.Println("intLike-as-any values (take 2):")
		fmt.Println("")

		for i, v := range b {
			fmt.Printf("%2d %x\n", i, v)
		}

		fmt.Println("")
		fmt.Printf("value of second int: %x\n", **(**int)(unsafe.Pointer(&b[1])))
	}
}

func main() {
	interfaceStuff()
}
