import engi1020.arduino.api as api
import time
import random
import tkinter as tk

# Global Constants
SOUND_THRESHOLD = 600  # Sound level required to trigger a jump
JUMP_HEIGHT = 75       # Jump height in pixels
GROUND_LEVEL = 300     # Ground level in pixels
OBSTACLE_SPEED = 7     # Obstacle movement speed

# Initialize Game State
game_running = False
score = 0
character_position = [50, GROUND_LEVEL]  # [x, y]
jumping = False
jump_velocity = 20
obstacles = []
    

# Input Functions
def detect_jump():
    sound_level = api.analog_read(2)
    return sound_level > SOUND_THRESHOLD

def button_pressed():
    return api.digital_read(6)

# Output Functions
def play_buzzer():
    api.buzzer_frequency(5, 8)
    time.sleep(0.25)
    api.buzzer_stop(5)

# GUI Setup
class GameGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=400, bg="lightblue")
        self.canvas.pack()
        
        self.character = self.canvas.create_rectangle(
            character_position[0], character_position[1] - 50,  
            character_position[0] + 50, character_position[1], fill="red")
        
        self.obstacle_objects = []
        self.score_label = self.canvas.create_text(700, 50, text=f"Score: {score}", font=("Arial", 20))

    def update_game_display(self):
        global character_position, obstacles, score

        # Update character position
        self.canvas.coords(
            self.character,
            character_position[0], character_position[1] - 50,  
            character_position[0] + 50, character_position[1]
        )

        # Update obstacles
        for i, obs in enumerate(obstacles):
            self.canvas.coords(
                self.obstacle_objects[i],
                obs[0], obs[1] - 25, obs[0] + 25, obs[1]
            )

        # Update score
        self.canvas.itemconfig(self.score_label, text=f"Score: {score}")

    def create_obstacle(self):
        global obstacles
        x_pos = 800
        y_pos = GROUND_LEVEL
        obstacles.append([x_pos, y_pos])
        obstacle_obj = self.canvas.create_rectangle(
            x_pos, y_pos - 25, x_pos + 25, y_pos, fill="black")
        self.obstacle_objects.append(obstacle_obj)

# Game Logic Functions
def jump_logic():
    global jumping, jump_velocity, character_position
    if jumping:
        character_position[1] -= jump_velocity * 1.5
        jump_velocity -= 1.5
        if character_position[1] >= GROUND_LEVEL:
            character_position[1] = GROUND_LEVEL
            jumping = False

def obstacle_logic(gui):
    global obstacles, score
    for obs in obstacles:
        obs[0] -= OBSTACLE_SPEED * 1.5

    # Remove off-screen obstacles
    for i in range(len(obstacles) - 1, -1, -1):
        if obstacles[i][0] + 25 <= 0:
            gui.canvas.delete(gui.obstacle_objects[i])
            del obstacles[i]
            del gui.obstacle_objects[i]

    # Check for collisions
    for obs in obstacles:
        if (character_position[0] + 50 > obs[0] and character_position[0] < obs[0] + 25 and
                character_position[1] >= obs[1] - 25):
            end_game()

    # Add new obstacles randomly
    if random.randint(0, 100) < 1:
        gui.create_obstacle()

# Main Game Loop
def game_loop(gui):
    global jumping, jump_velocity, score, game_running
    if not game_running:
        return

    # Detect jump input
    if detect_jump() and not jumping:
        jumping = True
        jump_velocity = 20
        play_buzzer()

    # Update game logic
    jump_logic()
    obstacle_logic(gui)

    # Update score
    score += 1

    # Update GUI
    gui.update_game_display()

    # Repeat loop
    gui.root.after(16, lambda: game_loop(gui))

# Start Game
def start_game(gui):
    global game_running, score, obstacles, character_position
    game_running = True
    score = 0
    obstacles = []
    character_position = [50, GROUND_LEVEL]
    game_loop(gui)

# End Game
def end_game():
    global game_running
    game_running = False
    play_buzzer()

# Main Function
def main():
    global game_running
    root = tk.Tk()
    gui = GameGUI(root)

    def button_loop():
        if button_pressed() and not game_running:
            start_game(gui)
        root.after(100, button_loop)

    button_loop()
    root.mainloop()

if __name__ == "__main__":
    main()
