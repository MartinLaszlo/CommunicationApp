import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('grouptech_app.db')
cursor = conn.cursor()

# Sample test data
programs = [
    # program_name
    ('Computer Science',),
    ('Business Administration',),
    ('Information Technology',),
    ('Engineering',),
    ('Digital Marketing',)
]

modules = [
    # module_name, program_ID
    ('Introduction to Programming', 1),
    ('Data Structures and Algorithms', 1),
    ('Computer Networks', 1),
    ('Operating Systems', 1),
    ('Software Engineering', 1),

    ('Principles of Management', 2),
    ('Organizational Behavior', 2),
    ('Marketing Fundamentals', 2),
    ('Financial Accounting', 2),
    ('Business Law', 2),

    ('Web Development', 3),
    ('Database Systems', 3),
    ('Information Security', 3),
    ('Cloud Computing', 3),
    ('Network Administration', 3),

    ('Calculus for Engineers', 4),
    ('Physics of Mechanics', 4),
    ('Introduction to Thermodynamics', 4),
    ('Electrical Circuits', 4),
    ('Material Science', 4),

    ('Content Marketing', 5),
    ('SEO Fundamentals', 5),
    ('Social Media Marketing', 5),
    ('Email Marketing', 5),
    ('Digital Analytics', 5),

]

staff = [
    # staff_email, staff_name, staff_username, staff_password, program_ID
    ('staff1@example.com', 'Alex Johnson', 'alex_johnson', 'pass123', 1),
    ('staff2@example.com', 'Maria Garcia', 'maria_garcia', 'pass123', 1),
    ('staff3@example.com', 'James Wilson', 'james_wilson', 'pass123', 2),
    ('staff4@example.com', 'Robert Anderson', 'robert_anderson', 'pass123', 2),
    ('staff5@example.com', 'Patricia Taylor', 'patricia_taylor', 'pass123', 3),
    ('staff6@example.com', 'David Thomas', 'david_thomas', 'pass123', 3),
    ('staff7@example.com', 'Michael Martinez', 'michael_martinez', 'pass123', 4),
    ('staff8@example.com', 'Jennifer Hernandez', 'jennifer_hernandez', 'pass123', 4),
    ('staff9@example.com', 'William Jones', 'william_jones', 'pass123', 5),
    ('staff10@example.com', 'Elizabeth Taylor', 'elizabeth_taylor', 'pass123', 5),
]

students = [
    #  student_email, student_name, student_username, student_password, program_ID
    ('student1@example.com', 'Alice Brown', 'alice_brown', 'pass123', 1),
    ('student2@example.com', 'Bob Jones', 'bob_jones', 'pass123', 1),
    ('student11@example.com', 'Kevin Taylor', 'kevin_taylor', 'pass123', 1),
    ('student12@example.com', 'Laura Walker', 'laura_walker', 'pass123', 1),
    ('student99@example.com', 'Victor Smith', 'victor_smith', 'pass123', 1),
    ('student3@example.com', 'Charlie Davis', 'charlie_davis', 'pass123', 2),
    ('student4@example.com', 'Diana Green', 'diana_green', 'pass123', 2),
    ('student13@example.com', 'Mason White', 'mason_white', 'pass123', 3),
    ('student14@example.com', 'Nora Young', 'nora_young', 'pass123', 4),
    ('student5@example.com', 'Ethan Hall', 'ethan_hall', 'pass123', 5),
]

projects = [
    (90, 1,),
    (75, 1,),
    (80, 1,),
    (98, 1,),
    (47, 1,),
    (32, 1,),
    (47, 1,),
    (89, 1,),
    (90, 9,),
    (30, 10,),
    (65, 11,),
    (71, 12,),
    (89, 13,),
    (45, 14,),
    (53, 15,),
    (73, 16,),
    (13, 17,),
    (89, 18,),
    (33, 19,),
    (47, 20,),
    (84, 21,),
    (73, 22,),
    (77, 23,),
    (57, 24,),
    (66, 25,),
    (43, 26,),
    (72, 27,),
    (95, 28,),
    (35, 29,),
    (47, 30,),
]

results = [
    # individual_grade, contribution_score, student_ID, project_ID
    (90, 20, 1, 1),  # Assuming '90' is the individual_grade, '20' is the contribution_score
    (75, 25, 1, 2),  # Student 1
    (85, 20, 1, 3),
        
    (90, 10, 2, 1),  # Student 2
    (75, 25, 2, 2),
    (85, 25, 2, 3),

    (90, 25, 3, 1),  # Student 3
    (75, 25, 3, 2),
    (85, 40, 3, 3),

    (90, 30, 4, 1),  # Student 4
    (75, 25, 4, 2),
    (85, 15, 4, 3),

    (60, 60, 5, 1),  # lower grade student for test.
    (40, 25, 5, 6),
    (40, 30, 5, 7),
]


