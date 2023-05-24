package main

import (
	"log"
	"net/http"
	"os"
	"strconv"

	_ "embed"
)

//go:embed index.html
var indexHTMLContents []byte

const PageSize = 4_096

func main() {
	memoryChunks := make([][]byte, 0)

	http.HandleFunc("/status", func(w http.ResponseWriter, req *http.Request) {
		procStatus, err := os.ReadFile("/proc/self/status")
		if err != nil {
			log.Printf("unable to read this process' status: %v", err)

			msg := []byte("Internal Server Error\n")
			w.Header().Add("Content-Type", "text/plain")
			w.Header().Add("Content-Length", strconv.Itoa(len(msg)))
			w.WriteHeader(http.StatusInternalServerError)
			w.Write(msg)

			return
		}

		w.Header().Add("Content-Type", "text/plain")
		w.Header().Add("Content-Length", strconv.Itoa(len(procStatus)))
		w.WriteHeader(http.StatusOK)
		w.Write(procStatus)
	})

	http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
		w.Header().Add("Content-Type", "text/html")
		w.Header().Add("Content-Length", strconv.Itoa(len(indexHTMLContents)))
		w.WriteHeader(http.StatusOK)
		w.Write(indexHTMLContents)
	})

	http.HandleFunc("/eat-memory", func(w http.ResponseWriter, req *http.Request) {
		amount := req.FormValue("amount")
		log.Printf("going to start eating %s more memory", amount)

		amountBytes, err := parseMemoryAmount(amount)
		if err != nil {
			log.Printf("unable to parse memory amount: %v", err)

			msg := []byte(err.Error())
			w.Header().Add("Content-Type", "text/plain")
			w.Header().Add("Content-Length", strconv.Itoa(len(msg)))
			w.WriteHeader(http.StatusBadRequest)
			w.Write(msg)

			return
		}

		chunk := make([]byte, amountBytes)
		for i := 0; i < int(amountBytes); i += PageSize {
			chunk[i] = 1
		}
		memoryChunks = append(memoryChunks, chunk)

		msg := []byte("OK")
		w.Header().Add("Content-Type", "text/plain")
		w.Header().Add("Content-Length", strconv.Itoa(len(msg)))
		w.Header().Add("Location", "/")
		w.WriteHeader(http.StatusPermanentRedirect)

		w.Write(msg)
	})

	bindAddress := ":8060"
	log.Printf("listening on %s...", bindAddress)
	err := http.ListenAndServe(bindAddress, nil)
	if err != nil {
		log.Printf("unable to listen on %s: %v", bindAddress, err)
	}
}
