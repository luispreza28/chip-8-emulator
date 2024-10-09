# CHIP-8 Emulator

## Overview
This project is a CHIP-8 emulator implemented in Python using the Pygame library. It allows users to run CHIP-8 games by loading ROM files and provides a graphical display for the games. The emulator implements all standard CHIP-8 instructions and includes features like sound, input handling, and a GUI for loading ROMs.

## Features
- ROM Loading: Load CHIP-8 games from your file system using a graphical interface.
- Graphics Rendering: Display graphics in a 64x32 pixel resolution, scaled for better visibility.
- Input Handling: Support for keyboard input mapped to the original CHIP-8 keypad.
- Timers: Implement delay and sound timers as per the CHIP-8 specifications.
- Error Handling: Basic error handling for memory access violations.

## Requirements
- Python 3.x
- Pygame library
- Tkinter library (comes pre-installed with Python)
## Installation
### 1. Clone the Repository:

```git clone https://github.com/your-username/chip8-emulator.git```
```cd chip8-emulator```

### 2. Install Dependencies: Make sure you have Pygame installed:

```pip install pygame```

### 3. Run the Emulator: You can run the emulator by executing the main.py file:

```python main.py```

## Usage
1. When you run the emulator, a file dialog will open, allowing you to select a CHIP-8 ROM file (*.ch8).

2. After loading the ROM, the emulator will begin executing the instructions in the loaded program.

3. Use the keyboard to control the game, as described in the Controls section below.

File Structure

chip8-emulator/

│

├── main.py                   # Main emulator script

└── README.md                 # Documentation file

## Supported Instructions
The emulator supports the full set of CHIP-8 instructions, including but not limited to:

- Clear the display
- Draw sprites
- Control timers
- Perform arithmetic and logical operations
- Conditional branching

Please refer to the [CHIP-8 specification](https://en.wikipedia.org/wiki/CHIP-8#Opcode_table) for a complete list of supported instructions.

## Controls
The following keyboard controls are mapped to the CHIP-8 keypad:

1  2  3  C

4  5  6  D

7  8  9  E

A  0  B  F

- 1: 1
- 2: 2
- 3: 3
- C: C
- 4: 4
- 5: 5
- 6: 6
- D: D
- 7: 7
- 8: 8
- 9: 9
- E: E
- A: A
- 0: 0
- B: B
- F: F
  
The emulator will register key presses and pass them to the running ROM.

## Known Issues
- Memory Access Violations: The emulator may print an IndexError message if the program attempts to access memory outside the allocated range.
- Limited ROM Compatibility: Some ROMs may not run perfectly due to variations in their implementation.
  
## Contributors
- Luis Preza – Developer
- CHIP-8 Community – Resources and specifications
