
import turtle
import random
import math




print("   BUMPER TURTLES")

player_name    = input("Enter your name: ").strip() or "Player"
difficulty_raw = input("Difficulty (easy / medium / hard): ").strip()
difficulty     = difficulty_raw.lower() if difficulty_raw else "medium"
# Weapon spawn interval scales with difficulty (frames at ~60fps)
_diff_key = difficulty[:1]
WEAPON_SPAWN_INTERVAL = 90 if _diff_key == "h" else (240 if _diff_key == "e" else 150)
print(f"\nWelcome, {player_name}!  Difficulty: {difficulty.upper()}")
print("SPACE=launch  Arrows=steer  R=reset  B=add bumper  C=clear  Q=quit\n")

screen = turtle.Screen()
screen.setup(width=800, height=600)
screen.bgcolor("black")
screen.title("Bumper Turtles")
screen.tracer(0)


game_state      = "waiting"
score           = 0
_frame_count    = 0
COLOR_CONSTANTS = ["cyan", "magenta", "yellow", "lime", "orange", "white", "red"]

# Shared turtles (declared here but behavior owned by each member's section)
hud = turtle.Turtle()
hud.hideturtle()
hud.penup()
hud.color("white")
hud.speed(0)

ball = turtle.Turtle()
ball.shape("circle")
ball.color("white")
ball.penup()
ball.speed(0)
ball.goto(0, 0)





# Each bumper stored as: [x, y, personality, hit_count, pulse_frames]
bumpers         = []
bumper_colors   = ["cyan", "magenta", "yellow", "lime", "orange", "red", "white"]
BUMPER_RADIUS   = 25
PERSONALITY_TYPES = ["repulsor", "attractor", "spinner", "teleporter"]

bumper_pen = turtle.Turtle()
bumper_pen.hideturtle()
bumper_pen.penup()
bumper_pen.speed(0)


def init_bumpers(count=10):
    """Populate bumpers list with random positions and personalities."""
    global bumpers
    bumpers = []
    for _ in range(count):
        x = random.randint(-350, 350)
        y = random.randint(-220, 220)
        personality = random.choice(PERSONALITY_TYPES)
        bumpers.append([x, y, personality, 0, 0])


def draw_bumper(x, y, personality, hit_count, pulse=False):
    color  = bumper_colors[hit_count % len(bumper_colors)]   # list indexing
    radius = BUMPER_RADIUS + 8 if pulse else BUMPER_RADIUS   # expand on hit
    bumper_pen.color(color)
    bumper_pen.goto(x, y - radius)
    bumper_pen.pendown()
    bumper_pen.circle(radius)
    bumper_pen.penup()
    # Personality label: first 3 chars, uppercased (string slicing + upper)
    bumper_pen.goto(x + radius + 3, y - 6)
    bumper_pen.write(personality[:3].upper(), font=("Arial", 8, "bold"))


def draw_all_bumpers():
    """Redraw every bumper and tick down each bumper's pulse countdown."""
    bumper_pen.clear()
    for b in bumpers:
        pulsing = b[4] > 0            
        draw_bumper(b[0], b[1], b[2], b[3], pulse=pulsing)
        if b[4] > 0:
            b[4] -= 1 


def apply_bumper_effect(bumper):

    global ball_dx, ball_dy, score

    bumper[3] += 1   # list index write: increment hit_count
    bumper[4] = 8    # list index write: trigger 8-frame pulse
    score += 10

    #String manipulation
    # join: build a formatted hit announcement from a list of parts
    hit_message = " | ".join([player_name, bumper[2], f"hit #{bumper[3]}"])

    raw_score_str = str(score).zfill(6)

    diff_parts = difficulty.split()

    diff_word = diff_parts[0].upper()

    diff_slice = diff_word[:3]

    # Combine into a compact difficulty/score label
    difficulty_warning = f"[{diff_slice}] Score: {raw_score_str}"

    print(f"  {hit_message}  —  {difficulty_warning}")


    bx, by   = bumper[0], bumper[1]
    ball_x   = ball.xcor()
    ball_y   = ball.ycor()

    if bumper[2] == "repulsor":
        # Reverse velocity away from bumper center
        ball_dx = abs(ball_dx)  if ball_x >= bx else -abs(ball_dx)
        ball_dy = abs(ball_dy)  if ball_y >= by else -abs(ball_dy)

    elif bumper[2] == "attractor":
        # Bend 20% of velocity toward the bumper center
        toward_x = bx - ball_x
        toward_y = by - ball_y
        dist     = math.sqrt(toward_x ** 2 + toward_y ** 2) or 1
        ball_dx += 0.2 * (toward_x / dist)
        ball_dy += 0.2 * (toward_y / dist)

    elif bumper[2] == "spinner":
        # Rotate velocity 45 degrees clockwise
        angle    = math.radians(45)
        new_dx   = ball_dx * math.cos(angle) - ball_dy * math.sin(angle)
        new_dy   = ball_dx * math.sin(angle) + ball_dy * math.cos(angle)
        ball_dx, ball_dy = new_dx, new_dy

    elif bumper[2] == "teleporter":
        # Jump ball to a random other bumper's position
        others = [b for b in bumpers if b is not bumper]
        if others:
            dest = random.choice(others)
            ball.goto(dest[0], dest[1])


