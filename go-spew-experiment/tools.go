//go:build !prod

package main

import "github.com/davecgh/go-spew/spew"

func dump(value any) {
	spew.Dump(value)
}
