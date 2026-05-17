# Bumper Turtles — Rubric Self-Assessment

---

## Member 1 — Bumper System

### User Input & Gameplay — **Excellent (10/10)**

Three independent controls, each meaningfully affecting gameplay:

| Control | Effect |
|---------|--------|
| Mouse click | Places a new bumper at the clicked coordinate |
| `b` key | Adds a random bumper anywhere on screen |
| `c` key | Clears all bumpers instantly |

Each bumper has a personality that actively changes how the ball moves (see List & String section for detail).

```python
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

screen.onclick(place_bumper_at_click)
screen.onkeypress(add_random_bumper, "b")
screen.onkeypress(clear_bumpers,     "c")
```

---

### Graphics, Color & Movement — **Excellent (5/5)**

- Bumpers cycle through 7 colors on each successive hit (`bumper_colors[hit_count % len(bumper_colors)]`)
- On hit, bumper expands by 8 px for 8 frames (pulse animation)
- Personality label written beside each bumper using `personality[:3].upper()`
- All bumpers are redrawn every frame at 60 fps

```python
def draw_bumper(x, y, personality, hit_count, pulse=False):
    color  = bumper_colors[hit_count % len(bumper_colors)]   # color cycles on hit
    radius = BUMPER_RADIUS + 8 if pulse else BUMPER_RADIUS   # expand on hit
    bumper_pen.color(color)
    bumper_pen.goto(x, y - radius)
    bumper_pen.pendown()
    bumper_pen.circle(radius)
    bumper_pen.penup()
    bumper_pen.goto(x + radius + 3, y - 6)
    bumper_pen.write(personality[:3].upper(), font=("Arial", 8, "bold"))

def draw_all_bumpers():
    bumper_pen.clear()
    for b in bumpers:
        pulsing = b[4] > 0
        draw_bumper(b[0], b[1], b[2], b[3], pulse=pulsing)
        if b[4] > 0:
            b[4] -= 1   # count down pulse frames
```

---

### Lists & String Manipulation — **Excellent (10/10)**

**List operations used:**

| Operation | Code |
|-----------|------|
| Append | `bumpers.append([x, y, personality, 0, 0])` |
| Index read | `b[0], b[1], b[2], b[3], b[4]` |
| Index write | `bumper[3] += 1` / `bumper[4] = 8` |
| Modulo index | `bumper_colors[hit_count % len(bumper_colors)]` |
| List comprehension | `[b for b in bumpers if b is not bumper]` |
| Clear | `bumpers.clear()` |

**String operations used:**

| Technique | Code |
|-----------|------|
| `.join()` | `" \| ".join([player_name, bumper[2], f"hit #{bumper[3]}"])` |
| `.zfill()` | `str(score).zfill(6)` |
| `.split()` | `difficulty.split()` |
| `.upper()` | `diff_parts[0].upper()` |
| Slicing `[:n]` | `diff_word[:3]` and `personality[:3]` |

```python
def apply_bumper_effect(bumper):
    bumper[3] += 1   # list index write: increment hit_count
    bumper[4] = 8    # list index write: trigger 8-frame pulse
    score += 10

    # join: build a formatted hit announcement
    hit_message = " | ".join([player_name, bumper[2], f"hit #{bumper[3]}"])

    raw_score_str = str(score).zfill(6)       # zfill

    diff_parts = difficulty.split()            # split
    diff_word  = diff_parts[0].upper()         # upper
    diff_slice = diff_word[:3]                 # slicing

    difficulty_warning = f"[{diff_slice}] Score: {raw_score_str}"
    print(f"  {hit_message}  —  {difficulty_warning}")
```

---

### Event Handling — **Excellent (5/5)**

Three distinct event types, all working and meaningful:

```python
screen.onclick(place_bumper_at_click)      # mouse click event
screen.onkeypress(add_random_bumper, "b")  # keyboard event
screen.onkeypress(clear_bumpers,     "c")  # keyboard event
```

---

### Code Quality & Readability — **Excellent (5/5)**

- All variables named descriptively (`bumper_colors`, `PERSONALITY_TYPES`, `BUMPER_RADIUS`, `hit_count`, `pulse_frames`)
- Each function has a docstring explaining its purpose
- Data structure layout documented at point of declaration
- Physics effects grouped by personality with inline comments

```python
# Each bumper stored as: [x, y, personality, hit_count, pulse_frames]
bumpers       = []
bumper_colors = ["cyan", "magenta", "yellow", "lime", "orange", "red", "white"]
BUMPER_RADIUS = 25
PERSONALITY_TYPES = ["repulsor", "attractor", "spinner", "teleporter"]

def check_bumper_collision():
    """Detect ball–bumper overlap and apply the first match found this frame."""
    bx = ball.xcor()
    by = ball.ycor()
    for b in bumpers:
        dist = math.sqrt((bx - b[0]) ** 2 + (by - b[1]) ** 2)
        if dist < BUMPER_RADIUS + 10:
            apply_bumper_effect(b)
            break   # one collision per frame prevents compounding effects
```

