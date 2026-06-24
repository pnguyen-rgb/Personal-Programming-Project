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
BLUE = Fore.BLUE
GREEN = Fore.GREEN
RESET = Style.RESET_ALL
WORDS_REQUIRED_FOR_HINT = 3

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
    return None

def is_theme_word(word, theme_words):
    """Check if word is a theme word and remove it"""
    word_upper = word.upper()
    if word_upper in theme_words:
        theme_words.remove(word_upper)
        return True
    return False
    
def check_word_valid(word):
    word = word.lower()
    freq = zipf_frequency(word, "en")
    if freq > 2.0:
        return True
    return False

def generate_grid(grid_lines):
    grid = []
    for i in range(len(grid_lines)):
        grid.append([])

    for i, row in enumerate(grid_lines):
        for letter in row:
            grid[i].append(letter)
    
    return grid

def build_visual_grid(grid, found_paths):
    #Build a visual representation of the grid with connecting lines
    rows = len(grid)
    cols = len(grid[0])
    
    # Create a larger grid to accommodate lines between letters
    visual_rows = rows * 2 - 1
    visual_cols = cols * 4 - 1
    
    # Initialize visual grid with spaces
    visual = [[" " for _ in range(visual_cols)] for _ in range(visual_rows)]
    
    # Place letters in the visual grid (at even rows, every 4th column)
    for r in range(rows):
        for c in range(cols):
            visual[r * 2][c * 4] = grid[r][c]
    
    # Draw connections for each found path
    for path, color in found_paths:
        if len(path) < 2:
            # If single letter path, just color it
            if path:
                r, c = path[0]
                vr, vc = r * 2, c * 4
                visual[vr][vc] = color + grid[r][c] + RESET
            continue
            
        # Color all letters in the path
        for r, c in path:
            vr, vc = r * 2, c * 4
            visual[vr][vc] = color + grid[r][c] + RESET
        
        # Draw lines between consecutive letters
        if color != GREEN:
            for i in range(len(path) - 1):
                r1, c1 = path[i]
                r2, c2 = path[i + 1]
                
                # Convert to visual coordinates
                vr1, vc1 = r1 * 2, c1 * 4
                vr2, vc2 = r2 * 2, c2 * 4
                
                # Determine direction and draw appropriate line
                dr = vr2 - vr1
                dc = vc2 - vc1
                
                if dr == 0 and dc > 0:  # Right (horizontal)
                    for j in range(1, dc):
                        if j == dc - 1:
                            visual[vr1][vc1 + j] = color + "-" + RESET
                        else:
                            visual[vr1][vc1 + j] = color + "–" + RESET
                elif dr == 0 and dc < 0:  # Left (horizontal)
                    for j in range(-1, dc, -1):
                        if j == dc + 1:
                            visual[vr1][vc1 + j] = color + "-" + RESET
                        else:
                            visual[vr1][vc1 + j] = color + "–" + RESET
                elif dr > 0 and dc == 0:  # Down (vertical)
                    for j in range(1, dr):
                        visual[vr1 + j][vc1] = color + "|" + RESET
                elif dr < 0 and dc == 0:  # Up (vertical)
                    for j in range(-1, dr, -1):
                        visual[vr1 + j][vc1] = color + "|" + RESET
                elif dr > 0 and dc > 0:  # Down-right diagonal
                    steps = abs(dr)
                    for step in range(1, steps):
                        vr = vr1 + step
                        vc = vc1 + step
                        visual[vr][vc] = color + "\\" + RESET
                elif dr > 0 and dc < 0:  # Down-left diagonal
                    steps = abs(dr)
                    for step in range(1, steps):
                        vr = vr1 + step
                        vc = vc1 - step
                        visual[vr][vc] = color + "/" + RESET
                elif dr < 0 and dc > 0:  # Up-right diagonal
                    steps = abs(dr)
                    for step in range(1, steps):
                        vr = vr1 - step
                        vc = vc1 + step
                        visual[vr][vc] = color + "/" + RESET
                elif dr < 0 and dc < 0:  # Up-left diagonal
                    steps = abs(dr)
                    for step in range(1, steps):
                        vr = vr1 - step
                        vc = vc1 - step
                        visual[vr][vc] = color + "\\" + RESET
    
    # Convert visual grid to string and clean up extra spaces
    result = []
    for row in visual:
        # Join the row and remove trailing spaces
        line = "".join(row).rstrip()
        result.append(line)
    
    return "\n".join(result)

def display_grid(grid, found_paths):
    """Display the grid with connecting lines for found words"""
    visual = build_visual_grid(grid, found_paths)
    print("\n" + visual + "\n")

def check_word_on_grid(word, grid):
    visited = []
    def find_path(current_word, r, c, visited):
        if len(current_word) == 0:
            return True
        
        adjacents = check_adjacent(grid, (r, c))
        next_letter = current_word[0]
        for letter in adjacents:
            nr, nc = letter[0], letter[1]
            if nr != "" and nc != "":
                if grid[nr][nc] == next_letter and (nr, nc) not in visited:
                    visited.append((nr, nc))
                    if find_path(current_word[1:], nr, nc, visited):
                        return True
                    visited.remove((nr, nc))

        return False
    
    for r, row in enumerate(grid):
        for c, letter in enumerate(row):
            if letter == word[0]:
                visited.append((r, c))
                if find_path(word[1:], r, c, visited):
                    return visited
                visited.remove((r, c))

    return visited