def check_bumper_collision():
    """Detect ball–bumper overlap and apply the first match found this frame."""
    bx = ball.xcor()
    by = ball.ycor()
    for b in bumpers:
        dist = math.sqrt((bx - b[0]) ** 2 + (by - b[1]) ** 2)
        if dist < BUMPER_RADIUS + 10: 
            apply_bumper_effect(b)
            break



def place_bumper_at_click(x, y):
    """Mouse click: add a bumper at the clicked screen coordinate."""
    personality = random.choice(PERSONALITY_TYPES)
    bumpers.append([x, y, personality, 0, 0])


def add_random_bumper():
    """'b' key: add a bumper at a random position."""
    x = random.randint(-350, 350)
    y = random.randint(-220, 220)
    personality = random.choice(PERSONALITY_TYPES)
    bumpers.append([x, y, personality, 0, 0])   


def clear_bumpers():
    """'c' key: remove every bumper from the game."""
    bumpers.clear() 
    bumper_pen.clear()


# Register Member 1 event bindings
screen.onclick(place_bumper_at_click)
screen.onkeypress(add_random_bumper, "b")
screen.onkeypress(clear_bumpers,     "c")




ball_dx               = 0.0    # horizontal velocity 
ball_dy               = 0.0    # vertical velocity
ball_speed_multiplier = 1.0    # grows on each wall bounce
ball_launched         = False
ball_trail            = []
_speed_display_str    = "SPD: 00.00"   
_warning_label        = ""           

trail_pen = turtle.Turtle()
trail_pen.hideturtle()
trail_pen.penup()
trail_pen.speed(0)

# Screen boundary constants
WALL_LEFT, WALL_RIGHT = -390,  390
WALL_TOP, WALL_BOTTOM =  280, -280

# Trail shades from darkest to lightest
TRAIL_SHADES = [
    "#1a1a1a", "#2e2e2e", "#424242", "#575757", "#6b6b6b",
    "#808080", "#949494", "#a8a8a8", "#bdbdbd", "#d1d1d1"
]


def launch_ball():
    """Space key: begin ball movement at a speed set by difficulty."""
    global ball_dx, ball_dy, ball_launched, game_state

    if game_state == "game_over":
        return
    game_state    = "playing"
    ball_launched = True

    diff_key = difficulty[:1]   # 'e', 'm', or 'h'
    if diff_key == "e":
        ball_dx, ball_dy = 3.0, 3.0
    elif diff_key == "h":
        ball_dx, ball_dy = 7.0, 7.0
    else:
        ball_dx, ball_dy = 5.0, 5.0


def reset_ball():
    """'r' key: reset ball, board, weapons, and score for a fresh game."""
    global ball_dx, ball_dy, ball_speed_multiplier, ball_launched, game_state
    global score, _frame_count

    # Reset ball
    ball.goto(0, 0)
    ball.color("white")
    ball_dx               = 0.0
    ball_dy               = 0.0
    ball_speed_multiplier = 1.0
    ball_launched         = False
    ball_trail.clear()

    # Reset bumpers to a fresh random layout
    init_bumpers(count=10)

    # Clear all falling weapons still on screen
    for w_entry in active_weapons:
        w_entry[0].hideturtle()
    active_weapons.clear()

    # Reset shared state
    score         = 0
    _frame_count  = 0
    game_state    = "waiting"


