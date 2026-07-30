from psychopy import visual, core, event
from PyQt5.QtWidgets import QApplication  # ✅ Import this to keep main timer alive
import random

# Modified: save_path is kept as an argument to prevent errors in main.py, but it is not used.
def run_stroop_game(duration_sec, save_path=None):
    # ==============================
    # PARAMETERS
    # ==============================
    MAX_RT = 2.0         
    FIXATION_TIME = 0.5
    PRE_STIM_GAP = 0.2
    FEEDBACK_TIME = 0.5

    # ==============================
    # WINDOW (Fixed size, No Fullscreen)
    # ==============================
    win = visual.Window(
        size=(800, 600),     # ✅ Small window
        color="black",
        units="pix",
        fullscr=False,       # ✅ No full screen
        allowGUI=True,
        monitor="testMonitor"
    )

    # ==============================
    # STIMULI
    # ==============================
    fixation = visual.TextStim(win, "+", color="white", height=40)
    correct_text = visual.TextStim(win, "✓", color="green", height=80)
    mistake_text = visual.TextStim(win, "✗", color="red", height=80)
    
    instr = visual.TextStim(
        win, 
        "STROOP TASK\n\n"
        "Press the key matching the INK COLOR:\n"
        "R = Red\nG = Green\nB = Blue\nY = Yellow\n\n"
        "Ignore the written word!\n\n"
        "Press any key to start.",
        color="white", height=30
    )

    # ==============================
    # LOGIC
    # ==============================
    stroop_trials = [
        ("yellow", "yellow", 1, "y"),
        ("yellow", "green",  0, "g"),
        ("yellow", "blue",   0, "b"),
        ("yellow", "red",    0, "r"),
        ("red",    "yellow", 0, "y"),
        ("red",    "red",    1, "r"),
        ("red",    "green",  0, "g"),
        ("red",    "blue",   0, "b"),
        ("green",  "yellow", 0, "y"),
        ("green",  "red",    0, "r"),
        ("green",  "green",  1, "g"),
        ("green",  "blue",   0, "b"),
        ("blue",   "yellow", 0, "y"),
        ("blue",   "red",    0, "r"),
        ("blue",   "green",  0, "g"),
        ("blue",   "blue",   1, "b"),
    ]

    instr.draw()
    win.flip()
    event.waitKeys()

    # Clocks
    global_clock = core.Clock()
    rt_clock = core.Clock()
    
    # ==============================
    # GAME LOOP
    # ==============================
    while global_clock.getTime() < duration_sec:
        # ✅ Keep the Main App Timer moving!
        QApplication.processEvents()

        word, color, condition, correct_key = random.choice(stroop_trials)

        # 1. Fixation
        fixation.draw()
        win.flip()
        core.wait(FIXATION_TIME)
        
        # Gap
        win.flip()
        core.wait(PRE_STIM_GAP)

        # 2. Stimulus
        stim = visual.TextStim(win, text=word.upper(), color=color, height=60)
        stim.draw()
        win.flip()

        # 3. Input
        rt_clock.reset()
        keys = event.waitKeys(
            maxWait=MAX_RT,
            keyList=["r", "g", "b", "y", "escape"],
            timeStamped=rt_clock
        )
        
        if keys and keys[0][0] == 'escape':
            break

        if keys:
            key, rt = keys[0]
            correct = int(key == correct_key)
        else:
            key, rt, correct = None, None, 0

        # 4. Feedback
        if correct:
            correct_text.draw()
        else:
            mistake_text.draw()
        
        win.flip()
        core.wait(FEEDBACK_TIME)

    win.close()