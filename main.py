import pygame
import random
import tkinter as tk
from tkinter import filedialog
import sys

# Constants
MEMORY_SIZE = 4096
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
KEYS_COUNT = 16
REGISTER_COUNT = 16
START_ADDRESS = 0x200
SPRITE_SIZE = 5

# Initialize memory, registers, and other components
memory = [0] * MEMORY_SIZE
V = [0] * REGISTER_COUNT
I = 0
pc = START_ADDRESS
stack = []
delay_timer = 0
sound_timer = 0
display = [[0] * DISPLAY_WIDTH for _ in range(DISPLAY_HEIGHT)]
keys = [0] * KEYS_COUNT

CHIP8_KEYS = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
}


# load the ROM
def load_rom(file_path):
    with open(file_path, 'rb') as f:
        rom = f.read()
    if START_ADDRESS + len(rom) > MEMORY_SIZE:
        raise MemoryError("ROM size exceeds available memory space")
    memory[START_ADDRESS:START_ADDRESS + len(rom)] = rom


# clear display
def clear_display():
    global display
    display = [[0] * DISPLAY_WIDTH for _ in range(DISPLAY_HEIGHT)]


# decode and execute
def execute_opcode(opcode):
    global pc, I, stack, delay_timer, sound_timer, display, V

    def skip_instruction():
        global pc
        pc += 4

    def next_instruction():
        global pc
        pc += 2

    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4
    nn = opcode & 0x00FF
    nnn = opcode & 0x0FFF
    n = opcode & 0x000F

    if opcode == 0x00E0:
        clear_display()
        next_instruction()
    elif opcode == 0x00EE:
        if stack:
            pc = stack.pop()
        else:
            print("stack underflow")
        next_instruction()
    elif (opcode & 0xF000) == 0x1000:
        pc = nnn
    elif (opcode & 0xF000) == 0x2000:
        stack.append(pc)
        pc = nnn
    elif (opcode & 0xF000) == 0x3000:
        skip_instruction() if V[x] == nn else next_instruction()
    elif (opcode & 0xF000) == 0x4000:
        skip_instruction() if V[x] != nn else next_instruction()
    elif (opcode & 0xF000) == 0x5000:
        skip_instruction() if V[x] == V[y] else next_instruction()
    elif (opcode & 0xF000) == 0x6000:
        V[x] = nn
        next_instruction()
    elif (opcode & 0xF000) == 0x7000:
        V[x] = (V[x] + nn) & 0xFF
        next_instruction()
    elif (opcode & 0xF000) == 0x8000:
        if n == 0x0:
            V[x] = V[y]
        elif n == 0x1:
            V[x] |= V[y]
        elif n == 0x2:
            V[x] &= V[y]
        elif n == 0x3:
            V[x] ^= V[y]
        elif n == 0x4:
            result = V[x] + V[y]
            V[0xF] = 1 if result > 0xFF else 0
            V[x] = result & 0xFF
        elif n == 0x5:
            V[0xF] = 1 if V[x] > V[y] else 0
            V[x] = (V[x] - V[y]) & 0xFF
        elif n == 0x6:
            V[0xF] = V[x] & 0x1
            V[x] >>= 1
        elif n == 0x7:
            V[0xF] = 1 if V[y] >= V[x] else 0
            V[x] = V[y] - V[x]
        elif n == 0xE:
            V[0xF] = (V[x] & 0x80) >> 7
            V[x] = (V[x] << 1) & 0xFF
        next_instruction()
    elif (opcode & 0xF000) == 0x9000:
        skip_instruction() if V[x] != V[y] else next_instruction()
    elif (opcode & 0xF000) == 0xA000:
        I = nnn
        next_instruction()
    elif (opcode & 0xF000) == 0xB000:
        pc = nnn + V[0]
    elif (opcode & 0xF000) == 0xC000:
        V[x] = random.randint(0, 255) & nn
        next_instruction()
    elif (opcode & 0xF000) == 0xD000:
        V[0xF] = 0
        for row in range(n):
            sprite_row = memory[I + row]
            for col in range(8):
                if sprite_row & (0x80 >> col):
                    display[(V[y] + row) % DISPLAY_HEIGHT][(V[x] + col) % DISPLAY_WIDTH] ^= 1
                    if not display[(V[y] + row) % DISPLAY_HEIGHT][(V[x] + col) % DISPLAY_WIDTH]:
                        V[0xF] = 1
        next_instruction()
    elif (opcode & 0xF000) == 0xE000:
        if nn == 0x9E:
            skip_instruction() if keys[V[x]] else next_instruction()
        elif nn == 0xA1:
            skip_instruction() if not keys[V[x]] else next_instruction()
        else:
            print(f"unknown opcode: {opcode:04X}")
            next_instruction()
    elif (opcode & 0xF000) == 0xF000:
        if nn == 0x07:
            V[x] = delay_timer
        elif nn == 0x0A:
            if any(keys):
                V[x] = keys.index(1)
            else:
                return
        elif nn == 0x15:
            delay_timer = V[x]
        elif nn == 0x18:
            sound_timer = V[x]
        elif nn == 0x1E:
            I += V[x]
        elif nn == 0x29:
            I = 0x050 + (V[x] * SPRITE_SIZE)
        elif nn == 0x33:
            memory[I:I + 3] = [V[x] // 100, (V[x] // 10) % 10, V[x] % 10]
        elif nn == 0x55:
            memory[I:I + x + 1] = V[:x + 1]
        elif nn == 0x65:
            V[:x + 1] = memory[I:I + x + 1]
        else:
            print(f"Unknown opcode: {opcode:04X}")
        next_instruction()


# implement the display
def initialize_display():
    pygame.init()
    return pygame.display.set_mode((DISPLAY_WIDTH * 10, DISPLAY_HEIGHT * 10))


# draw display
def draw_display(screen):
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            color = (255,255,255) if display[y][x] else (0,0,0)
            pygame.draw.rect(screen, color, (x * 10, y * 10, 10, 10))
    pygame.display.flip()


# add input
def handle_input():
    global keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in CHIP8_KEYS:
                keys[CHIP8_KEYS[event.key]] = 1
        elif event.type == pygame.KEYUP:
            if event.key in CHIP8_KEYS:
                keys[CHIP8_KEYS[event.key]] = 0


# implement timers
def update_timers():
    global delay_timer, sound_timer
    if delay_timer > 0:
        delay_timer -= 1
    if sound_timer > 0:
        sound_timer -= 1


def load_rom_gui():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("chip8", "*.ch8")])
    return file_path


# main loop
def main():
    rom_file = load_rom_gui()
    if not rom_file:
        print("No rom file selected")
        sys.exit(1)

    load_rom(rom_file)
    screen = initialize_display()
    clock = pygame.time.Clock()

    while True:
        try:
            opcode = (memory[pc] << 8) | memory[pc+1]
            execute_opcode(opcode)
            update_timers()
            handle_input()
            draw_display(screen)
            clock.tick(60)
        except IndexError:
            print(f"IndexError: Accessing memory out of range at PC: {pc:04X}")
            break

    pygame.quit()


if __name__ == "__main__":
    main()