channels = [
    #channel_name, channel_description, channel_type ('staff-only', 'task-info', 'both'), module_ID, group_ID
    ('Staff', 'General discussion', 'staff-only', 1),
    ('Tasks', 'General discussion', 'task-info', 1),
    ('General', 'General discussion', 'both', 1),
    ('Homework', 'Homework questions', 'both', 1),

    ('Staff', 'General discussion', 'staff-only', 2),
    ('Tasks', 'General discussion', 'task-info', 2),
    ('General', 'General discussion', 'both', 2),
    ('Homework', 'Homework questions', 'both', 2),

    ('Staff', 'General discussion', 'staff-only', 3),
    ('Tasks', 'General discussion', 'task-info', 3),
    ('General', 'General discussion', 'both', 3),
    ('Homework', 'Homework questions', 'both', 3),

    ('Staff', 'General discussion', 'staff-only', 4),
    ('Tasks', 'General discussion', 'task-info', 4),
    ('General', 'General discussion', 'both', 4),
    ('Homework', 'Homework questions', 'both', 4),
    
    ('Staff', 'General discussion', 'staff-only', 5),
    ('Tasks', 'General discussion', 'task-info', 5),
    ('General', 'General discussion', 'both', 5),
    ('Homework', 'Homework questions', 'both', 5),
]

channel_members = [
    # role, channel_ID, student_ID, staff_ID
    ('read', 1, 1, None),
    ('read', 1, 2, None),
    ('write', 1, None, 1),
]

messages = [
    # content, timestamp, channel, staff/student
    ('Welcome to the General channel!', '2024-03-18 09:00:00', 1, None, 1),
    ('Can someone explain this week\'s homework?', '2024-03-18 09:05:00', 2, 1, None),
]

groups = [
    ('Group 1', 1),  # Group name, Module ID
    ('Group 2', 1),
    ('Group 1', 2),  
    ('Group 2', 2),
    ('Group 1', 3),  
    ('Group 2', 3),
    ('Group 1', 4),  
    ('Group 2', 4),
    ('Group 1', 5),  
    ('Group 2', 5),
]

group_members = [
    # Group ID, Student ID
    (30, 10),
    (30, 22),
    (30, 43),
    (30, 54),
]

# test data for private_messages using new unified user_IDs
private_messages = [
    # Assuming user_IDs as mapped above: Student 1 (ID 1), Student 2 (ID 2), Staff 1 (ID 3), Staff 2 (ID 4)
    # sender_ID, receiver_ID, message_content, message_timestamp, message_read
    (1, 2, 'Student to student 1 to 2.', '2024-04-01 10:00:00', False),
    (2, 1, 'Student to student 2 to 1', '2024-04-01 10:05:00', False),
    (11, 12, 'Staff to staff 1 to 2', '2024-04-01 11:00:00', False),
    (12, 11, 'Staff to staff 2 to 1', '2024-04-01 11:10:00', False),
    (1, 12, 'Hi, do you have updates on our meeting? student 1 to staff 2', '2024-04-01 12:00:00', False),
    (12, 1, 'Yes, let’s meet tomorrow at 10 AM. staff 2 to student 1', '2024-04-01 12:05:00', False)
]

# Students: 1, 2
# Staff: 1, 2

user_mappings = [
    (1, None),  # student 1
    (2, None),  # student 2
    (3, None),  
    (4, None),  
    (5, None),  
    (6, None),  
    (7, None),  
    (8, None),  
    (9, None),  
    (10, None),  
    (None, 1),  # staff 1
    (None, 2),   # staff 2
    (None, 3),  
    (None, 4),  
    (None, 5),  
    (None, 6), 
    (None, 7),  
    (None, 8), 
    (None, 9),  
    (None, 10), 
]



# Insert test data into the database
with conn:
    cursor.executemany('INSERT INTO tbl_programs (program_name) VALUES (?)', programs)
    cursor.executemany('INSERT INTO tbl_modules (module_name, program_ID) VALUES (?, ?)', modules)
    cursor.executemany('INSERT INTO tbl_staff (staff_email, staff_name, staff_username, staff_password, program_ID) VALUES (?, ?, ?, ?, ?)', staff)
    cursor.executemany('INSERT INTO tbl_students (student_email, student_name, student_username, student_password, program_ID) VALUES (?, ?, ?, ?, ?)', students)
    cursor.executemany('INSERT INTO tbl_projects (overall_grade, module_ID) VALUES (?, ?)', projects)
    cursor.executemany('INSERT INTO tbl_results (individual_grade, contribution_score, student_ID, project_ID) VALUES (?, ?, ?, ?)', results)
    cursor.executemany('INSERT INTO tbl_channels (channel_name, channel_description, channel_type, module_ID) VALUES (?, ?, ?, ?)', channels)
    cursor.executemany('INSERT INTO tbl_channel_members (role, channel_ID, student_ID, staff_ID) VALUES (?, ?, ?, ?)', channel_members)
    cursor.executemany('INSERT INTO tbl_messages (message_content, message_timestamp, channel_ID, student_ID, staff_ID) VALUES (?, ?, ?, ?, ?)', messages)
    cursor.executemany('INSERT INTO tbl_groups (group_name, module_ID) VALUES (?, ?)', groups)
    cursor.executemany('INSERT INTO tbl_group_members (group_ID, student_ID) VALUES (?, ?)', group_members)
    cursor.executemany('''INSERT INTO tbl_private_messages (sender_ID, receiver_ID, message_content, message_timestamp, message_read) VALUES (?, ?, ?, ?, ?)''', private_messages)
    cursor.executemany('INSERT INTO tbl_user (student_ID, staff_ID) VALUES (?, ?)', user_mappings)
conn.commit()  
conn.close()  

print("Test data inserted successfully.")
