import gleam/int
import gleam/io
import gleam/list
import gleam/string

pub type Puzzle = List(List(Int))

pub fn format_puzzle_row(row: List(Int)) -> String {
  string.join(list.map(row, fn(i) {
    "│" <> case i {
      0 -> " "
      _ -> int.to_string(i)
    }
  }), "") <> "│"
}

pub fn format_puzzle(puzzle: Puzzle) -> String {
  let top_row    = "┌─┬─┬─┬─┬─┬─┬─┬─┬─┐"
  let middle_row = "├─┼─┼─┼─┼─┼─┼─┼─┼─┤"
  let bottom_row = "└─┴─┴─┴─┴─┴─┴─┴─┴─┘"
  top_row <> "\n" <> string.join(list.map(puzzle, format_puzzle_row), "\n" <> middle_row <> "\n") <> "\n" <> bottom_row
}

pub fn print_puzzle(puzzle: Puzzle) {
  io.println(format_puzzle(puzzle))
}

pub fn main() {
  let puzzle = [
    [1, 2, 9,   0, 8, 3,   4, 0, 7],
    [6, 0, 0,   0, 1, 5,   0, 0, 0],
    [0, 7, 5,   0, 2, 4,   6, 1, 8],

    [4, 9, 0,   0, 0, 0,   0, 7, 6],
    [0, 3, 7,   0, 4, 0,   0, 0, 0],
    [0, 0, 0,   1, 0, 0,   3, 0, 0],

    [0, 0, 0,   2, 6, 0,   7, 0, 5],
    [9, 0, 0,   0, 7, 0,   0, 0, 0],
    [0, 0, 2,   4, 0, 0,   0, 3, 1],
  ]

  print_puzzle(puzzle)
}
