import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('grouptech_app.db')

# Enable foreign key constraint support
conn.execute("PRAGMA foreign_keys = 1")

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create tables within the database
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_programs (
        program_ID INTEGER PRIMARY KEY,
        program_name TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_modules (
        module_ID INTEGER PRIMARY KEY,
        module_name TEXT NOT NULL,
        program_ID INTEGER,
        FOREIGN KEY (program_ID) REFERENCES tbl_programs(program_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_staff (
        staff_ID INTEGER PRIMARY KEY,
        staff_email TEXT NOT NULL,
        staff_name TEXT NOT NULL,
        staff_username TEXT NOT NULL,
        staff_password TEXT NOT NULL,
        program_ID INTEGER,
        FOREIGN KEY (program_ID) REFERENCES tbl_programs(program_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_students (
        student_ID INTEGER PRIMARY KEY,
        student_email TEXT NOT NULL,
        student_name TEXT NOT NULL,
        student_username TEXT NOT NULL,
        student_password TEXT NOT NULL,
        program_ID INTEGER,
        FOREIGN KEY (program_ID) REFERENCES tbl_programs(program_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_user (
        user_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        student_ID INTEGER,
        staff_ID INTEGER,
        FOREIGN KEY (student_ID) REFERENCES tbl_students(student_ID),
        FOREIGN KEY (staff_ID) REFERENCES tbl_staff(staff_ID),
        UNIQUE (student_ID),
        UNIQUE (staff_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_projects (
        project_ID INTEGER PRIMARY KEY,
        overall_grade TEXT,
        module_ID INTEGER,
        FOREIGN KEY (module_ID) REFERENCES tbl_modules(module_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_results (
        result_ID INTEGER PRIMARY KEY,
        individual_grade TEXT,
        contribution_score INTEGER,
        student_ID INTEGER,
        project_ID INTEGER,
        FOREIGN KEY (student_ID) REFERENCES tbl_students(student_ID),
        FOREIGN KEY (project_ID) REFERENCES tbl_projects(project_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_channels (
        channel_ID INTEGER PRIMARY KEY,
        channel_name TEXT NOT NULL,
        channel_description TEXT,
        channel_type TEXT CHECK(channel_type IN ('staff-only', 'task-info', 'both', 'private')) DEFAULT 'both',
        module_ID INTEGER,
        group_ID INTEGER,
        FOREIGN KEY (module_ID) REFERENCES tbl_modules(module_ID),
        FOREIGN KEY (group_ID) REFERENCES tbl_groups(group_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_group_members (
        group_member_ID INTEGER PRIMARY KEY,
        group_ID INTEGER,
        student_ID INTEGER,
        FOREIGN KEY (group_ID) REFERENCES tbl_groups(group_ID),
        FOREIGN KEY (student_ID) REFERENCES tbl_students(student_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_groups (
        group_ID INTEGER PRIMARY KEY,
        group_name TEXT NOT NULL,
        module_ID INTEGER,
        FOREIGN KEY (module_ID) REFERENCES tbl_modules(module_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_channel_members (
        channel_member_ID INTEGER PRIMARY KEY,
        role TEXT NOT NULL,
        channel_ID INTEGER,
        student_ID INTEGER,
        staff_ID INTEGER,
        FOREIGN KEY (channel_ID) REFERENCES tbl_channels(channel_ID),
        FOREIGN KEY (student_ID) REFERENCES tbl_students(student_ID),
        FOREIGN KEY (staff_ID) REFERENCES tbl_staff(staff_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_messages (
        message_ID INTEGER PRIMARY KEY,
        message_content TEXT NOT NULL,
        message_timestamp DATETIME NOT NULL,
        channel_ID INTEGER,
        student_ID INTEGER,
        staff_ID INTEGER,
        FOREIGN KEY (channel_ID) REFERENCES tbl_channels(channel_ID),
        FOREIGN KEY (student_ID) REFERENCES tbl_students(student_ID),
        FOREIGN KEY (staff_ID) REFERENCES tbl_staff(staff_ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tbl_private_messages (
        message_ID INTEGER PRIMARY KEY,
        sender_ID INTEGER,
        receiver_ID INTEGER,
        message_content TEXT NOT NULL,
        message_timestamp DATETIME NOT NULL,
        message_read BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (sender_ID) REFERENCES tbl_user(user_ID),
        FOREIGN KEY (receiver_ID) REFERENCES tbl_user(user_ID)
    )
''')

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("Database and tables created successfully.")
