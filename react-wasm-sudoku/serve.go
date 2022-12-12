package main

import (
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
)

func main() {
	addr := ":8000"

	http.Handle("/", http.FileServer(http.Dir(".")))

	wasmExecLocation := filepath.Join(runtime.GOROOT(), "misc", "wasm", "wasm_exec.js")

	http.HandleFunc("/wasm_exec.js", func(w http.ResponseWriter, req *http.Request) {
		http.ServeFile(w, req, wasmExecLocation)
	})

	http.HandleFunc("/sudoku.wasm", func(w http.ResponseWriter, req *http.Request) {
		rebuildWASMCmd := exec.Command("make", "sudoku.wasm")
		rebuildWASMCmd.Stdout = os.Stdout
		rebuildWASMCmd.Stderr = os.Stderr

		err := rebuildWASMCmd.Run()
		if err != nil {
			msg := []byte("unable to build WASM :(")

			log.Println(string(msg))

			w.Header().Add("Content-Type", "text/plain")
			w.Header().Add("Content-Length", strconv.Itoa(len(msg)))
			w.WriteHeader(500)
			w.Write(msg)

			return
		}

		http.ServeFile(w, req, "sudoku.wasm")
	})

	log.Printf("listening on %s", addr)
	err := http.ListenAndServe(addr, nil)
	if err != nil {
		panic(err)
	}
}
