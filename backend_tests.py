import docx
import os
import pandas as pd
import unittest
import xlsxwriter

from datetime import datetime

from backend import (
    base_query,
    add_attendee_query,
    get_list_all_attendees_query,
    get_attendee_info_query,
    remove_attendee_query,
    store_attendee_data_in_postgresql,
    create_text_version_list_of_all_attendees,
    get_attendees_list_format_docx,
    get_attendees_list_format_xlsx,
    xlsx_file_add_column_titles,
    xlsx_file_add_data
)
from config import get_database_configuration


# Functions and variables that save code
def remove_test_attendee(cur):
    sql = """DELETE FROM 
                    guestlist 
            WHERE 
                    first_name = 'Hermenegildo' 
                    AND last_name = 'Verycomplicatedname' 
                    AND phone = '111222333';
            SELECT 
                setval('guestlist_guest_id_seq',
                nextval('guestlist_guest_id_seq')-1);"""
    cur.execute(sql, )
    return cur, None

test_attendee_data = ('Hermenegildo', 'Verycomplicatedname', 'New York',
                      'Testers', 'jd@testers.com', '111222333',
                      datetime(2010, 10, 10, 10, 10, 10, 10))

# Tests
class BackendTests(unittest.TestCase):
    def test_get_database_configuration(self):
        """Checks if the data read from the configuration file is correct."""

        test_database_config_data = get_database_configuration(
            filename="conference_attendees.ini")
        self.assertEqual(test_database_config_data['host'],
                         os.environ['DB_HOST_CA'])
        self.assertEqual(test_database_config_data['database'],
                         os.environ['DB_DATABASE_CA'])
        self.assertEqual(test_database_config_data['user'],
                         os.environ['DB_USER_CA'])
        self.assertEqual(test_database_config_data['password'],
                         os.environ['DB_PASS_CA'])

    def test_base_query(self):
        """
        Checks if base_query is able to talk in a specific test_func,
        execute a very specific query within it and compares its
        result with the expected result.
        """
        def test_func(cur):
            sql = """SELECT * FROM guestlist_test WHERE guest_id = 50"""
            cur.execute(sql, )
            result = cur.fetchone()
            return cur, result
        test_attendee = base_query(test_func)
        self.assertEqual(str(test_attendee),
                         "(50, 'Miłosz', 'Wyrzbicki', 'Poznań',"
                         " 'Coders', 'aw@coders.com', '786978432',"
                         " datetime.datetime(2019, 9, 13, 13, 22, 15, 271516))")

    def test_add_attendee_querry_and_test_get_attendee_info_query(self):
        """
        Checks if the attendee is added to the database in the
        following steps:
        - uses the tested function
        - queries the database to see if the new record is there
        - compares it with the expected values
        - removes the data from the database
        - resets the PostgreSQL SEQUENCE to the value
        from the beginning of the transaction
        """
        base_query(add_attendee_query, test_attendee_data)
        test_attendee = base_query(get_attendee_info_query, 'Hermenegildo Verycomplicatedname')
        self.assertEqual(test_attendee_data, test_attendee[0][1:])
        base_query(remove_test_attendee)

    def test_get_list_all_attendees_query(self):
        """Checks data types of all attendees attributes."""
        all_attendees = base_query(get_list_all_attendees_query)
        for attendee in all_attendees:
            self.assertEqual(type(attendee), tuple)
            for attribute in attendee:
                if attribute == attendee[0]:
                    self.assertEqual(type(attribute), int)
                elif attribute == attendee[7]:
                    self.assertEqual(type(attribute), datetime)
                else:
                    self.assertEqual(type(attribute), str)


    def test_remove_attendee_query(self):
        """
        Checks if the chosen attendee is removed from the database by:
        - adding a test attendee
        - getting his data
        - removing the attendee base on this data
        - trying to query the same attendee again and making sure
        no results come back.
        """
        base_query(add_attendee_query, test_attendee_data)
        test_attendee = base_query(get_attendee_info_query, 'Hermenegildo Verycomplicatedname')
        base_query(remove_attendee_query, test_attendee[0][0])
        self.assertFalse(base_query(get_attendee_info_query, 'Hermenegildo Verycomplicatedname'))

    def test_store_attendee_data_in_postgresql(self):
        """Checks if the chosen attendee is added to the database."""
        store_attendee_data_in_postgresql(list(test_attendee_data[:6]))
        attendee = base_query(get_attendee_info_query, 'Hermenegildo Verycomplicatedname')
        for attribute in test_attendee_data[:6]:
            self.assertIn(attribute, attendee[0])
        base_query(remove_test_attendee)

    def test_create_text_version_list_of_all_attendees(self):
        """
        Checks if the text info about the attendees is returned
        as a properly structured string.
        """
        store_attendee_data_in_postgresql(list(test_attendee_data[:6]))
        list_all_attendees = base_query(get_list_all_attendees_query)
        attendees_list_text = create_text_version_list_of_all_attendees(
                                                        list_all_attendees)
        for attendee in attendees_list_text:
            self.assertEqual(type(attendee), str)
        self.assertEqual(attendees_list_text[0][:65],
                         'Hermenegildo Verycomplicatedname from New York'
                         ' working at Testers')
        base_query(remove_test_attendee)

    def test_get_attendees_list_format_docx(self):
        """
        Checks if a docx file is created and contains a specified
        form of text with attendees.
        """
        directory = get_attendees_list_format_docx('test.docx')
        doc = docx.Document(directory)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)

        attendees_list = base_query(get_list_all_attendees_query)
        for attendee, paragraph in zip(attendees_list, full_text):
            self.assertIn(
                    f"[ ] id {attendee[0]}:"
                    f"\n\t{attendee[1]} {attendee[2]} from {attendee[3]}"
                    f"\n\tWorking at {attendee[4]},"
                    f"\n\temail: {attendee[5]},"
                    f"\n\tnumber: {attendee[6]}",
                    paragraph)
        os.unlink('test.docx')  # cleanup

    def test_get_attendees_list_format_xlsx_returns_none(self):
        """Checks if the function without any arguments returns None."""
        self.assertEqual(get_attendees_list_format_xlsx(), None)

    def test_get_attendees_list_format_xlsx_returns_directory(self):
        """Checks if the function without any arguments returns the directory."""
        self.assertEqual(get_attendees_list_format_xlsx('test.xlsx'), 'test.xlsx')
        os.unlink('test.xlsx')

    def test_xlsx_file_add_column_titles(self):
        """
        Checks if the columns added to a newly created xlsx file
        is the same as intended.
        """
        column_titles = [
            "test1",
            "test2",
            "test3"
        ]

        xlsx_file = xlsxwriter.Workbook('test.xlsx')
        worksheet = xlsx_file.add_worksheet()
        xlsx_file_add_column_titles(column_titles, worksheet)
        xlsx_file.close()

        xlsx_file_check = pd.read_excel('test.xlsx')
        self.assertEqual(list(xlsx_file_check.columns), ['test1', 'test2', 'test3'])

        os.unlink('test.xlsx')

    def test_xlsx_file_add_data(self):
        """
        Checks if the data added to a newly created xlsx file
        is the same as intended.
        """
        row_data = (
            "test1",
            "test2",
            "test3"
        )
        multiple_rows = [row_data for _ in range(10)]

        xlsx_file = xlsxwriter.Workbook('test.xlsx')
        worksheet = xlsx_file.add_worksheet()
        xlsx_file_add_data(multiple_rows, worksheet)
        xlsx_file.close()

        xlsx_file_check = pd.read_excel('test.xlsx')
        for row in xlsx_file_check.values:
            self.assertEqual(tuple(row), row_data)

        os.unlink('test.xlsx')