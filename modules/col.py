def display_256_color_palette():
    for i in range(0, 256, 16):
        for j in range(16):
            code = i + j
            print(f'\033[38;5;{code}m {code:3} \033[0m', end=' ')
        print()

if __name__ == "__main__":
    display_256_color_palette()