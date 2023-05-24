package main

import "testing"

type parseTest struct {
	input          string
	expectedOutput uint64
}

func TestParse(t *testing.T) {
	tests := []parseTest{
		{"1k", 1_000},
		{"1m", 1_000_000},
		{"1g", 1_000_000_000},

		{"1K", 1_000},
		{"1M", 1_000_000},
		{"1G", 1_000_000_000},

		{"1kb", 1_000},
		{"1mb", 1_000_000},
		{"1gb", 1_000_000_000},

		{"1KB", 1_000},
		{"1MB", 1_000_000},
		{"1GB", 1_000_000_000},

		{"1ki", 1 << 10},
		{"1mi", 1 << 20},
		{"1gi", 1 << 30},

		{"1Ki", 1 << 10},
		{"1Mi", 1 << 20},
		{"1Gi", 1 << 30},

		{"1kib", 1 << 10},
		{"1mib", 1 << 20},
		{"1gib", 1 << 30},

		{"1KiB", 1 << 10},
		{"1MiB", 1 << 20},
		{"1GiB", 1 << 30},
	}

	for _, test := range tests {
		got, err := parseMemoryAmount(test.input)
		if err != nil {
			t.Logf("Got error when parsing %q: %v", test.input, err)
			t.FailNow()
		}

		if got != test.expectedOutput {
			t.Logf("Output for %q was wrong", test.input)
			t.Logf("  Got:      %v", got)
			t.Logf("  Expected: %v", test.expectedOutput)
			t.FailNow()
		}
	}
}
