all: sudoku sudoku-hidden.wasm

sudoku: main.go generate.go
	go build -o $@ $^

sudoku-hidden.wasm: main_js.go generate.go
	tinygo build -stack-size=32KB -o $@ -target wasm .

clean:
	rm -f sudoku sudoku-hidden.wasm
