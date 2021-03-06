
import os

import tkinter as tk

from vnc_collaborate import freeswitch
from vnc_collaborate import icons50 as icons

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    # need to run 'pip3 install importlib-resources' to get this
    import importlib_resources as pkg_resources

def student_audio_controls(*options):
    r"""
    Displays a Tk window in the top-right corner of the display with
    student audio controls: mute, deaf, and a hand (click to raise).

    The function never returns.  Instead, it manages the window and
    polls the freeswitch API every quarter second to keep it updated.
    """

    username = os.environ['USER']

    window = tk.Tk()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # ImageMagick commands to create this graphics (originally extracted from BBB font file bbb-icons.woff)
    #
    # convert mute_filled_BigBlueButton.ppm -fill blue -opaque white mute_filled_BigBlueButton_blue.gif

    button_size = 60

    mute_white_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons, "mute_filled.ppm"))
    mute_blue_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons, "mute_filled_blue.gif"))
    deaf_white_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons, "listen_filled.ppm"))
    deaf_blue_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons, "listen_filled_blue.gif"))
    hand_white_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons,  "hand.png"))
    hand_blue_logo = tk.PhotoImage(data=pkg_resources.read_binary(icons, "hand_blue.png"))

    mute_button = tk.Label(
        text="MUTE",
        image=mute_white_logo,
        width=button_size,
        height=button_size,
        bg="white",
        fg="black",
    )

    deaf_button = tk.Label(
        text="DEAF",
        image=deaf_white_logo,
        width=button_size,
        height=button_size,
        bg="white",
        fg="black",
    )

    hand_button = tk.Label(
        text="HAND",
        image=hand_white_logo,
        width=button_size,
        height=button_size,
        bg="white",
        fg="black",
    )

    def set_correct_icon_status():
        freeswitch.get_status()
        try:
            if freeswitch.mute_status[freeswitch.freeswitch_ids[username]]:
                mute_button.configure(bg='white')
                mute_button.configure(image=mute_white_logo)
            else:
                mute_button.configure(bg='blue')
                mute_button.configure(image=mute_blue_logo)

            if freeswitch.deaf_status[freeswitch.freeswitch_ids[username]]:
                deaf_button.configure(bg='white')
                deaf_button.configure(image=deaf_white_logo)
            else:
                deaf_button.configure(bg='blue')
                deaf_button.configure(image=deaf_blue_logo)
        except KeyError:
            # The exception will most likely trigger if the username doesn't
            # appear in the freeswitch_ids, most likely because the user
            # audio isn't connected at all.  So we should probably paint
            # both of the mute and deaf controls as disabled.
            mute_button.configure(bg='white')
            mute_button.configure(image=mute_white_logo)
            deaf_button.configure(bg='white')
            deaf_button.configure(image=deaf_white_logo)

        window.after(250, set_correct_icon_status)

    global hand_raised
    hand_raised = False

    def toggle_hand(event):
        global hand_raised
        hand_raised = ~ hand_raised
        if hand_raised:
            hand_button.configure(bg='blue')
            hand_button.configure(image=hand_blue_logo)
        else:
            hand_button.configure(bg='white')
            hand_button.configure(image=hand_white_logo)

    def toggle_mute(event):
        freeswitch.get_status()
        try:
            if freeswitch.mute_status[freeswitch.freeswitch_ids[username]]:
                freeswitch.unmute_student(username)
                mute_button['bg'] = 'blue'
                mute_button['image'] = mute_blue_logo
            else:
                freeswitch.mute_student(username)
                mute_button['bg'] = 'white'
                mute_button['bg'] = mute_white_logo
        except:
            pass

    def toggle_deaf(event):
        freeswitch.get_status()
        try:
            if freeswitch.deaf_status[freeswitch.freeswitch_ids[username]]:
                freeswitch.undeaf_student(username)
                deaf_button['bg'] = 'blue'
                deaf_button['image'] = deaf_blue_logo
            else:
                freeswitch.deaf_student(username)
                deaf_button['bg'] = 'white'
                deaf_button['bg'] = deaf_white_logo
        except:
            pass

    hand_button.bind("<Button-1>", toggle_hand)
    mute_button.bind("<Button-1>", toggle_mute)
    deaf_button.bind("<Button-1>", toggle_deaf)

    mute_button.pack(side="left")
    deaf_button.pack(side="left")
    hand_button.pack(side="left")

    # Center audio control widget at the bottom of the screen
    # window.geometry("+" + str(int(screen_width/2 - button_size)) + "-0")

    # Put audio control widget at the bottom right of the screen
    # window.geometry("-0-0")

    # Put audio control widget at the top right of the screen
    window.geometry("-0+0")

    set_correct_icon_status()

    window.mainloop()
