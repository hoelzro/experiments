package main

import (
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
)

func main() {
	network := "tcp"
	addr := ":8000"

	if len(os.Args) > 1 {
		addr = os.Args[1]
	}

	if !regexp.MustCompile(`^:\d+$`).MatchString(addr) {
		network = "unix"
	}

	listener, err := net.Listen(network, addr)
	if err != nil {
		panic(err)
	}

	http.Handle("/", http.FileServer(http.Dir(".")))

	wasmExecLocation := "/usr/lib/tinygo/targets/wasm_exec.js"

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

	log.Printf("listening on %s", listener.Addr())
	err = http.Serve(listener, nil)
	if err != nil {
		panic(err)
	}
}
