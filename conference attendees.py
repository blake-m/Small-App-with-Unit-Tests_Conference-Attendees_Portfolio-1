import psycopg2
import sys
from PyQt5 import QApplication, QMainWindow
from config import config

# This program helps you to keep track of conference attendees
#
# Features:
# - keeps track of: name, company, state, email, phone
# - add a new attendee
# - remove an existing attendee
# - display inormation on an attendee
# - list all of the attendees -> output it to a docx file




if __name__ == '__main__':
    main()