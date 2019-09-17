import docx
import psycopg2 as pg2
import xlsxwriter

from config import get_database_configuration
from datetime import datetime


def base_query(func_to_modify):
    """
    Serves as a base for PostgreSQL queries. Use it to avoid Code Bloat.
    Opens and closes the connection each time, commits changes.
    Takes in a function (func) which should be a PostgreSQL query
    and arguments which are then transferred to the func function as its arguments.
    Returns query's result, if any - otherwise returns None.
    """
    def complete_query(*args):
        conn = None
        result = None
        try:
            parameters = get_database_configuration(filename="conference_attendees.ini")
            conn = pg2.connect(**parameters)
            cur = conn.cursor()
            # Here goes the query
            cur, result = func_to_modify(cur, *args)
            conn.commit()
            cur.close()
        except (Exception, pg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                return result

    return complete_query


@base_query
def store_attendee_data_in_postgresql(cur, attendee_data):
    """
    Takes in a list of attendee's data, adds current time to it,
    saves it in the database.
    """
    if len(attendee_data) == 6:
        attendee_data.append(datetime.now())
    first, last, city, company, email, phone, date = attendee_data

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


@base_query
def get_list_all_attendees(cur):
    """
    Creates and returns a list of tuples of attendee's data
    - each item in such a list is one piece of info.
    For example list[0][0] is first_name of the first attendee.
    """
    sql = """SELECT * FROM guestlist ORDER BY guest_id;"""
    cur.execute(sql)
    all_attendees = cur.fetchall()
    return cur, all_attendees


@base_query
def get_matching_attendees(cur, attendees_name):
    """Returns a list of tuples with attendees data."""
    sql = """SELECT * FROM guestlist
             WHERE first_name || ' ' || last_name
             ILIKE %s"""
    cur.execute(sql, (attendees_name,))
    attendees_list = cur.fetchall()
    return cur, attendees_list


@base_query
def remove_attendee(cur, guest_id):
    """
    Deletes an attendee from the database based on
    their guest_id.
    """
    sql = """DELETE FROM guestlist
             WHERE guest_id = %s;"""
    cur.execute(sql, (guest_id,))
    return cur, None


def create_text_version_list_of_all_attendees(list_from_query):
    """
    Takes in a list of tuples created by SQL query. For every
    tuple (position from SQL database) creates a text string
    that can be presented to the user. Returns a list of such
    strings.

    Result Example: John Doe from Warsaw wokring at GDF, id 55
    """
    counter = 0
    text_version_list_of_all_attendees = []
    for attendee in list_from_query:
        text_version_list_of_all_attendees.append(
            f"{attendee[1]} {attendee[2]} from {attendee[3]}"
            f" working at {attendee[4]}, id {attendee[0]}"
        )
        counter += 1
    return text_version_list_of_all_attendees


def get_attendees_list_format_docx(directory):
    """
    Takes in a directory with the 'to-be-created' filename.
    Creates a word document (*.docx) with a list of attendees.
    Returns the directory with the created file.
    """
    doc = docx.Document()
    attendees_list = get_list_all_attendees()
    counter = 0
    for attendee in attendees_list:
        attendees_list[counter] = (
            f"[ ] id {attendee[0]}:"
            f"\n\t{attendee[1]} {attendee[2]} from {attendee[3]}"
            f"\n\tWorking at {attendee[4]},"
            f"\n\temail: {attendee[5]},"
            f"\n\tnumber: {attendee[6]}"
        )
        doc.add_paragraph(attendees_list[counter])
        counter += 1
    doc.save(f"{directory}")
    return directory


def get_attendees_list_format_xlsx(directory=None):
    """
    Takes in a directory with the 'to-be-created' filename.
    Creates an excel document (*.xlsx) with a list of attendees.
    Returns the directory with the created file.
    """
    if directory is None:
        return None

    xlsx_file = xlsxwriter.Workbook(directory)
    worksheet = xlsx_file.add_worksheet()

    attendees_list = get_list_all_attendees()

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
    worksheet = xlsx_file_add_column_titles(column_titles, worksheet)
    xlsx_file_add_data(attendees_list, worksheet)
    xlsx_file.close()
    return directory


def xlsx_file_add_column_titles(column_titles, worksheet):
    """
    Takes in a list with column titles and and a worksheet opened
    with xlsxwriter module. Writes the column names into
    the worksheet. Returns the changed worksheet.
    """
    row, column = 0, 0
    for title in column_titles:
        worksheet.write(row, column, title)
        column += 1
    return worksheet


def xlsx_file_add_data(list_of_item_lists, worksheet):
    """
    Takes in a list with tuples of items and a worksheet opened
    with xlsxwriter module. Writes the items into
    the worksheet. Returns the changed worksheet.
    """
    row, column = 1, 0
    for item_list in list_of_item_lists:
        for item in item_list:
            if column == 7:
                item = item.strftime("%Y-%m-%d %H:%M:%S")
            worksheet.write(row, column, item)
            column += 1
        column = 0
        row += 1
    return worksheet
