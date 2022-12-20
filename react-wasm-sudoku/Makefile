all: sudoku sudoku-hidden.wasm

sudoku: main.go generate.go
	go build -o $@ $^

sudoku-hidden.wasm: main_js.go generate.go
	GOOS=js GOARCH=wasm go build -o $@ $^

clean:
	rm -f sudoku sudoku-hidden.wasm
