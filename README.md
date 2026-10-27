# sokobot-
credits: designed and inspected by github:datraveller


# SokoBot

An AI bot that automatically solves [Sokoban](https://en.wikipedia.org/wiki/Sokoban) puzzles. The game is modeled as a state-based search problem, and the solver uses search techniques to find a solution within a fixed time limit.

> Major Course Output 1: De La Salle University

## Table of Contents

- [About Sokoban](#about-sokoban)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Level Format](#level-format)
- [Solver Interface](#solver-interface)
- [Constraints](#constraints)
- [Algorithm Overview](#algorithm-overview)
- [Evaluation](#evaluation)
- [Project Structure](#project-structure)

## About Sokoban

Sokoban (倉庫番, "warehouse keeper") is a classic Japanese puzzle game created by Hiroyuki Imabayashi and first published by Thinking Rabbit in 1981. The player pushes crates around a grid-based warehouse.

**Rules**

1. The player can move in four orthogonal directions (up, down, left, right).
2. The player can only stand on empty spaces or target spaces, and cannot walk through walls.
3. The player can push a crate only if the space behind it is empty. Multiple crates cannot be pushed at once.
4. The player cannot pull crates.
5. The goal is to put all crates on the target spaces.

Despite its simple rules, Sokoban is hard for computers: it has a large branching factor, solutions can be very deep, and the problem is NP-hard.

## Getting Started

### Requirements

- Python 3.9+
- `pygame` (used for the graphical interface)

### Installation

From the project directory, run:

```bash
pip install -r requirements.txt
```

## Usage

The program has two modes: **Free Play** and **SokoBot**. Levels are stored in the `maps` directory and referenced by file name (without the `.txt` extension).

### Free Play Mode

Play a level yourself with the keyboard.

```bash
# Windows
freeplay testlevel

# UNIX-based systems
./freeplay.sh testlevel
```

| Key | Action |
|-----|--------|
| Arrow keys | Move |
| `U` | Undo last move |
| `R` | Restart level |

### SokoBot Mode

Run the bot on a level. By default, the solution string is printed to the console without opening a window.

```bash
# Windows
sokobot testlevel

# UNIX-based systems
./sokobot.sh testlevel
```

To see an animated playback of the solution, add the `--gui` flag and press **Space** to start the bot:

```bash
sokobot testlevel --gui
```

## Level Format

Levels are plain `.txt` files in the `maps` directory, one level per file. They follow the standard [Sokoban level format](http://www.sokobano.de/wiki/index.php?title=Level_format) **without** run-length encoding.

| Character | Meaning |
|-----------|---------|
| `#` | Wall |
| `@` | Player |
| `+` | Player on target |
| `$` | Crate |
| `*` | Crate on target |
| `.` | Target |
| ` ` | Empty floor |

Many levels are included with the starter program, and thousands more can be downloaded online.

## Solver Interface

The solver lives in `src/solver`. The entry point is the `solveSokobanPuzzle` method of the `SokoBot` class:

```python
def solveSokobanPuzzle(self, width, height, mapData, itemsData) -> str
```

**Parameters**

- `width`, `height`: dimensions of the level (integers).
- `mapData`: 2D list of single-character strings holding the **static** elements: `'#'` for a wall, `'.'` for a target.
- `itemsData`: 2D list of single-character strings holding the **movable** elements: `'@'` for the player, `'$'` for a crate.

All other cells are `' '`. Crates and the player may share a location with a target.

**Returns**

A string of moves to be executed in order, using `'u'`, `'d'`, `'l'`, `'r'` for up, down, left, and right.

**Example**

For a level with `width = 7` and `height = 5`:

```python
mapData = [[' ', '#', '#', '#', '#', '#', '#'],
           [' ', '#', ' ', ' ', '.', ' ', '#'],
           ['#', '#', ' ', ' ', ' ', ' ', '#'],
           ['#', '.', '.', ' ', '.', ' ', '#'],
           ['#', '#', '#', '#', '#', '#', '#']]

itemsData = [[' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', '@', ' ', ' ', ' ', ' '],
             [' ', ' ', '$', '$', '$', ' ', ' '],
             [' ', ' ', ' ', ' ', '$', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ']]
```

## Constraints

- **Time limit:** the bot has **15 seconds** to return a solution. If it takes longer, the program discards the result and displays a message that SokoBot took too long thinking.
- **Where to write code:** all solver code goes inside the `src/solver` package. Additional variables, functions, classes, and modules are allowed there. Code in other packages must not be modified.
- **Libraries:** external libraries for data structures (e.g., trees, graphs) are allowed and should be added to `requirements.txt`. Libraries that implement AI algorithms such as search are **not** allowed.
- **Target difficulty:** the bot is designed for levels with roughly **2 to 8 crates**.

## Algorithm Overview

<!-- Fill this in with your own implementation details. -->

- **Algorithm used:** _TODO_
- **State representation:** _TODO_
- **Action generation:** _TODO_
- **Search strategy rationale:** _TODO_
- **Heuristics / evaluation functions:** _TODO_

## Evaluation

<!-- Add your own results here, e.g. a table of levels tested, solved/unsolved, solution length, and time taken. -->

| Level | Crates | Solved | Moves | Time (s) |
|-------|--------|--------|-------|----------|
| _TODO_ | | | | |

## Project Structure

```
.
├── maps/               # Level files (.txt)
├── src/
│   └── solver/         # SokoBot implementation (your code goes here)
├── freeplay.bat / .sh  # Launch Free Play mode
├── sokobot.bat / .sh   # Launch SokoBot mode
└── requirements.txt    # Python dependencies
```

## Authors

- datraveller and WafiDafi