---

---

## Member 2 — Ball Physics

### User Input & Gameplay — **Excellent (10/10)**

Six controls, each with a distinct and meaningful gameplay effect:

| Control | Effect |
|---------|--------|
| `Space` | Launches the ball (speed set by difficulty) |
| `Left` / `Right` arrows | Nudge horizontal velocity mid-flight |
| `Up` / `Down` arrows | Nudge vertical velocity mid-flight |
| `r` | Resets ball, bumpers, weapons, and score |

```python
def launch_ball():
    """Space key: begin ball movement at a speed set by difficulty."""
    if game_state == "game_over":
        return
    game_state    = "playing"
    ball_launched = True
    diff_key = difficulty[:1]   # slicing: 'e', 'm', or 'h'
    if diff_key == "e":
        ball_dx, ball_dy = 3.0, 3.0
    elif diff_key == "h":
        ball_dx, ball_dy = 7.0, 7.0
    else:
        ball_dx, ball_dy = 5.0, 5.0

def steer_left():
    if game_state == "playing":
        ball_dx = max(ball_dx - 1.5, -10)

screen.onkeypress(launch_ball,  "space")
screen.onkeypress(steer_left,   "Left")
screen.onkeypress(steer_right,  "Right")
screen.onkeypress(steer_up,     "Up")
screen.onkeypress(steer_down,   "Down")
screen.onkeypress(reset_ball,   "r")
```

---

### Graphics, Color & Movement — **Excellent (5/5)**

- Ball moves smoothly at ~60 fps via `screen.ontimer(game_loop, 16)`
- Ball color shifts white → yellow → red as speed increases
- A 10-position ghost trail renders behind the ball using 10 shades of gray from darkest (oldest) to lightest (newest)
- Speed and difficulty tier shown live on the HUD

```python
# Ball color changes with speed
speed = round(math.sqrt(ball_dx**2 + ball_dy**2) * ball_speed_multiplier, 1)
if speed < 5:
    ball.color("white")
elif speed < 8:
    ball.color("yellow")
else:
    ball.color("red")

# Ghost trail
TRAIL_SHADES = [
    "#1a1a1a", "#2e2e2e", "#424242", "#575757", "#6b6b6b",
    "#808080", "#949494", "#a8a8a8", "#bdbdbd", "#d1d1d1"
]

def draw_trail():
    trail_len = len(ball_trail)
    if trail_len < 2:
        return
    for i, pos in enumerate(ball_trail):
        shade_idx = min(int(i / trail_len * len(TRAIL_SHADES)), len(TRAIL_SHADES) - 1)
        trail_pen.color(TRAIL_SHADES[shade_idx])
        trail_pen.goto(pos[0], pos[1])
        trail_pen.dot(8)
```

---

### Lists & String Manipulation — **Excellent (10/10)**

**List operations used:**

| Operation | Code |
|-----------|------|
| Append | `ball_trail.append((ball.xcor(), ball.ycor()))` |
| Slicing | `ball_trail = ball_trail[-10:]` |
| Enumerate | `for i, pos in enumerate(ball_trail)` |
| Index read | `TRAIL_SHADES[shade_idx]`, `pos[0]`, `pos[1]` |
| Clear | `ball_trail.clear()` |
| `len()` | `len(ball_trail)`, `len(TRAIL_SHADES)` |

**String operations used:**

| Technique | Code |
|-----------|------|
| `.join()` | `" >> ".join(["BALL", "SPEED", "ALERT"])` |
| `.upper()` | `.upper()` on joined string |
| `.split()` | `difficulty.split()[0]` |
| `.zfill()` | `str(speed).zfill(5)` |
| Slicing `[:n]` | `difficulty[:1]` |

```python
ball_trail.append((ball.xcor(), ball.ycor()))   # list append
ball_trail = ball_trail[-10:]                    # list slicing

parts   = ["BALL", "SPEED", "ALERT"]
warning = " >> ".join(parts).upper()             # join + upper
_warning_label = warning if speed > 7 else ""

diff_display       = difficulty.split()[0].upper()          # split + upper
diff_key           = difficulty[:1]                          # slicing
speed_tier         = "EASY" if diff_key == "e" else ("HARD" if diff_key == "h" else "MED")
_speed_display_str = f"SPD: {str(speed).zfill(5)}  [{diff_display}/{speed_tier}]"
```

---

### Event Handling — **Excellent (5/5)**

Six independently bound events, all affecting gameplay:

```python
screen.onkeypress(launch_ball,  "space")   # start game
screen.onkeypress(steer_left,   "Left")    # steer
screen.onkeypress(steer_right,  "Right")   # steer
screen.onkeypress(steer_up,     "Up")      # steer
screen.onkeypress(steer_down,   "Down")    # steer
screen.onkeypress(reset_ball,   "r")       # full board reset
```

---

### Code Quality & Readability — **Excellent (5/5)**

