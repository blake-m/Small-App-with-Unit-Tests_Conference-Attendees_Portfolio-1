# Conference Attendees
### Features:
 - keep track of: name, company, city, email, phone, last update
 - add a new attendee
 - remove an existing attendee (based on a database)
 - display information on an attendee
 - list all of the attendees -> output it to a docx file
 - buttons have tooltips
 
 ### Requirements
 - specified in requirements.txt
 
 ### How
 - Divided into frontend and backend
 - All the backend functions have their unit tests in backend_tests.py
 
 ### Version 1.1
 - Refactored the code so that the "base_query" function is now a decorator. Thanks to that the code is now more readable, maintainable and also many lines shorter.