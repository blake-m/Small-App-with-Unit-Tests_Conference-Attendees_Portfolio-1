# This program helps you to keep track of conference attendees
#
# Features:
# - keeps track of: name, company, city, email, phone, last update
# - add a new attendee
# - remove an existing attendee (based on a database)
# - display information on an attendee
# - list all of the attendees -> output it to a docx file
# - buttons have tooltips

import docx
import psycopg2 as pg2
import sys
import re
import datetime

import xlsxwriter as xlsxwriter
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QFileDialog,
    QLineEdit,
)
from config import config


def base_query(func, *args):
    """
    Serves as a base for PostgreSQL queries. Use it to avoid Code Bloat.
    Opens and closes the connection each time, commits changes.
    Takes in a function (func) which should be a PostgreSQL query
    and arguments which are then transferred to the func function as its arguments.
    Returns query's result, if any - otherwise returns None.
    """

    conn = None
    result = None
    try:
        params = config(filename="conference_attendees.ini")
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
            return result


class GUIMenu(QWidget):
    """
    Main window for the app. It has 4 functions:
    -add an attendee based on users input
    -get info about an attendee based on a part of their name
    -export a word or excel file with the list
    -delete an attendee from the list.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        positions = [(i, j) for i in range(1, 3) for j in range(1, 3)]
        names = [
            "Add an attendee",
            "Delete an attendee",
            "Get info on an attendee",
            "Get full list",
        ]
        functions = [
            self.add_attendee_dialog,
            self.remove_attendee_dialog,
            self.get_info_dialog,
            self.get_list_dialog,
        ]
        tooltips = [
            "Adds an attendee based on your input",
            "Deletes an attendee chosen from the list",
            "Provides more information about an attendee based on your input",
            "Exports a list of attendees in xlsx or docx format",
        ]

        for position, name, function, tooltip in zip(
            positions, names, functions, tooltips
        ):
            button = QPushButton(name)
            # remove the hash to change the buttons color to gray
            # button.setStyleSheet("background-color: gray")
            button.setToolTip(tooltip)
            grid.addWidget(button, *position)
            button.clicked.connect(function)

        self.setLayout(grid)
        self.setGeometry(200, 200, 200, 200)
        self.setWindowTitle("CA System")
        self.show()

    def cancel(self):
        return self.close()

    def add_attendee_dialog(self):
        counter = 0
        attendee_data = []
        query_list = [
            "Attendee's first name",
            "Attendee's last name",
            "Attendee's city",
            "Attendee's company",
            "Attendee's email",
            "Attendee's phone number",
        ]

        # Get attendees data
        for query in query_list:
            text, ok = QInputDialog.getText(self, "Input Dialog", f"{query}:")
            if not ok:
                attendee_data = []
                break
            else:
                attendee_data.append(text)
                counter += 1

        # Confirm the attendee's data is correct
        if attendee_data:
            message_reply = QMessageBox.question(
                self,
                "Confirmation",
                "Do you want to add this attendee to the guest list?"
                f"\n\tName: {attendee_data[0]} {attendee_data[1]}"
                f"\n\tCity: {attendee_data[2]}"
                f"\n\tCompany: {attendee_data[3]}"
                f"\n\tEmail: {attendee_data[4]}"
                f"\n\tPhone: {attendee_data[5]}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            # If the data is correct, store it into PostgreSQL database and inform about the results
            if message_reply == QMessageBox.Yes:
                attendee_data.append(datetime.datetime.now())
                base_query(
                    self.add_attendee_query,
                    attendee_data[0],
                    attendee_data[1],
                    attendee_data[2],
                    attendee_data[3],
                    attendee_data[4],
                    attendee_data[5],
                    attendee_data[6],
                )
                QMessageBox.information(
                    self, "Continue", "Attendee created", QMessageBox.Ok
                )
            else:
                QMessageBox.information(
                    self, "Interrupted", "Operation interrupted!", QMessageBox.Ok
                )

    def add_attendee_query(self, cur, first, last, city, company, email, phone, date):
        """
        Works with base_query() function (needs cursor as an argument and returns cursor).
        Inserts attendee's data into PostgreSQL database
        """
        sql = """INSERT INTO guestlist(
                        first_name,
                        last_name,
                        city,
                        company,
                        email,
                        phone,
                        date_added)
                VALUES
                        (%s,%s,%s,%s,%s,%s,%s);"""
        cur.execute(sql, (first, last, city, company, email, phone, date))
        return cur, None

    def remove_attendee_dialog(self):
        items = base_query(
            self.get_all_attendees_query
        )  # Creates a list of lists of attendee's data
        counter = 0
        for item in items:
            items[counter] = f"{item[1]} {item[2]} from {item[3]} working at {item[4]}, id {item[0]}"
            counter += 1
        attendee, ok_pressed = QInputDialog.getItem(
            self,
            "Delete attendee",
            "Which attendee do you want" "\nto remove from the list?",
            items,
            0,
            False,
        )
        if ok_pressed and attendee:
            base_query(
                self.remove_attendee_query, re.search("\d+", attendee).group(), attendee
            )

    def get_all_attendees_query(self, cur):
        """
        Works with base_query() function (needs cursor as an argument and returns cursor).
        Creates and returns a list of lists of attendee's data - each item in such a list is one piece of info.
        For example list[0] is first_name.
        """
        sql = """SELECT * FROM guestlist;"""
        cur.execute(sql)
        items = cur.fetchall()
        return cur, items

    def remove_attendee_query(self, cur, guest_id, who_deleted):
        """
        Works with base_query() function (needs cursor as an argument and returns cursor).
        Deletes an attendee from the PostgreSQL database based on their id.
        """
        sql = """DELETE FROM guestlist
                 WHERE guest_id = %s;"""
        cur.execute(sql, (guest_id,))
        QMessageBox.information(
            self,
            "Continue",
            f"Attendee:\n{who_deleted}\nis now deleted",
            QMessageBox.Ok,
        )
        return cur, None

    def get_list_dialog(self):
        """
        Asks the user to choose what file format do they want to get the list in.
        """
        items = ("Word Document", "Excel Document")
        item, okPressed = QInputDialog.getItem(
            self, "File Format", "Format:", items, 0, False
        )
        if okPressed and item:
            if item == "Word Document":
                self.get_list_docx(self.get_list_save_file())
            elif item == "Excel Document":
                self.get_list_xlsx(self.get_list_save_file(".xlsx"))

    def get_list_save_file(self, format=".docx"):
        """
        Asks the user to specify where to save and how to name the file with the guest list.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Where do you want to save your file?",
            "",
            f"Microsoft Office {format} Files (*{format});;All Files (*)",
            options=options,
        )

        # Check if correct file format is about to be created, ask for input one more time if not.
        if file_name:
            if file_name.endswith(format):
                return file_name
            elif re.findall("\.+", file_name):
                self.get_list_dialog_error()
                self.get_list_dialog()
            else:
                file_name += format
                return file_name

    def get_list_dialog_error(self):
        QMessageBox.information(
            self, "Try again", "Incorrect File Name - try again!", QMessageBox.Ok
        )

    def get_list_docx(self, directory):
        """Creates a word document (*.docx) with a list of attendees."""
        doc = docx.Document()
        list = base_query(self.get_all_attendees_query)
        counter = 0
        for item in list:
            list[counter] = (
                f"[ ] id {item[0]}:"
                f"\n\t{item[1]} {item[2]} from {item[3]}"
                f"\n\tWorking at {item[4]},"
                f"\n\temail: {item[5]},"
                f"\n\tnumber: {item[6]}"
            )
            doc.add_paragraph(list[counter])
            counter += 1
        doc.save(f"{directory}")
        self.get_list_success(directory)

    def get_list_xlsx(self, directory):
        """Creates an excel document (*.xlsx) with a list of attendees."""

        # Create the file in a chosen directory
        xlsx = xlsxwriter.Workbook(directory)
        worksheet = xlsx.add_worksheet()

        # Get the data from the PostgreSQL database
        list = base_query(self.get_all_attendees_query)

        # Create the 1st row
        column_titles = [
            "id",
            "first name",
            "last_name",
            "city",
            "company",
            "email",
            "phone number",
            "date added",
        ]
        row, column = 0, 0
        for title in column_titles:
            worksheet.write(row, column, title)
            column += 1

        # Add data to the spreadsheet
        counter = 0
        row, column = 1, 0
        for position in list:
            l = list[counter]
            for item in l:
                if column == 7:
                    item = item.strftime("%Y-%m-%d %H:%M:%S")
                worksheet.write(row, column, item)
                column += 1
            column = 0
            row += 1
            counter += 1

        xlsx.close()
        self.get_list_success(directory)

    def get_list_success(self, directory):
        QMessageBox.information(
            self,
            "List ready",
            f"List successfully exported to:" f"\n{directory}",
            QMessageBox.Ok,
        )

    def get_info_dialog(self):
        """
        Based on user's input (name and/or last name required) returns complete information about an attendee.
        """
        # Get user's input
        text, ok_pressed = QInputDialog.getText(
            self,
            "Attendee info",
            "Provide attendee's name (or its part)",
            QLineEdit.Normal,
            "",
        )

        # Search for the name in the PostgreSQL database
        text = "%" + text + "%"
        if ok_pressed and text != "":
            list = base_query(self.get_info_query, text)
            if len(list) >= 8:
                QMessageBox.information(
                    self,
                    "Try again",
                    "There are too many matching results!\n\nTry more specified search :)"
                    * 500,
                    QMessageBox.Ok,
                )
                self.get_info_dialog()
            else:
                self.get_info_present(list)

    def get_info_query(self, cur, name):
        """
        Works with base_query() function (needs cursor as an argument and returns cursor).
        Searches the database for a name or/and last_name matching 'name' argument.
        """
        sql = """SELECT * FROM guestlist
                 WHERE first_name || ' ' || last_name
                 ILIKE %s"""
        cur.execute(sql, (name,))
        list = cur.fetchall()
        return cur, list

    def get_info_present(self, list):
        text = ""
        for item in list:
            text += (
                f"id {item[0]}:"
                f"\n\t{item[1]} {item[2]} from {item[3]}"
                f"\n\tWorking at {item[4]},"
                f"\n\temail: {item[5]},"
                f"\n\tnumber: {item[6]}\n\n"
            )
        QMessageBox.information(self, "Try again", f"{text}", QMessageBox.Ok)


def main():
    app = QApplication(sys.argv)
    menu = GUIMenu()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()