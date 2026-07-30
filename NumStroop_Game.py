from psychopy import visual, core, event
from PyQt5.QtWidgets import QApplication # ✅ Keep timer alive
import random

# Modified: save_path is kept as an argument to prevent errors in main.py, but it is not used.
def run_num_stroop_game(duration_sec, save_path=None):
    # =========================
    # PARAMETERS
    # =========================
    MAX_RT = 3.0
    FIX_TIME = 0.5
    FEEDBACK_TIME = 0.5
    SMALL_FONT = 60  # Smaller font for windowed mode
    BIG_FONT = 100

    # =========================
    # WINDOW (Fixed size, No Fullscreen)
    # =========================
    win = visual.Window(
        size=(800, 600),     # ✅ Small window
        color="#EEEEEE",
        units="pix",
        fullscr=False,       # ✅ No full screen
        allowGUI=True
    )

    # =========================
    # STIMULI
    # =========================
    fixation = visual.TextStim(win, "+", color="black", height=40)
    correct_text = visual.TextStim(win, "Well done", color="green", height=40)
    wrong_text = visual.TextStim(win, "Wrong", color="red", height=40)
    slow_text = visual.TextStim(win, "Too slow", color="black", height=40)
    
    instr = visual.TextStim(
        win, 
        "NUMERICAL STROOP\n\n"
        "Which number is PHYSICALLY LARGER?\n"
        "Press LEFT arrow or RIGHT arrow.\n\n"
        "Ignore the numerical value!\n\n"
        "Press any key to start.",
        color="black", height=30
    )

    # Setup numbers
    nums = [2, 3, 4, 5, 6, 7, 8, 9]
    pairs = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] != nums[j]:
                pairs.append((nums[i], nums[j]))

    instr.draw()
    win.flip()
    event.waitKeys()

    global_clock = core.Clock()
    rt_clock = core.Clock()
    
    # =========================
    # LOOP
    # =========================
    while global_clock.getTime() < duration_sec:
        # ✅ Keep the Main App Timer moving!
        QApplication.processEvents()

        n1, n2 = random.choice(pairs)
        cond_type = random.choice(["congruent", "incongruent", "neutral"])
        
        # Logic for fonts
        size1, size2 = 0, 0
        correct_key = ""
        
        # Simplified Logic
        if cond_type == "neutral":
            if random.random() > 0.5:
                size1, size2, correct_key = BIG_FONT, SMALL_FONT, "left"
            else:
                size1, size2, correct_key = SMALL_FONT, BIG_FONT, "right"
        elif cond_type == "congruent":
            if n1 > n2: 
                size1, size2, correct_key = BIG_FONT, SMALL_FONT, "left"
            else:
                size1, size2, correct_key = SMALL_FONT, BIG_FONT, "right"
        elif cond_type == "incongruent":
            if n1 > n2:
                size1, size2, correct_key = SMALL_FONT, BIG_FONT, "right"
            else:
                size1, size2, correct_key = BIG_FONT, SMALL_FONT, "left"

        # Draw
        fixation.draw()
        win.flip()
        core.wait(FIX_TIME)

        left_stim = visual.TextStim(win, text=str(n1), height=size1, color="black", pos=(-150, 0))
        right_stim = visual.TextStim(win, text=str(n2), height=size2, color="black", pos=(150, 0))

        left_stim.draw()
        right_stim.draw()
        win.flip()

        # Input
        rt_clock.reset()
        keys = event.waitKeys(maxWait=MAX_RT, keyList=["left", "right", "escape"], timeStamped=rt_clock)

        if keys and keys[0][0] == 'escape':
            break

        if keys:
            key, rt = keys[0]
            status = "CORRECT" if key == correct_key else "WRONG"
        else:
            key, rt, status = None, None, "TIMEOUT"

        # Feedback
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

    win.close()