
import subprocess
import os

import vnc_collaborate.freeswitch as freeswitch

HOME = os.environ['HOME']

def teacher_zoom(window, desktop_width, desktop_height):
   r"""
   teacher-zoom(WINDOW-NAME, DESKTOP_WIDTH, DESKTOP_HEIGHT)

   Called from fvwm when a student desktop is clicked in a teacher desktop view,
   this script is passed the window name of the miniaturized view-only student window
   on the teacher desktop (which was created by the teacher-desktop script).

   We decode the window name (which was set in teacher_desktop) to figure
   out the user name and X11 display name in order to launch a full-screen,
   fully interactive view of the student desktop, so that the teacher can
   interact with it.

   We also check to see if the student was deafed, and if so undeaf them
   on entry, then re-deaf the student after the full-screen view exits.
   """

   # See FVWM man page on $[w.name] - the window name is encased in single quotes
   # and embedded single quotes are escaped with a backspace.  The window name
   # created in the teacher_desktop.py script has the fields separated by semicolons.
   # So, this expression undoes the FVWM quoting and splits apart our arguments.

   args = window.replace("\\'", "'")[1:-1].split(';')

   if len(args) == 3 and args[0] == 'TeacherViewVNC':

      STUDENT_ID = args[1]
      STUDENT_DISPLAY = args[2]

      print(STUDENT_ID, STUDENT_DISPLAY)

      freeswitch.print_status()

      was_deafed = freeswitch.is_deaf(STUDENT_ID, default=False)

      # If the student was deafed, undeaf them, since we're probably about to talk to them
      if was_deafed:
         freeswitch.undeaf_student(STUDENT_ID)

      geometry = desktop_width + 'x' + desktop_height

      args = ['ssvncviewer', '-title', 'Zoomed Student Desktop',
              '-geometry', geometry, '-scale', geometry,
              '-escape', 'Alt_L', '-passwd', HOME + '/.vnc/passwd',
              STUDENT_DISPLAY]

      proc = subprocess.Popen(args)
      proc.wait()

      # Re-deaf the student, but ONLY if they were deafed originally
      if was_deafed:
         freeswitch.deaf_student(STUDENT_ID)
