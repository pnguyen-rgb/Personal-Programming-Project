import colorama
from colorama import Fore, Back, Style
from pathlib import Path
import random
import time
from wordfreq import zipf_frequency
import os
colorama.init()


CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
WHITE = Fore.WHITE

def print_coloured_text(colour, text, end=False):
    if end:
        print(colour + text, end="")
    else:
        print(colour + text)

def clear_screen():
    os.system("clear")
    print("\n"*5)

def find_sprangram(theme_words):
    for word in theme_words:
        if word.strip().lower().endswith("(sprangram)"):
            theme_words.remove(word)
            theme_words.append(word[:(len(word)-12)])
            return word[:(len(word)-12)]
        
def is_theme_word(word, theme_words):
    if word in theme_words:
        theme_words.remove(word.upper())
        return True
    return False

def check_word_valid(word):
    word = word.lower()
    freq = zipf_frequency(word, "en")
    if freq > 2.0:
        return True

def generate_grid(grid_lines):
    grid = []
    for i in range(len(grid_lines)):
        grid.append([])

    for i, row in enumerate(grid_lines):
        for letter in row:
            grid[i].append(letter)
    
    return grid

def display_grid(grid):
    for row in grid:
        print()
        print(" ".join(row))
    print()

def start_game():
    selected_grid = select_grid()
    theme = selected_grid.stem
    grid_lines, theme_words = load_game(selected_grid)
    playing = True
    words_found = []
    score = 0
    num_words = len(theme_words)
    hints = 0
    words_required_for_hint = 3
    sprangram = find_sprangram(theme_words)

    while playing:
        grid = generate_grid(grid_lines)
        display_grid(grid)
        print("Theme:", theme)
        print(f"{score} of {num_words} theme words found")
        print("Hints:", hints)
        print(f"{words_required_for_hint} more non-theme words required for a hint\n")
        word = input("Enter a combination of adjacent letters from the grid or enter “?” for a hint: ").upper().replace(" ", "")
        clear_screen()
        print(word + "\n")
        if len(word) < 4:
            print("Word is too short!")
        else:
            if word in words_found:
                print("Word is found already!")
            elif is_theme_word(word, theme_words):
                score += 1
                words_found.append(word)
                if word == sprangram:
                    print_coloured_text(YELLOW, "\nSprangram!")
                    print_coloured_text(WHITE, "", True)
            else:
                if check_word_valid(word):
                    print("Word is valid")
                    words_found.append(word)
                else:
                    print("That doesn't look like a valid English word. Try again.")


def load_game(file):
    print()
    print("Generating theme and grid...")
    time.sleep(3)

    with open(file, "r") as f:
        lines = f.readlines()

    words_index = None
    for i, line in enumerate(lines):
        line = line.rstrip("\n")
        if line.lower().startswith("words:"):
            words_index = i
            break
    
    if words_index == None:
        print(f"No 'Words:' line found in file {file.name}")

    grid_lines = [line.strip() for line in lines[:words_index - 1]]
    theme_words = [line.strip() for line in lines[words_index + 1:]]

    return grid_lines, theme_words


def select_grid():
    # Path to the grids directory (relative to main.py)
    GRIDS_DIR = Path(__file__).parent / "grids"

    # Get a list of all files in the grids directory
    grid_files = [p for p in GRIDS_DIR.iterdir() if p.is_file()]
    selected_grid = random.choice(grid_files)

    return selected_grid

def display_rules():
    print_coloured_text(WHITE, 'Find theme words to fill the board.\nTheme words stay highlighted in blue when found.\nEnter a word or letters to create words.\nTheme words fill the board entirely. No theme words overlap.\n\nFind the “spangram.”\nThe spangram describes the puzzle’s theme and touches two opposite sides of the board. It may be one or more words.\nThe spangram highlights in yellow when found.\nAn example spangram with corresponding theme words: ', True)
    print_coloured_text(CYAN, "LIME", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(YELLOW, "FRUIT", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(CYAN, "BANANA", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(CYAN, "APPLE", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(WHITE, "etc.\n\nNeed a hint?\nFind non-theme words to get hints.\nFor every 3 non-theme words you find, you earn a hint.\nHints show the letters of a theme word. The letters will be highlighted in green. If there is already an active hint on the board, a hint will show that word’s letter order.\n")
    input("Press enter to continue:\n")
    clear_screen()

def show_results():
    pass

def main():
    while True:
        user_choice = input("Would you like to play or read the rules (p for play, r for read rules?\n").lower()
        if user_choice == "p":
            start_game()
        elif user_choice == "r":
            display_rules()
        else:
            print("Not a valid option! Pick p for play or r for rules.\n")

main()