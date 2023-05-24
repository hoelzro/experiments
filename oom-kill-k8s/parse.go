package main

import (
	"errors"
	"math"
	"strconv"
	"strings"
)

func parseMemoryAmount(s string) (uint64, error) {
	type unitSuffix struct {
		suffix             string
		multiplierExponent int
	}

	suffixes := []unitSuffix{
		{"k", 1},
		{"m", 2},
		{"g", 3},
	}

	s = strings.ToLower(s)
	for _, us := range suffixes {
		multiplier := uint64(0)

		if strings.HasSuffix(s, us.suffix) || strings.HasSuffix(s, us.suffix+"b") {
			multiplier = uint64(math.Pow10(3 * us.multiplierExponent))
		} else if strings.HasSuffix(s, us.suffix+"i") || strings.HasSuffix(s, us.suffix+"ib") {
			multiplier = uint64(1) << (10 * us.multiplierExponent)
		}

		if multiplier == 0 {
			continue
		}

		s = strings.TrimSuffix(s, "b")
		s = strings.TrimSuffix(s, "i")
		s = strings.TrimSuffix(s, us.suffix)

		base, err := strconv.ParseUint(s, 10, 64)
		if err != nil {
			return 0, err
		}
		return base * multiplier, nil
	}

	return 0, errors.New("unable to find pattern for memory amount")
}