def steer_left():
    """Left arrow: nudge ball in the leftward direction."""
    global ball_dx
    if game_state == "playing":
        ball_dx = max(ball_dx - 1.5, -10)


def steer_right():
    """Right arrow: nudge ball in the rightward direction."""
    global ball_dx
    if game_state == "playing":
        ball_dx = min(ball_dx + 1.5, 10)


def steer_up():
    """Up arrow: nudge ball upward."""
    global ball_dy
    if game_state == "playing":
        ball_dy = min(ball_dy + 1.5, 10)


def steer_down():
    """Down arrow: nudge ball downward."""
    global ball_dy
    if game_state == "playing":
        ball_dy = max(ball_dy - 1.5, -10)


def bounce_wall():
    """Reverse velocity at each boundary wall and increase speed slightly."""
    global ball_dx, ball_dy, ball_speed_multiplier

    if ball.xcor() >= WALL_RIGHT or ball.xcor() <= WALL_LEFT:
        ball_dx *= -1
        ball_speed_multiplier = min(ball_speed_multiplier + 0.02, 3.0)

    if ball.ycor() >= WALL_TOP or ball.ycor() <= WALL_BOTTOM:
        ball_dy *= -1
        ball_speed_multiplier = min(ball_speed_multiplier + 0.02, 3.0)


def draw_trail():
    """Render ghost dots from ball_trail (oldest dots are darker.)"""
    trail_pen.clear()
    trail_len = len(ball_trail)
    if trail_len < 2:
        return
    for i, pos in enumerate(ball_trail):
        shade_idx = int(i / trail_len * len(TRAIL_SHADES))
        shade_idx = min(shade_idx, len(TRAIL_SHADES) - 1)
        trail_pen.color(TRAIL_SHADES[shade_idx])      
        trail_pen.goto(pos[0], pos[1])                
        trail_pen.dot(8)


def move_ball():
    """Advance ball, bounce off walls, check bumper hits, update trail."""
    global ball_dx, ball_dy, ball_trail, _speed_display_str, _warning_label

    if not ball_launched:
        return

    ball.goto(
        ball.xcor() + ball_dx * ball_speed_multiplier,
        ball.ycor() + ball_dy * ball_speed_multiplier,
    )

    bounce_wall()
    check_bumper_collision()


    ball_trail.append((ball.xcor(), ball.ycor()))   
    ball_trail = ball_trail[-10:]                    

    # Change ball color based on current speed
    speed = round(math.sqrt(ball_dx ** 2 + ball_dy ** 2) * ball_speed_multiplier, 1)
    if speed < 5:
        ball.color("white")
    elif speed < 8:
        ball.color("yellow")
    else:
        ball.color("red")


    parts   = ["BALL", "SPEED", "ALERT"]
    warning = " >> ".join(parts).upper()    # join then upper
    _warning_label = warning if speed > 7 else ""

    diff_display       = difficulty.split()[0].upper()
    diff_key           = difficulty[:1]                  
    speed_tier         = "EASY" if diff_key == "e" else ("HARD" if diff_key == "h" else "MED")
    _speed_display_str = f"SPD: {str(speed).zfill(5)}  [{diff_display}/{speed_tier}]"

    draw_trail()


# Register Member 2 event bindings
screen.onkeypress(launch_ball,  "space")
screen.onkeypress(steer_left,   "Left")
screen.onkeypress(steer_right,  "Right")
screen.onkeypress(steer_up,     "Up")
screen.onkeypress(steer_down,   "Down")
screen.onkeypress(reset_ball,   "r")



weapon_types   = [["red", 3, 1.5], ["yellow", 5, 1.2], ["white", 2, 2.0]]
active_weapons = []
WEAPON_RADIUS  = 15


def spawn_weapon():
    """Create a new falling weapon at a random x position at the top edge."""
    idx   = random.randint(0, len(weapon_types) - 1)
    wtype = weapon_types[idx]

    w = turtle.Turtle()
    w.shape("circle")
    w.color(wtype[0])
    w.shapesize(wtype[2])
    w.penup()
    w.speed(0)
    w.goto(random.randint(-370, 370), WALL_TOP + 20)

    # Store as [turtle, dx, dy] — starts falling straight down
    active_weapons.append([w, 0.0, -float(wtype[1])])


