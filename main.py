import logging
from menu_definitions import menu_main, student_select, department_select, debug_select
from db_connection import engine, Session
from orm_base import metadata
# Note that until you import your SQLAlchemy declarative classes, such as Student, Python
# will not execute that code, and SQLAlchemy will be unaware of the mapped table.
from Student import Student
from Department import Department
from Option import Option
from Menu import Menu


def add_department(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    while True:
        unique_abbreviation = True
        unique_chair_name = True
        unique_building = True
        unique_office = True
        unique_description = True

        name = input("Department name --> ")
        abbr = input("Department abbreviation --> ")
        chairName = input("Department chair name --> ")
        building = input("Department building --> ")
        office = int(input("Department office --> "))
        description = input("Department description --> ")

        abbr_count = session.query(Department).filter(Department.abbreviation == abbr).count()
        if abbr_count > 0:
            print("Invalid, pick a different abbreviation.")
            unique_abbreviation = False

        chair_count = session.query(Department).filter(Department.chairName == chairName).count()
        if chair_count > 0:
            print("Invalid, pick a different chair name.")
            unique_chair_name = False

        office_count = session.query(Department).filter(Department.building == building,
                                                        Department.office == office).count()
        if office_count > 0:
            print("Invalid, pick a different office.")
            unique_office = False

        description_count = session.query(Department).filter(Department.description == description).count()
        if description_count > 0:
            print("Invalid, pick a different description.")
            unique_description = False

        if unique_abbreviation and unique_chair_name and unique_building and unique_office and unique_description:
            new_department = Department(
                name=name,
                abbreviation=abbr,
                chair_name=chairName,
                building=building,
                office=office,
                description=description
            )
            session.add(new_department)
            break


# select_department_abbreviation
def select_department_abbreviation(sess: Session) -> Department:
    """
    Prompt the user for a specific student by the department abbreviation.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    abbreviation: str = ''
    while not found:
        abbreviation = input("Enter the department abbreviation --> ")
        id_count: int = sess.query(Department).filter(Department.abbreviation == abbreviation).count()
        found = id_count == 1
        if not found:
            print("No department with that abbreviation.  Try again.")
    return_department: Department = sess.query(Department).filter(Department.abbreviation == abbreviation).first()
    return return_department


# select_department_chair_name
def select_department_chair_name(sess: Session) -> Department:
    """
    Select a department by the chair name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    chair_name: str = ''
    while not found:
        chair_name = input("Enter the department chair name --> ")
        id_count: int = sess.query(Department).filter(Department.chairName == chair_name).count()
        found = id_count == 1
        if not found:
            print("No department with that chair name.  Try again.")
    return_department: Department = sess.query(Department).filter(Department.chairName == chair_name).first()
    return return_department


# select_department_building_office
def select_department_building_office(sess: Session) -> Department:
    """
    Select a department by the combination of the building and office.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    building: str = ''
    office: int = -1
    while not found:
        building = input("Department building to delete--> ")
        office = input("Department office to delete--> ")
        building_office_count: int = sess.query(Department).filter(Department.building == building,
                                                                   Department.office == office).count()
        found = building_office_count == 1
        if not found:
            print("No department by that building/office.  Try again.")
    oldDepartment = sess.query(Department).filter(Department.building == building,
                                                  Department.office == office).first()
    return oldDepartment


# select_department_description
def select_department_description(sess: Session) -> Department:
    """
    Prompt the user for a specific department by the department description.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    description: str = ''
    while not found:
        description = input("Enter the department description --> ")
        id_count: int = sess.query(Department).filter(Department.description == description).count()
        found = id_count == 1
        if not found:
            print("No department with that description.  Try again.")
    return_department: Department = sess.query(Department).filter(Department.description == description).first()
    return return_department


def find_department(sess: Session) -> Department:
    """
    Prompt the user for attribute values to select a single deparment.
    :param sess:    The connection to the database.
    :return:        The instance of Department that the user selected.
                    Note: there is no provision for the user to simply "give up".
    """
    find_department_command = department_select.menu_prompt()
    match find_department_command:
        case "abbreviation":
            old_department = select_department_abbreviation(sess)
        case "chair_name":
            old_department = select_department_chair_name(sess)
        case "building/office":
            old_department = select_department_building_office(sess)
        case "description":
            old_department = select_department_description(sess)
        case _:
            old_department = None
    return old_department


def delete_department(session: Session):
    """
    Prompt the user for a department to delete using find_department.
    :param session: The connection to the database.
    :return:        None
    """
    print("deleting a department")
    oldDepartment = find_department(session)
    session.delete(oldDepartment)


def list_departments(session: Session):
    """
    List all of the departments, sorted by the abbreviation, then chair name, building and office,
    and then description.
    :param session:
    :return:
    """
    departments: [Department] = list(
        session.query(Department).order_by(Department.abbreviation, Department.chairName, Department.building,
                                           Department.office, Department.description))
    for department in departments:
        print(department)


def select_department_from_list(session):
    """
    Allow the user to select a department from a list of already added departments.
    :param session:     The connection to the database.
    :return:            None
    """
    departments: [Department] = list(
        sess.query(Department).order_by(Department.abbreviation, Department.chairName, Department.building,
                                        Department.office, Department.description))
    options: [Option] = []

    for department in departments:
        options.append(Option(
            f"{department.abbreviation}: {department.chairName}, {department.building}, {department.office}, {department.description}",
            department.abbreviation  # Use the abbreviation as the action value
        ))

    temp_menu = Menu('Department List', 'Select a department from this list', options)
    text_departmentName: str = temp_menu.menu_prompt()

    # Find the selected department based on the action (abbreviation)
    returned_department = sess.query(Department).filter(Department.abbreviation == text_departmentName).first()

    print("Selected department:", returned_department)


def add_student(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    unique_name: bool = False
    unique_email: bool = False
    lastName: str = ''
    firstName: str = ''
    email: str = ''
    # Note that there is no physical way for us to duplicate the student_id since we are
    # using the Identity "type" for studentId and allowing PostgreSQL to handle that.
    # See more at: https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-identity-column/
    while not unique_name or not unique_email:
        lastName = input("Student last name--> ")
        firstName = input("Student first name--> ")
        email = input("Student e-mail address--> ")
        name_count: int = session.query(Student).filter(Student.lastName == lastName,
                                                        Student.firstName == firstName).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = session.query(Student).filter(Student.eMail == email).count()
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that e-mail address.  Try again.")
    newStudent = Student(lastName, firstName, email)
    session.add(newStudent)


def select_student_id(sess: Session) -> Student:
    """
    Prompt the user for a specific student by the student ID.  Generally
    this is not a terribly useful approach, but I have it here for
    an example.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    ID: int = -1
    while not found:
        ID = int(input("Enter the student ID--> "))
        id_count: int = sess.query(Student).filter(Student.studentId == ID).count()
        found = id_count == 1
        if not found:
            print("No student with that ID.  Try again.")
    return_student: Student = sess.query(Student).filter(Student.studentId == ID).first()
    return return_student


def select_student_first_and_last_name(sess: Session) -> Student:
    """
    Select a student by the combination of the first and last name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    lastName: str = ''
    firstName: str = ''
    while not found:
        lastName = input("Student last name to delete--> ")
        firstName = input("Student first name to delete--> ")
        name_count: int = sess.query(Student).filter(Student.lastName == lastName,
                                                     Student.firstName == firstName).count()
        found = name_count == 1
        if not found:
            print("No student by that name.  Try again.")
    oldStudent = sess.query(Student).filter(Student.lastName == lastName,
                                            Student.firstName == firstName).first()
    return oldStudent


def select_student_email(sess: Session) -> Student:
    """
    Select a student by the e-mail address.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    email: str = ''
    while not found:
        email = input("Enter the student email address --> ")
        id_count: int = sess.query(Student).filter(Student.eMail == email).count()
        found = id_count == 1
        if not found:
            print("No student with that email address.  Try again.")
    return_student: Student = sess.query(Student).filter(Student.eMail == email).first()
    return return_student


def find_student(sess: Session) -> Student:
    """
    Prompt the user for attribute values to select a single student.
    :param sess:    The connection to the database.
    :return:        The instance of Student that the user selected.
                    Note: there is no provision for the user to simply "give up".
    """
    find_student_command = student_select.menu_prompt()
    match find_student_command:
        case "ID":
            old_student = select_student_id(sess)
        case "first/last name":
            old_student = select_student_first_and_last_name(sess)
        case "email":
            old_student = select_student_email(sess)
        case _:
            old_student = None
    return old_student


def delete_student(session: Session):
    """
    Prompt the user for a student by the last name and first name and delete that
    student.
    :param session: The connection to the database.
    :return:        None
    """
    print("deleting a student")
    oldStudent = find_student(session)
    session.delete(oldStudent)


def list_students(session: Session):
    """
    List all of the students, sorted by the last name first, then the first name.
    :param session:
    :return:
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    students: [Student] = list(session.query(Student).order_by(Student.lastName, Student.firstName))
    for student in students:
        print(student)


def select_student_from_list(session):
    """
    This is just a cute little use of the Menu object.  Basically, I create a
    menu on the fly from data selected from the database, and then use the
    menu_prompt method on Menu to display characteristic descriptive data, with
    an index printed out with each entry, and prompt the user until they select
    one of the Students.
    :param session:     The connection to the database.
    :return:            None
    """
    # query returns an iterator of Student objects, I want to put those into a list.  Technically,
    # that was not necessary, I could have just iterated through the query output directly.
    students: [Student] = list(sess.query(Student).order_by(Student.lastName, Student.firstName))
    options: [Option] = []  # The list of menu options that we're constructing.
    for student in students:
        # Each time we construct an Option instance, we put the full name of the student into
        # the "prompt" and then the student ID (albeit as a string) in as the "action".
        options.append(Option(student.lastName + ', ' + student.firstName, student.studentId))
    temp_menu = Menu('Student list', 'Select a student from this list', options)
    # text_studentId is the "action" corresponding to the student that the user selected.
    text_studentId: str = temp_menu.menu_prompt()
    # get that student by selecting based on the int version of the student id corresponding
    # to the student that the user selected.
    returned_student = sess.query(Student).filter(Student.studentId == int(text_studentId)).first()
    # this is really just to prove the point.  Ideally, we would return the student, but that
    # will present challenges in the exec call, so I didn't bother.
    print("Selected student: ", returned_student)


if __name__ == '__main__':
    print('Starting off')
    logging.basicConfig()
    # use the logging factory to create our first logger.
    # for more logging messages, set the level to logging.DEBUG.
    # logging_action will be the text string name of the logging level, for instance 'logging.INFO'
    logging_action = debug_select.menu_prompt()
    # eval will return the integer value of whichever logging level variable name the user selected.
    logging.getLogger("sqlalchemy.engine").setLevel(eval(logging_action))
    # use the logging factory to create our second logger.
    # for more logging messages, set the level to logging.DEBUG.
    logging.getLogger("sqlalchemy.pool").setLevel(eval(logging_action))

    metadata.drop_all(bind=engine)  # start with a clean slate while in development

    # Create whatever tables are called for by our "Entity" classes.
    metadata.create_all(bind=engine)

    with Session() as sess:
        main_action: str = ''
        while main_action != menu_main.last_action():
            main_action = menu_main.menu_prompt()
            print('next action: ', main_action)
            exec(main_action)
        sess.commit()
    print('Ending normally')
