import psycopg2 as pg2
import sys
import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QPushButton, QLabel, QComboBox, QToolTip, \
    QInputDialog, QMessageBox
from config import config


# This program helps you to keep track of conference attendees
#
# Features:
# - keeps track of: name, company, city, email, phone, last update
# - add a new attendee
# - remove an existing attendee
# - display information on an attendee
# - list all of the attendees -> output it to a docx file


def base_query(func, *args):
    """
    Serves as a base for PostgreSQL queries. Use it to avoid Code Bloat.
    Opens and closes the connection each time, commits changes.
    Returns query's result, if any - otherwise returns None.
    """

    conn = None
    try:
        params = config(filename='conference_attendees.ini')
        conn = pg2.connect(**params)
        cur = conn.cursor()
        # Here goes the query
        cur, result = func(cur, *args)
        conn.commit()
        cur.close()
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

class Attendee:

    def __init__(self):
        self.id = None
        self.name = None
        self.company = None
        self.city = None
        self.email = None
        self.phone = None
        self.last_update = None

class GUIWXXXXXXXXXXXXXXXXXXXXX(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.setLayout(grid)
        self.setGeometry(200, 200, 200, 200)
        self.setWindowTitle('Which Attendee')
        self.show()



class GUIMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        positions = [(i, j) for i in range(1, 3) for j in range(1, 3)]
        names = ['Add an attendee', 'Delete and attendee',
                 'Get info on an attendee', 'Get full list']
        functions = [self.add_attendee_dialog, self.cancel,
                     self.cancel, self.cancel]

        for position, name, function in zip(positions, names, functions):
            button = QPushButton(name)
            button.setStyleSheet("background-color: gray")
            grid.addWidget(button, *position)
            button.clicked.connect(function)
            button.clicked.connect(self.cancel)

        self.setLayout(grid)
        self.setGeometry(200, 200, 200, 200)
        self.setWindowTitle('CA System')
        self.show()

    def get_info(self):
        return 'lol'

    def add_attendee_dialog(self):
        counter = 0
        attendee_data = []
        query_list = ["Attendee's first name",
                      "Attendee's last name",
                      "Attendee's city",
                      "Attendee's company",
                      "Attendee's email",
                      "Attendee's phone number"]
        for query in query_list:
            text, ok = QInputDialog.getText(self, 'Input Dialog',
                                            f"{query}:")
            if not ok:
                attendee_data = []
                break
            else:
                attendee_data.append(text)
                counter += 1

        if attendee_data:
            message_reply = QMessageBox.question(self, 'Confirmation',
                                                 'Do you want to add this attendee to the guest list?'
                                                 f'\n\tName: {attendee_data[0]} {attendee_data[1]}'
                                                 f'\n\tCity: {attendee_data[2]}'
                                                 f'\n\tCompany: {attendee_data[3]}'
                                                 f'\n\tEmail: {attendee_data[4]}'
                                                 f'\n\tPhone: {attendee_data[5]}',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if message_reply == QMessageBox.Yes:
                print('Yes clicked1.')
                base_query(
                    self.add_attendee_query,
                    attendee_data[0],
                    attendee_data[1],
                    attendee_data[2],
                    attendee_data[3],
                    attendee_data[4],
                    attendee_data[5]
                )
                QMessageBox.information(self, "Continue", "Attendee created", QMessageBox.Ok)
            else:
                print('No clicked.')

            attendee_data.append(datetime.datetime.now())
            print(attendee_data)   # To remove

    def add_attendee_query(self, cur, first, last, city, company, email, phone):
        print(type(first), type(last), type(city), type(company), type(email), type(phone))
        sql = '''INSERT INTO guestlist(
                        first_name,
                        last_name,
                        city,
                        company,
                        email,
                        phone)
                VALUES
                        (%s,%s,%s,%s,%s,%s);'''
        cur.execute(sql, (first, last, city, company, email, phone))
        return cur, None

    def cancel(self):
        pass
        # return self.close()


# def main_loop():
#     menu = GUIMenu()
#

def main():
    app = QApplication(sys.argv)
    menu = GUIMenu()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