def move_weapons():
    """Move weapons by dx/dy; bounce off walls and bumpers."""
    to_remove = []
    for w_entry in active_weapons:
        w_turtle = w_entry[0]
        wx = w_turtle.xcor() + w_entry[1]
        wy = w_turtle.ycor() + w_entry[2]

        # Bounce off left/right walls
        if wx > WALL_RIGHT or wx < WALL_LEFT:
            w_entry[1] *= -1
            wx = w_turtle.xcor()

        # Reflect off any bumper the weapon overlaps
        for b in bumpers:
            dist = math.sqrt((wx - b[0]) ** 2 + (wy - b[1]) ** 2)
            if dist < BUMPER_RADIUS + 12:
                # Push velocity outward from bumper center
                nx = wx - b[0]
                ny = wy - b[1]
                mag = math.sqrt(nx ** 2 + ny ** 2) or 1
                spd = math.sqrt(w_entry[1] ** 2 + w_entry[2] ** 2)
                w_entry[1] = (nx / mag) * spd
                w_entry[2] = (ny / mag) * spd
                wx, wy = w_turtle.xcor(), w_turtle.ycor()
                break

        w_turtle.goto(wx, wy)
        if w_turtle.ycor() < WALL_BOTTOM:
            w_turtle.hideturtle()
            to_remove.append(w_entry)
    for entry in to_remove:
        active_weapons.remove(entry)


def check_weapon_collision():
    """End the game immediately if any weapon touches the ball."""
    global game_state

    bx = ball.xcor()
    by = ball.ycor()
    to_remove = []
    for w_entry in active_weapons:
        w_turtle = w_entry[0]
        dist = math.sqrt((bx - w_turtle.xcor()) ** 2 + (by - w_turtle.ycor()) ** 2)
        if dist < WEAPON_RADIUS + 10:
            game_state = "game_over"
            w_turtle.hideturtle()
            to_remove.append(w_entry)
    for entry in to_remove:
        active_weapons.remove(entry)



def update_hud():
    """Redraw all on-screen text: score, speed, warnings, state messages."""
    hud.clear()

    # Top bar: player name and zero-padded score
    hud.goto(-390, 262)
    hud.color("white")
    hud.write(
        f"PLAYER: {player_name}   SCORE: {str(score).zfill(7)}",
        font=("Arial", 12, "bold")
    )

    hud.goto(-390, 240)
    hud.write(_speed_display_str, font=("Arial", 10, "normal"))

    if _warning_label:
        hud.goto(-390, 218)
        hud.color("red")
        hud.write(_warning_label, font=("Arial", 10, "bold"))
        hud.color("white")

    hud.goto(-390, -288)
    hud.color("gray")
    hud.write(
        "SPACE=launch  Arrows=steer  R=reset  B=add bumper  C=clear  Q=quit",
        font=("Arial", 8, "normal")
    )
    hud.color("white")

    if game_state == "waiting":
        hud.goto(-155, 5)
        hud.write("Press SPACE to launch!", font=("Arial", 18, "bold"))

    elif game_state == "game_over":
        hud.goto(-90, 20)
        hud.color("red")
        hud.write("GAME OVER", font=("Arial", 28, "bold"))
        hud.color("white")
        hud.goto(-140, -20)
        hud.write(
            f"Final Score: {str(score).zfill(7)}",
            font=("Arial", 14, "normal")
        )
        hud.goto(-175, -50)
        hud.write("Press R to play again", font=("Arial", 12, "normal"))


def quit_game():
    """'q' key: close the game window."""
    screen.bye()


def game_loop():
    """Main loop — called every 16 ms (~60 fps) via ontimer."""
    global _frame_count

    if game_state == "playing":
        move_ball()
        _frame_count += 1
        if _frame_count % WEAPON_SPAWN_INTERVAL == 0:
            spawn_weapon()
        move_weapons()
        check_weapon_collision()

    draw_all_bumpers()
    update_hud()
    screen.update()              
    screen.ontimer(game_loop, 16)


screen.listen()
screen.onkeypress(quit_game, "q")

init_bumpers(count=10)
game_loop()
screen.mainloop()
