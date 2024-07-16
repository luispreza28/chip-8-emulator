import pygame

# memory
memory = [0] * 4096 # start at 0 - end at 4096

# registers
V = [0] * 16
I = 0
pc = 0x200 # memory address starts at 0x200 (program counter)

# stack
stack = []

# timer
delay_timer = 0
sound_timer = 0

# display (64x32 pixels)
display = [[0 for _ in range(64)] for _ in range(32)]


# load the ROM
def load_rom(file_path):
    with open(file_path, 'rb') as f:
        rom = f.read()
    for i in range(len(rom)):
        # store byte starting at address 0x200 and then increment by i
        memory[0x200 + i] = rom[i]
    print("ROM loaded at memory[0x200]:", memory[0x200:0x220])


# clear display
def clear_display():
    global display
    display = [[0] * 64 for _ in range(32)]


# decode and execute
def execute_opcode(opcode):
    global pc, I, stack, delay_timer, sound_timer, display, V

    # Ensure PC is within bounds
    if pc >= len(memory) or pc < 0:
        print(f"Memory access out of bounds at PC: {pc:04X}")
        return

    print(f"PC: {pc:04X}, Opcode: {opcode:04X}")

    if opcode == 0x00E0:  # Clear display
        clear_display()
        pc += 2
    elif opcode == 0x00EE:  # Return from subroutine
        if stack:
            pc = stack.pop()
        else:
            print("Stack underflow")
            pc += 2
    # use 0xF000 to isolate the most significant nibble (the first 4 bits)
    elif (opcode & 0xF000) == 0x1000:  # Jump to address
        # use 0x0FFF to isolate the least significant 12 bits
        pc = opcode & 0x0FFF
    elif (opcode & 0xF000) == 0x2000:  # Call subroutine
        stack.append(pc)
        pc = opcode & 0x0FFF
    elif (opcode & 0xF000) == 0x3000:  # Skip next instruction if Vx == NN
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        if V[x] == nn:
            pc += 4
        else:
            pc += 2
    elif (opcode & 0xF000) == 0x4000:  # Skip next instruction if Vx != NN
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        if V[x] != nn:
            pc += 4
        else:
            pc += 2
    elif (opcode & 0xF000) == 0x5000:  # Skip next instruction if Vx == Vy
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        if V[x] == V[y]:
            pc += 4
        else:
            pc += 2
    elif (opcode & 0xF000) == 0x6000:  # Set Vx = NN
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        V[x] = nn
        pc += 2
    elif (opcode & 0xF000) == 0x7000:  # Add NN to Vx
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        V[x] = (V[x] + nn) & 0xFF
        pc += 2
    elif (opcode & 0xF000) == 0x8000:
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        if (opcode & 0x000F) == 0x0:  # Set Vx = Vy
            V[x] = V[y]
        elif (opcode & 0x000F) == 0x1:  # Set Vx = Vx OR Vy
            V[x] |= V[y]
        elif (opcode & 0x000F) == 0x2:  # Set Vx = Vx AND Vy
            V[x] &= V[y]
        elif (opcode & 0x000F) == 0x3:  # Set Vx = Vx XOR Vy
            V[x] ^= V[y]
        elif (opcode & 0x000F) == 0x4:  # Add Vy to Vx
            result = V[x] + V[y]
            V[0xF] = 1 if result > 0xFF else 0
            V[x] = result & 0xFF
        elif (opcode & 0x000F) == 0x5:  # Subtract Vy from Vx
            V[0xF] = 1 if V[x] >= V[y] else 0
            V[x] -= V[y]
        elif (opcode & 0x000F) == 0x6:  # Shift Vx right by 1
            V[0xF] = V[x] & 0x1
            V[x] >>= 1
        elif (opcode & 0x000F) == 0x7:  # Set Vx = Vy - Vx
            V[0xF] = 1 if V[y] >= V[x] else 0
            V[x] = V[y] - V[x]
        elif (opcode & 0x000F) == 0xE:  # Shift Vx left by 1
            V[0xF] = (V[x] & 0x80) >> 7
            V[x] <<= 1
        pc += 2
    elif (opcode & 0xF000) == 0x9000:  # Skip next instruction if Vx != Vy
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        if V[x] != V[y]:
            pc += 2
        else:
            pc += 4
    elif (opcode & 0xF000) == 0xA000:  # Set I = NNN
        I = opcode & 0x0FFF
        pc += 2
    elif (opcode & 0xF000) == 0xB000:  # Jump to address NNN + V0
        pc = (opcode & 0x0FFF) + V[0]
    elif (opcode & 0xF000) == 0xC000:  # Set Vx = random byte AND NN
        import random
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        V[x] = random.randint(0, 255) & nn
        pc += 2
    elif (opcode & 0xF000) == 0xD000:  # Draw sprite
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        height = opcode & 0x000F
        if I + height > len(memory):  # Check bounds for memory access
            print(f"Memory access out of bounds at I: {I}, height: {height}")
            return
        V[0xF] = 0
        for row in range(height):
            sprite_row = memory[I + row]
            for col in range(8):
                if (sprite_row & (0x80 >> col)) != 0:
                    if display[(V[y] + row) % 32][(V[x] + col) % 64] == 1:
                        V[0xF] = 1
                    display[(V[y] + row) % 32][(V[x] + col) % 64] ^= 1
        pc += 2
    elif (opcode & 0xF000) == 0xE000:
        x = (opcode & 0x0F00) >> 8
        if (opcode & 0x00FF) == 0x009E:  # Skip next instruction if key with value Vx is pressed
            if keys[V[x]] == 1:
                pc += 2
        elif (opcode & 0x00FF) == 0x00A1:  # Skip next instruction if key with value Vx is not pressed
            if keys[V[x]] == 0:
                pc += 2
        else:
            print(f"Unknown opcode: {opcode:04X}")
            pc += 2
    elif (opcode & 0xF000) == 0xF000:
        x = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00ff
        if kk == 0x0007:  # Set Vx = delay timer
            V[x] = delay_timer
            pc += 2
        elif kk == 0x000A:  # Wait for key press, store value in Vx
            key_pressed = False
            for i, key in enumerate(keys):
                if key:
                    V[x] = i
                    key_pressed = True
                    break
            if not key_pressed:
                return  # Wait for key press
        elif kk == 0x0015: # set delay timer = Vx
            delay_timer = V[x]
        elif kk == 0x0018: # set sound timer = Vx
            sound_timer = V[x]
        elif kk == 0x001e: # set I = I + Vx
            I += V[x]
        elif kk == 0x0029: # set I = location of sprite for digit Vx
            if V[x] < 16:
                I = V[x] * 0x0005
        elif kk == 0x0033: # store BCD representation of Vx in memory locations I, I+1, and I+2
            memory[I] = V[x] // 100 # hundreds digit
            memory[I + 1] = (V[x] // 10) & 10 # tens digit
            memory[I + 2] = V[x] & 10 # ones digit
        elif kk == 0x0055: # store registers V0 through Vx in memory starting at location I
            for i in range(x + 1):
                memory[I + i] = V[i]
        elif kk == 0x0065: # read registers v0 through Vx from memory starting at location I
            for i in range(x + 1):
                V[i] = memory[I + i]



# implement the display
def initialize_display():
    pygame.init()
    screen = pygame.display.set_mode((64 * 10, 32 * 10))
    return screen


# draw display
def draw_display(screen):
    for y in range(32):
        for x in range(64):
            color = (255,255,255) if display[y][x] == 1 else (0,0,0)
            pygame.draw.rect(screen, color, (x * 10, y * 10, 10, 10))
    pygame.display.flip()


keys = [0] * 16


# add input
def handle_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                keys[0x1] = 1
            elif event.key == pygame.K_2:
                keys[0x2] = 1
            elif event.key == pygame.K_3:
                keys[0x3] = 1
            elif event.key == pygame.K_4:
                keys[0xC] = 1
            elif event.key == pygame.K_q:
                keys[0x4] = 1
            elif event.key == pygame.K_w:
                keys[0x5] = 1
            elif event.key == pygame.K_e:
                keys[0x6] = 1
            elif event.key == pygame.K_r:
                keys[0xD] = 1
            elif event.key == pygame.K_a:
                keys[0x7] = 1
            elif event.key == pygame.K_s:
                keys[0x8] = 1
            elif event.key == pygame.K_d:
                keys[0x9] = 1
            elif event.key == pygame.K_f:
                keys[0xE] = 1
            elif event.key == pygame.K_z:
                keys[0xA] = 1
            elif event.key == pygame.K_x:
                keys[0x0] = 1
            elif event.key == pygame.K_c:
                keys[0xB] = 1
            elif event.key == pygame.K_v:
                keys[0xF] = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_1:
                keys[0x1] = 0
            elif event.key == pygame.K_2:
                keys[0x2] = 0
            elif event.key == pygame.K_3:
                keys[0x3] = 0
            elif event.key == pygame.K_4:
                keys[0xC] = 0
            elif event.key == pygame.K_q:
                keys[0x4] = 0
            elif event.key == pygame.K_w:
                keys[0x5] = 0
            elif event.key == pygame.K_e:
                keys[0x6] = 0
            elif event.key == pygame.K_r:
                keys[0xD] = 0
            elif event.key == pygame.K_a:
                keys[0x7] = 0
            elif event.key == pygame.K_s:
                keys[0x8] = 0
            elif event.key == pygame.K_d:
                keys[0x9] = 0
            elif event.key == pygame.K_f:
                keys[0xE] = 0
            elif event.key == pygame.K_z:
                keys[0xA] = 0
            elif event.key == pygame.K_x:
                keys[0x0] = 0
            elif event.key == pygame.K_c:
                keys[0xB] = 0
            elif event.key == pygame.K_v:
                keys[0xF] = 0


# implement timers
def update_timers():
    global delay_timer, sound_timer

    if delay_timer > 0:
        delay_timer -= 1
    if sound_timer > 0:
        sound_timer -= 1


# main loop
def main():
    screen = initialize_display()
    load_rom("picture.ch8")

    while True:
        try:
            opcode = memory[pc] << 8 | memory[pc+1]
            print(f"PC: {pc}, Opcode: {opcode:04X}")  # Debugging output
            execute_opcode(opcode)
        except IndexError:
            print(f"IndexError: Accessing memory out of range at PC: {pc:04X}")
            break

        update_timers()
        handle_input()
        draw_display(screen)
        pygame.time.wait(16) # 60hz


if __name__ == "__main__":
    main()