def check_adjacent(grid, pos):
    r, c = pos[0], pos[1]
    left = "", ""
    right = "", ""
    up = "", ""
    down = "", ""
    top_left = "", ""
    top_right = "", ""
    bottom_left = "", ""
    bottom_right = "", ""
    if c != 0:
        left = (r, c-1)
    if c != len(grid[r]) - 1:
        right = (r, c+1)
    if r != 0:
        up = (r-1, c)
    if r != len(grid) - 1:
        down = (r+1, c)
    if r != 0 and c != 0:
        top_left = (r-1, c-1)
    if r != 0 and c != len(grid[r]) - 1:
        top_right = (r-1, c+1)
    if r != len(grid) - 1 and c != 0:
        bottom_left = (r+1, c-1)
    if r != len(grid) - 1 and c != len(grid[r]) - 1:
        bottom_right = (r+1, c+1)
    adjacents = [left, right, up, down, top_left, top_right, bottom_left, bottom_right]
    return adjacents

def start_game():
    selected_grid = select_grid()
    theme = selected_grid.stem
    grid_lines, theme_words = load_game(selected_grid)
    playing = True
    words_found = []
    score = 0
    num_words = len(theme_words)
    sprangram = find_sprangram(theme_words)
    grid = generate_grid(grid_lines)
    found_paths = []
    words_until_next_hint = 3
    hints = 0

    while playing:
        clear_screen()
        print_coloured_text(WHITE, f"\n{'='*50}")
        display_grid(grid, found_paths)
        print("Theme:", theme)
        print(f"{score} of {num_words} theme words found\n")
        
        word = input("Enter a combination of adjacent letters from the grid: (enter ? for a hint) ").upper().replace(" ", "")
        if word == "?":
            if hints > 0:
                hints -= 1
                sorted_words = sorted(theme_words, key=len)
                for word in sorted_words:
                    if word in words_found:
                        sorted_words.remove(word)
                hint_word = sorted_words[0]
                path = check_word_on_grid(hint_word, grid)
                if path:
                    found_paths.append((path, GREEN))
                display_grid(grid, found_paths)
                input("Your hint is shown in green. Press enter to continue. ")
                found_paths.pop()
                
            else:
                print("You don't have enough hints!")
                time.sleep(3)
            continue

        if word.isalpha():        
            if len(word) < 4:
                print("Word is too short!")
                time.sleep(2)
            else:
                if word in words_found:
                    print("Word is found already!")
                    time.sleep(2)
                elif is_theme_word(word, theme_words):
                    score += 1
                    words_found.append(word)
                    if word == sprangram:
                        print_coloured_text(YELLOW, "\nSprangram!")
                        print_coloured_text(WHITE, "", True)
                        # Add sprangram path with yellow color
                        path = check_word_on_grid(word, grid)
                        if path:
                            found_paths.append((path, YELLOW))
                    else:
                        # Add theme word path with blue color
                        path = check_word_on_grid(word, grid)
                        if path:
                            found_paths.append((path, BLUE))
                    
                    print_coloured_text(BLUE, f"\nTheme word found: {word}")
                    print_coloured_text(WHITE, "", True)
                    time.sleep(1.5)
                    
                    # Check if all words found
                    if score == num_words:
                        clear_screen()
                        display_grid(grid, found_paths)
                        print_coloured_text(YELLOW, "\n🎉 Congratulations! You found all the theme words! 🎉")
                        playing = False
                        
                else:
                    path = check_word_on_grid(word, grid)
                    if path:
                        print("Word is on grid")
                        if check_word_valid(word):
                            print("Word is valid")
                            words_found.append(word)
                            print_coloured_text(WHITE, f"\nNon-theme word found: {word}")
                            words_until_next_hint -= 1
                            print(f"Words until next hint: {words_until_next_hint}")
                            if words_until_next_hint == 0:
                                hints += 1
                                words_until_next_hint = 3
                            print(f"Hints: {hints}")

                            print()
                            time.sleep(1.5)
                        else:
                            print("That doesn't look like a valid English word. Try again.")
                            time.sleep(2)
                    else:
                        print("Word not found on grid. Try again.")
                        time.sleep(2)
        else:
            print("Please enter a string")

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
    print_coloured_text(WHITE, 'Find theme words to fill the board.\nTheme words stay highlighted in blue when found.\nEnter a word or letters to create words.\nTheme words fill the board entirely. No theme words overlap.\n\nFind the "spangram."\nThe spangram describes the puzzle\'s theme and touches two opposite sides of the board. It may be one or more words.\nThe spangram highlights in yellow when found.\nAn example spangram with corresponding theme words: ', True)
    print_coloured_text(CYAN, "LIME", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(YELLOW, "FRUIT", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(CYAN, "BANANA", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(CYAN, "APPLE", True)
    print_coloured_text(WHITE, ", ", True)
    print_coloured_text(WHITE, "etc.\n")
    input("Press enter to continue:\n")
    clear_screen()

def main():
    while True:
        user_choice = input("Would you like to play or read the rules (p for play, r for read rules)?\n").lower()
        if user_choice == "p":
            start_game()
        elif user_choice == "r":
            display_rules()
        else:
            print("Not a valid option! Pick p for play or r for rules.\n")

main()