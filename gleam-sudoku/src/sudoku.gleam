import gleam/dict
import gleam/int
import gleam/io
import gleam/iterator
import gleam/list
import gleam/option.{type Option, None, Some}
import gleam/set
import gleam/string

pub type Puzzle =
  List(List(Int))

pub fn format_puzzle_row(row: List(Int)) -> String {
  string.join(
    list.map(row, fn(i) {
      "│"
      <> case i {
        0 -> " "
        _ -> int.to_string(i)
      }
    }),
    "",
  )
  <> "│"
}

pub fn format_puzzle(puzzle: Puzzle) -> String {
  let top_row = "┌─┬─┬─┬─┬─┬─┬─┬─┬─┐"
  let middle_row = "├─┼─┼─┼─┼─┼─┼─┼─┼─┤"
  let bottom_row = "└─┴─┴─┴─┴─┴─┴─┴─┴─┘"
  top_row
  <> "\n"
  <> string.join(
    list.map(puzzle, format_puzzle_row),
    "\n" <> middle_row <> "\n",
  )
  <> "\n"
  <> bottom_row
}

pub fn print_puzzle(puzzle: Puzzle) {
  io.println(format_puzzle(puzzle))
}

pub fn row_neighbors(row: Int, _col: Int) -> List(#(Int, Int)) {
  list.map(list.range(0, 8), fn(neighbor_col) { #(row, neighbor_col) })
}

pub fn col_neighbors(_row: Int, col: Int) -> List(#(Int, Int)) {
  list.map(list.range(0, 8), fn(neighbor_row) { #(neighbor_row, col) })
}

pub fn block_neighbors(row: Int, col: Int) -> List(#(Int, Int)) {
  let start_row = row - row % 3
  let start_col = col - col % 3
  let rows = list.range(start_row, start_row + 2)
  let cols = list.range(start_col, start_col + 2)

  list.flat_map(rows, fn(row) { list.map(cols, fn(col) { #(row, col) }) })
}

pub fn update_puzzle(
  puzzle: Puzzle,
  target_row_num: Int,
  target_col_num: Int,
  new_value: Int,
) -> Puzzle {
  list.index_map(puzzle, fn(row, row_num) {
    case row_num == target_row_num {
      False -> row
      True ->
        list.index_map(row, fn(col, col_num) {
          case col_num == target_col_num {
            False -> col
            True -> new_value
          }
        })
    }
  })
}

pub fn solve_puzzle(puzzle: Puzzle) -> Option(Puzzle) {
  // XXX strip out 0s?
  let current_values =
    dict.from_list(
      list.flatten(
        list.index_map(puzzle, fn(row, row_num) {
          list.index_map(row, fn(value, col_num) {
            #(#(row_num, col_num), value)
          })
        }),
      ),
    )

  let possible_values =
    list.flatten(
      list.index_map(puzzle, fn(row, row_num) {
        list.index_map(row, fn(_cell, col_num) {
          let neighbors =
            list.concat([
              row_neighbors(row_num, col_num),
              col_neighbors(row_num, col_num),
              block_neighbors(row_num, col_num),
            ])
          // XXX can I partially apply dict.get here?
          let neighbor_values =
            list.filter_map(neighbors, fn(n) { dict.get(current_values, n) })
          let possible_cell_values =
            set.drop(set.from_list(list.range(1, 9)), neighbor_values)
          #(#(row_num, col_num), possible_cell_values)
        })
      }),
    )

  let possible_values =
    list.filter(possible_values, fn(pair) {
      // XXX this could be !dict.has_key(current_values, pair.0)
      //     if I strip 0s out of current_values above
      case dict.get(current_values, pair.0) {
        // XXX does this ordering matter?
        Ok(0) -> True
        Ok(_) -> False
        Error(_) -> True
      }
    })

  let possible_values =
    list.sort(possible_values, fn(a, b) {
      // XXX destructuring bind
      int.compare(set.size(a.1), set.size(b.1))
    })

  case possible_values {
    [] -> Some(puzzle)
    // XXX verify that it's actually solved!
    [#(#(row, col), cell_values), ..] -> {
      // XXX hopefully this is actually lazy?
      let lazy_solutions =
        iterator.filter_map(
          iterator.from_list(set.to_list(cell_values)),
          fn(value) {
            // XXX partial application?
            option.to_result(
              solve_puzzle(update_puzzle(puzzle, row, col, value)),
              False,
            )
            // XXX False is a dummy placeholder - unit type?
          },
        )
      option.from_result(iterator.first(lazy_solutions))
    }
  }
}

pub fn main() {
  let puzzle = [
    [1, 2, 9, 0, 8, 3, 4, 0, 7],
    [6, 0, 0, 0, 1, 5, 0, 0, 0],
    [0, 7, 5, 0, 2, 4, 6, 1, 8],
    [4, 9, 0, 0, 0, 0, 0, 7, 6],
    [0, 3, 7, 0, 4, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 3, 0, 0],
    [0, 0, 0, 2, 6, 0, 7, 0, 5],
    [9, 0, 0, 0, 7, 0, 0, 0, 0],
    [0, 0, 2, 4, 0, 0, 0, 3, 1],
  ]

  case solve_puzzle(puzzle) {
    None -> io.println("unable to find solution :(")
    Some(solution) -> print_puzzle(solution)
  }
}
