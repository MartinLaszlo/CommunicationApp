import sqlite3
from itertools import combinations
from datetime import datetime, timedelta

# Database connection
def get_db_connection():
    conn = sqlite3.connect('grouptech_app.db')
    conn.row_factory = sqlite3.Row
    return conn

# Get student project details with the correct joins
def get_student_projects(student_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.project_ID, p.overall_grade, r.individual_grade, r.contribution_score, p.module_ID
        FROM tbl_results r
        INNER JOIN tbl_projects p ON r.project_ID = p.project_ID
        WHERE r.student_ID = ?
    ''', (student_ID,))
    projects = cursor.fetchall()
    conn.close()
    print(f"Projects fetched for student_ID {student_ID}: {projects}")
    return projects

# Calculate scores with weights using averages of grade, overall grade, amount of projects and contribution scores
def calculate_student_score(student_ID, module_ID, weights):
    projects = get_student_projects(student_ID)
    score = 0
    num_projects = len(projects)
    
    if num_projects == 0:
        return 0

    sum_overall_grade = 0
    sum_individual_grade = 0
    sum_contribution_score = 0

    for project in projects:
        sum_overall_grade += int(project['overall_grade'])
        sum_individual_grade += int(project['individual_grade'])
        sum_contribution_score += project['contribution_score']

    avg_overall_grade = sum_overall_grade / num_projects
    avg_individual_grade = sum_individual_grade / num_projects
    avg_contribution_score = sum_contribution_score / num_projects

    score += (weights['w1'] * num_projects +
              weights['w2'] * avg_overall_grade +
              weights['w3'] * avg_individual_grade +
              weights['w4'] * avg_contribution_score)

    weight_multiplier = 1.5 if any(project['module_ID'] == module_ID for project in projects) else 1
    return score * weight_multiplier

# Form groups based on scores and group sizes
def form_groups(student_queue, target_score_range, size):
    valid_groups = []
    for group in combinations(student_queue, size):
        total_score = sum(student['score'] for student in group)
        if target_score_range[0] <= total_score <= target_score_range[1]:
            valid_groups.append(group)
            for student in group:
                student_queue.remove(student)  # Ensure they are not considered for other groupings
    print(f"Formed groups: {valid_groups}")
    return valid_groups

# Add group into the database
def insert_group_into_db(module_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tbl_groups (module_ID, group_name) VALUES (?, ?)
    ''', (module_ID, "Placeholder"))
    group_id = cursor.lastrowid
    group_name = f"Group {group_id}"
    cursor.execute('''
        UPDATE tbl_groups SET group_name = ? WHERE group_ID = ?
    ''', (group_name, group_id))
    conn.commit()
    conn.close()
    return group_id, group_name

# Add students into group and private groupchat
def finalize_group(module_ID, group):
    group_id, group_name = insert_group_into_db(module_ID)
    conn = get_db_connection()
    cursor = conn.cursor()
    for student in group:
        cursor.execute('''
            INSERT INTO tbl_group_members (group_ID, student_ID) VALUES (?, ?)
        ''', (group_id, student['student_ID']))

    channel_name = f"Group {group_id}"
    cursor.execute('''
        INSERT INTO tbl_channels (channel_name, module_ID, group_ID) VALUES (?, ?, ?)
    ''', (channel_name, module_ID, group_id))
    conn.commit()
    conn.close()

    print(f"Finalized group {group_name} with channel {channel_name} for module {module_ID}: {group}")
    return group_id, group_name