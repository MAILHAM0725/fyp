from psychopy import visual, core, event
import random
import csv

# ==============================
# PARAMETERS
# ==============================
TASK_DURATION = 90  # 3 minutes (seconds)
MAX_RT = 2.0         # response window
FIXATION_TIME = 0.5
PRE_STIM_GAP = 0.2
FEEDBACK_TIME = 0.5

# ==============================
# WINDOW
# ==============================
win = visual.Window(
    size=(1024, 768),
    color="black",
    units="pix",
    fullscr=False
)

# ==============================
# STIMULI
# ==============================
fixation = visual.TextStim(win, "+", color="white", height=40)
correct_text = visual.TextStim(win, "✓", color="green", height=40)
mistake_text = visual.TextStim(win, "✗", color="red", height=40)

# ==============================
# STROOP TABLE
# condition: 1 = congruent, 0 = incongruent
# ==============================
stroop_trials = [
    ("yellow", "yellow", 1, "y"),
    ("yellow", "green",  0, "g"),
    ("yellow", "blue",   0, "b"),
    ("yellow", "red",    0, "r"),
    ("red",    "yellow", 0, "y"),
    ("red",    "green",  0, "g"),
    ("red",    "blue",   0, "b"),
    ("red",    "red",    1, "r"),
    ("green",  "yellow", 0, "y"),
    ("green",  "green",  1, "g"),
    ("green",  "blue",   0, "b"),
    ("green",  "red",    0, "r"),
    ("blue",   "yellow", 0, "y"),
    ("blue",   "green",  0, "g"),
    ("blue",   "blue",   1, "b"),
    ("blue",   "red",    0, "r")
]

# ==============================
# DATA STORAGE
# ==============================
results = []
trial_count = 0

# ==============================
# CLOCKS
# ==============================
global_clock = core.Clock()
rt_clock = core.Clock()

# ==============================
# START TASK
# ==============================
global_clock.reset()

while global_clock.getTime() < TASK_DURATION:

    random.shuffle(stroop_trials)

    for word, color, condition, correct_key in stroop_trials:

        if global_clock.getTime() >= TASK_DURATION:
            break

        trial_count += 1

        # Fixation
        fixation.draw()
        win.flip()
        core.wait(FIXATION_TIME)

        win.flip()
        core.wait(PRE_STIM_GAP)

        # Stimulus
        stim = visual.TextStim(
            win,
            text=word.upper(),
            color=color,
            height=60
        )

        stim.draw()
        win.flip()

        rt_clock.reset()
        keys = event.waitKeys(
            maxWait=MAX_RT,
            keyList=["r", "g", "b", "y"],
            timeStamped=rt_clock
        )

        win.flip()

        if keys:
            key, rt = keys[0]
            correct = int(key == correct_key)
        else:
            key, rt, correct = None, None, 0

        # Feedback
        if correct:
            correct_text.draw()
        else:
            mistake_text.draw()

        win.flip()
        core.wait(FEEDBACK_TIME)

        # Save trial
        results.append([
            trial_count,
            word,
            color,
            condition,
            correct_key,
            key,
            correct,
            rt
        ])

# ==============================
# SAVE RESULTS
# ==============================
with open("stroop_3min_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "trial", "word", "ink_color",
        "condition", "correct_key",
        "response_key", "correct", "rt"
    ])
    writer.writerows(results)

# ==============================
# END
# ==============================
win.close()
core.quit()
