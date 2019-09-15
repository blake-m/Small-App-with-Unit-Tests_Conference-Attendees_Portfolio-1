import os
import unittest

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

test_attendee_data = ('Hermenegildo', 'Verycomplicatedname', 'New York', 'Testers',
                      'jd@testers.com', '111222333',
                      datetime(2010, 10, 10, 10, 10, 10, 10))

# Tests
class BackendTests(unittest.TestCase):
    def test_get_database_configuration(self):
        """Checks if the data read from the configuration file is correct."""

        test_database_config_data = get_database_configuration(
            filename="../conference_attendees.ini")
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
        store_attendee_data_in_postgresql()

    def test_create_text_version_list_of_all_attendees(self):
        create_text_version_list_of_all_attendees()

    def test_get_attendees_list_format_docx(self):
        get_attendees_list_format_docx()

    def test_get_attendees_list_format_xlsx(self):
        get_attendees_list_format_xlsx()

    def test_xlsx_file_add_column_titles(self):
        xlsx_file_add_column_titles()

    def test_xlsx_file_add_data(self):
        xlsx_file_add_data()