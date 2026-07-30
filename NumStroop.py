from psychopy import visual, core, event
import random
import csv

# =========================
# PARAMETERS
# =========================
TASK_DURATION = 180   # 3 minutes
MAX_RT = 3.0
FIX_TIME = 0.5
FEEDBACK_TIME = 0.5

SMALL_FONT = 80
BIG_FONT = 120

# =========================
# WINDOW
# =========================
win = visual.Window(
    size=(1024, 768),
    color="#EEEEEE",
    units="pix",
    fullscr=False
)

# =========================
# STIMULI
# =========================
fixation = visual.TextStim(win, "+", color="black", height=40)
correct_text = visual.TextStim(win, "Well done", color="green", height=40)
wrong_text = visual.TextStim(win, "Wrong", color="red", height=40)
slow_text = visual.TextStim(win, "Too slow", color="black", height=40)

# =========================
# CLOCKS
# =========================
global_clock = core.Clock()
rt_clock = core.Clock()

# =========================
# DATA
# =========================
results = []
trial_count = 0

# =========================
# START TASK
# =========================
global_clock.reset()

while global_clock.getTime() < TASK_DURATION:

    # -------------------------
    # Generate numbers
    # -------------------------
    left_num = random.randint(1, 9)
    right_num = random.choice([n for n in range(1, 10) if n != left_num])

    # Decide which side is physically larger
    left_big = random.choice([True, False])

    if left_big:
        left_size = BIG_FONT
        right_size = SMALL_FONT
        correct_key = "a"   # left
    else:
        left_size = SMALL_FONT
        right_size = BIG_FONT
        correct_key = "l"   # right

    # -------------------------
    # Determine congruency
    # -------------------------
    if (left_num > right_num and left_big) or (right_num > left_num and not left_big):
        condition_name = "congruent"
        condition_code = 1
    else:
        condition_name = "incongruent"
        condition_code = 2

    trial_count += 1

    # -------------------------
    # Fixation
    # -------------------------
    fixation.draw()
    win.flip()
    core.wait(FIX_TIME)

    win.flip()
    core.wait(0.2)

    # -------------------------
    # Stimuli
    # -------------------------
    left_stim = visual.TextStim(
        win, text=str(left_num),
        pos=(-200, 0), height=left_size,
        color="black"
    )

    right_stim = visual.TextStim(
        win, text=str(right_num),
        pos=(200, 0), height=right_size,
        color="black"
    )

    left_stim.draw()
    right_stim.draw()
    win.flip()

    rt_clock.reset()
    keys = event.waitKeys(
        maxWait=MAX_RT,
        keyList=["a", "l"],
        timeStamped=rt_clock
    )

    win.flip()

    # -------------------------
    # Response handling
    # -------------------------
    if keys:
        key, rt = keys[0]
        status = "CORRECT" if key == correct_key else "WRONG"
    else:
        key, rt = None, None
        status = "TIMEOUT"

    # -------------------------
    # Feedback
    # -------------------------
    if status == "CORRECT":
        correct_text.draw()
        win.flip()
        core.wait(FEEDBACK_TIME)
    elif status == "WRONG":
        wrong_text.draw()
        win.flip()
        core.wait(1.0)
    else:
        slow_text.draw()
        win.flip()
        core.wait(1.0)

    win.flip()
    core.wait(0.5)

    # -------------------------
    # Save trial
    # -------------------------
    results.append([
        trial_count,
        condition_name,
        condition_code,
        rt,
        status,
        left_num,
        right_num,
        left_size
    ])

# =========================
# SAVE CSV
# =========================
with open("numerical_stroop_3min.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "trial",
        "condition_name",
        "condition_code",
        "rt",
        "status",
        "left_number",
        "right_number",
        "left_font_size"
    ])
    writer.writerows(results)

# =========================
# END
# =========================
win.close()
core.quit()