- Boundary wall constants named clearly (`WALL_LEFT`, `WALL_RIGHT`, `WALL_TOP`, `WALL_BOTTOM`)
- Velocity components clearly separated (`ball_dx`, `ball_dy`, `ball_speed_multiplier`)
- Every function has a docstring
- Speed cap on steering prevents runaway velocity

```python
WALL_LEFT, WALL_RIGHT = -390,  390
WALL_TOP, WALL_BOTTOM =  280, -280

ball_dx               = 0.0    # horizontal velocity
ball_dy               = 0.0    # vertical velocity
ball_speed_multiplier = 1.0    # grows on each wall bounce

def bounce_wall():
    """Reverse velocity at each boundary wall and increase speed slightly."""
    if ball.xcor() >= WALL_RIGHT or ball.xcor() <= WALL_LEFT:
        ball_dx *= -1
        ball_speed_multiplier = min(ball_speed_multiplier + 0.02, 3.0)
    if ball.ycor() >= WALL_TOP or ball.ycor() <= WALL_BOTTOM:
        ball_dy *= -1
        ball_speed_multiplier = min(ball_speed_multiplier + 0.02, 3.0)
```

---

---

## Member 3 — Falling Weapons

### User Input & Gameplay — **Proficient (8/10)**

No direct key controls, but weapons create active danger that forces the player to dodge using the arrow-key steering from Member 2. Weapons spawn automatically every ~3 seconds of gameplay.

```python
if _frame_count % 180 == 0:   # every 180 frames at 60fps = ~3 seconds
    spawn_weapon()
```

---

### Graphics, Color & Movement — **Proficient (4/5)**

Three weapon types with distinct colors and sizes; all fall smoothly downward and disappear off-screen.

```python
weapon_types = [["red", 3, 1.5], ["yellow", 5, 1.2], ["white", 2, 2.0]]
#               [color, speed, size_scale]

def spawn_weapon():
    idx   = random.randint(0, len(weapon_types) - 1)
    wtype = weapon_types[idx]
    w = turtle.Turtle()
    w.shape("circle")
    w.color(wtype[0])       # color from list
    w.shapesize(wtype[2])   # size from list
    w.penup()
    w.speed(0)
    w.goto(random.randint(-370, 370), WALL_TOP + 20)
    active_weapons.append([w, wtype[1]])
```

---

### Lists & String Manipulation — **Proficient (8/10)**

Strong list use; no explicit string manipulation (that criterion is fully covered by Members 1 and 2).

```python
weapon_types   = [["red", 3, 1.5], ["yellow", 5, 1.2], ["white", 2, 2.0]]
active_weapons = []

idx   = random.randint(0, len(weapon_types) - 1)   # list indexing
wtype = weapon_types[idx]
active_weapons.append([w, wtype[1]])                # list append

def move_weapons():
    to_remove = []
    for w_entry in active_weapons:
        w_turtle = w_entry[0]    # list index
        w_speed  = w_entry[1]    # list index
        w_turtle.sety(w_turtle.ycor() - w_speed)
        if w_turtle.ycor() < WALL_BOTTOM:
            w_turtle.hideturtle()
            to_remove.append(w_entry)
    for entry in to_remove:
        active_weapons.remove(entry)
```

---

### Event Handling — **Meets Minimum Requirements (3/5)**

No direct key bindings; weapons respond to the game timer (spawning on `_frame_count % 180`), and collision detection fires every frame to end the game.

```python
def check_weapon_collision():
    """End the game immediately if any weapon touches the ball."""
    for w_entry in active_weapons:
        w_turtle = w_entry[0]
        dist = math.sqrt((bx - w_turtle.xcor())**2 + (by - w_turtle.ycor())**2)
        if dist < WEAPON_RADIUS + 10:
            game_state = "game_over"
            w_turtle.hideturtle()
```

---

### Code Quality & Readability — **Excellent (5/5)**

Clean, readable functions with clear variable names and docstrings throughout.

```python
weapon_types   = [["red", 3, 1.5], ["yellow", 5, 1.2], ["white", 2, 2.0]]
active_weapons = []   # each entry: [turtle_obj, speed]
WEAPON_RADIUS  = 15

def spawn_weapon():
    """Create a new falling weapon at a random x position at the top edge."""
    ...

def move_weapons():
    """Move every weapon downward; remove any that fall below the screen."""
    ...

def check_weapon_collision():
    """End the game immediately if any weapon touches the ball."""
    ...
```

---

## Creativity & Effort — **Excellent (5/5)** *(Group)*

- Four bumper personalities each implement distinct physics (vector math for attractor, rotation matrix for spinner, random teleportation)
- Live speed HUD with difficulty tier label
- Ghost trail with 10 progressive gray shades
- Full board reset on death (bumpers re-randomized, weapons cleared, score reset)
- Terminal input for name and difficulty before the game window opens

---

## Student Leader — *(extra credit, up to 5 pts)*

The student who assembled all three sections, managed the shared variable architecture, integrated the event bindings, and implemented the full board reset on death qualifies for student leader credit.
