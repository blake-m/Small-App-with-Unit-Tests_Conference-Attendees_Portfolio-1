# TO DO: dorób wszystkie To Do, usun pliki, które są niepotrzebne... posprzątaj  - wsadz na git
# potem zrob testy i znow refactor i znow na git!

import re
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QFileDialog,
    QLineEdit,
)

from backend import (
    base_query,
    create_text_version_list_of_all_attendees,
    get_attendees_list_format_docx,
    get_attendees_list_format_xlsx,
    get_list_all_attendees_query,
    get_matching_attendees,
    remove_attendee_query,
    store_attendee_data_in_postgresql
)

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
        self.initialize_user_interface()

    def initialize_user_interface(self):
        """
        Initializes the GUI."""
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
            self.get_attendee_info_dialog,
            self.get_attendees_list_file_dialog
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
            # remove the hash tag to change the buttons color to gray
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

    def get_attendee_data_dialog(self, query_list):
        """
        Gets input from the user by showing him a small dialog window for every
        position on the query_list. Returns a list with the data acquired.
        """
        attendee_data = []
        for query in query_list:
            text, ok = QInputDialog.getText(self, "Input Dialog", f"{query}:")
            if not ok:
                attendee_data = []
                break
            else:
                attendee_data.append(text)
        return attendee_data

    def user_confirm_attendee_data_is_correct(self, attendee_data):
        """
        Takes in a list with the attendee's data. Shows it to the user.
        Returns user's decision regarding the data's correctness.
        """
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
            return message_reply


    def add_attendee_dialog(self):
        """
        Based on the specified query_list gets attendee data from the user and saves it
        to the database if the user confirms the data is correct.
        """
        query_list = [
            "Attendee's first name",
            "Attendee's last name",
            "Attendee's city",
            "Attendee's company",
            "Attendee's email",
            "Attendee's phone number",
        ]

        attendee_data = self.get_attendee_data_dialog(query_list)
        user_response = self.user_confirm_attendee_data_is_correct(attendee_data)

        # If the data is correct, store it into PostgreSQL database and inform about the results
        if user_response == QMessageBox.Yes:
            store_attendee_data_in_postgresql(attendee_data)
            QMessageBox.information(
                self, "Continue", "Attendee created", QMessageBox.Ok
            )
        else:
            QMessageBox.information(
                self, "Interrupted", "Operation interrupted!", QMessageBox.Ok
            )


    def user_choice_attendee_to_delete(self, attendee_list):
        """
        Based on a list of attendee's provided shows a dialog to the user.
        User needs to choose which attendee to delete. Returns the attendee
        that is to be deleted and confirmation that 'ok' was pressed.
        """
        attendee_to_delete, ok_pressed = QInputDialog.getItem(
            self,
            "Delete attendee",
            "Which attendee do you want" "\nto remove from the list?",
            attendee_list,
            0,
            False,
        )
        return attendee_to_delete, ok_pressed

    def deletion_successful_show_information(self, who_deleted):
        """
        Takes in a string of information about who was deleted from the database
        and shows a communicate to the user.
        """
        QMessageBox.information(
            self,
            "Continue",
            f"Attendee:\n{who_deleted}\nis now deleted",
            QMessageBox.Ok,
        )

    def remove_attendee_dialog(self):
        # TO DO: DOCSTRING
        list_of_all_attendees = base_query(
            get_list_all_attendees_query
        )
        text_version_list_of_all_attendees = \
            create_text_version_list_of_all_attendees(list_of_all_attendees)

        attendee_to_delete, ok_pressed = \
            self.user_choice_attendee_to_delete(text_version_list_of_all_attendees)

        if ok_pressed and attendee_to_delete:
            base_query(
                remove_attendee_query, re.search("\d+", attendee_to_delete).group()
            )
            self.deletion_successful_show_information(attendee_to_delete)

    def user_choice_attendees_list_file_format(self):
        """
        Presents a dialog to the user. The user can choose which file format
        is preferred. Returns the choice and confirmation.
        """
        available_formats = ("Word Document", "Excel Document")
        chosen_format, okPressed = QInputDialog.getItem(
            self, "File Format", "Format:", available_formats, 0, False
        )
        return chosen_format, okPressed

    def get_attendees_list_file_dialog(self):
        """
        Based on the user's format choice saves the attendee's list to a chosen
        directory.
        """
        chosen_format, confirmation = self.user_choice_attendees_list_file_format()

        if confirmation and chosen_format:
            if chosen_format == "Word Document":
                directory = get_attendees_list_format_docx(
                        self.get_attendees_list_save_file())
                if directory: self.get_attendees_list_show_success(directory)
            elif chosen_format == "Excel Document":
                directory = get_attendees_list_format_xlsx(
                        self.get_attendees_list_save_file(".xlsx"))
                if directory: self.get_attendees_list_show_success(directory)



    def get_attendees_list_save_file(self, format=".docx"):
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
        # Check if correct file format is about to be created, ask for input one more time if not.'
        if file_name:
            if file_name.endswith(format):
                return file_name
            elif re.findall("\.+", file_name):
                self.get_attendees_list_show_error()
                self.get_attendees_list_save_file()
            else:
                file_name += format
                return file_name

    def get_attendees_list_show_error(self):
        """Shows error message when an incorrect filename was chosen."""
        QMessageBox.information(
            self, "Try again", "Incorrect File Name - try again!", QMessageBox.Ok
        )

    def get_attendees_list_show_success(self, directory):
        """
        Takes in a directory and shows a success message stating
        that the file was successfully created there.
        """
        QMessageBox.information(
            self,
            "List ready",
            f"List successfully exported to:" f"\n{directory}",
            QMessageBox.Ok,
        )

    def user_input_attendees_name(self):
        """Presents a dialog to a user. Returns the text input."""
        user_input, _ = QInputDialog.getText(
            self,
            "Attendee info",
            "Provide attendee's name (or its part)",
            QLineEdit.Normal,
            "",
        )
        return user_input

    # TO DO: refactor from here
    def get_attendee_info_dialog(self):
        """
        Based on user's input (name and/or last name required)
        returns complete information about an attendee.
        """
        user_input = self.user_input_attendees_name()
        user_input = "%".join(user_input.join("%"))

        if user_input != "%%":
            matching_attendees_list = get_matching_attendees(user_input)
            if len(matching_attendees_list) >= 7:
                self.too_many_matching_results_show_info()
                self.get_info_dialog()
            else:
                self.get_attendee_info_present(matching_attendees_list)

    def too_many_matching_results_show_info(self):
        """
        Shows an information message when
        too many matching attendees were found.
        """
        QMessageBox.information(
            self,
            "Try again",
            "There are too many matching results!\n\nTry more specified search :)"
            * 500,
            QMessageBox.Ok,
        )

    def get_attendee_info_present(self, matching_attendees_list):
        # TO DO: DOCSTRING
        text = ""
        for item in matching_attendees_list:
            text += (
                f"id {item[0]}:"
                f"\n\t{item[1]} {item[2]} from {item[3]}"
                f"\n\tWorking at {item[4]},"
                f"\n\temail: {item[5]},"
                f"\n\tnumber: {item[6]}\n\n"
            )
        QMessageBox.information(self, "Try again", f"{text}", QMessageBox.Ok)
