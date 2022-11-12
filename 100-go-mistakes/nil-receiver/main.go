package main

import "fmt"

type multerror struct {
	errors []error
}

func (err *multerror) Error() string {
	return "many errors"
}

func returnErrorTypeVariable() error {
	var err error

	return err
}

func returnStructPointerVariable() error {
	var err *multerror

	return err
}

func functionReturnTypeStructPointer() *multerror {
	var err *multerror

	return err
}

func main() {
	var err error

	err = returnErrorTypeVariable()
	if err != nil {
		fmt.Println("return variable of type error: not nil?!")
	}

	err = returnStructPointerVariable()
	if err != nil {
		fmt.Println("return variable of type *multerror: not nil?!")
	}

	err = functionReturnTypeStructPointer()
	if err != nil {
		fmt.Println("function return type is *multerror: not nil?!")
	}
}
