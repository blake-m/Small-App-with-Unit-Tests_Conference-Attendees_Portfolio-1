# This program helps you keep track of conference attendees
#
# Features:
# - keep track of: name, company, city, email, phone, last update
# - add a new attendee
# - remove an existing attendee (based on a database)
# - display information on an attendee
# - list all of the attendees -> output it to a docx file
# - buttons have tooltips

# TO DO - protect yourself from SQL injections!
# https://stackoverflow.com/questions/45128902/psycopg2-and-sql-injection-security - to do conference attendees!

import sys
from gui import GUIMenu
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    menu = GUIMenu()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
