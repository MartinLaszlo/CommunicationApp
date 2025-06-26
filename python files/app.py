from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime, timedelta
from threading import Lock
from threading import Timer
from grouping_algorithm import get_student_projects, calculate_student_score, form_groups, insert_group_into_db, finalize_group
from itertools import combinations 
from werkzeug.utils import secure_filename
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
import os
import json
import sqlite3

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")
lock = Lock()

# Connect to database
def get_db_connection():
    conn = sqlite3.connect('grouptech_app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "Welcome to the GroupTech Education App API!"

# Get programs
@app.route('/programs', methods=['GET']) 
def get_programs():
    conn = get_db_connection()
    programs = conn.execute('SELECT * FROM tbl_programs').fetchall()
    conn.close()
    return jsonify([dict(row) for row in programs])

# Add channel member
@app.route('/channels/<int:channel_ID>/members', methods=['POST'])
def add_channel_member(channel_ID):
    member = request.json
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tbl_channel_members (channel_ID, student_ID, staff_ID, role) VALUES (?, ?, ?, ?)',
        (channel_ID, member.get('student_ID'), member.get('staff_ID'), member['role']))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "response": "Channel member added successfully"}), 201

# Use channel to get messages
@app.route('/channels/<int:channel_id>/messages', methods=['GET'])
def get_messages_for_channel(channel_id):
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM tbl_messages WHERE channel_ID = ?', (channel_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in messages])

# Send message
@app.route('/channels/<int:channel_id>/messages', methods=['POST'])
def post_message_to_channel(channel_id):
    message_data = request.json
    conn = get_db_connection()
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO tbl_messages (message_content, message_timestamp, channel_ID, student_ID, staff_ID)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (message_data['content'], current_timestamp, channel_id, message_data.get('student_ID'), message_data.get('staff_ID'))
        )
        conn.commit()
        last_message_id = cursor.lastrowid
        message = conn.execute('SELECT * FROM tbl_messages WHERE message_ID = ?', (last_message_id,)).fetchone()
        conn.close()
        if message:
            return jsonify(dict(message)), 201
        else:
            return jsonify({"error": "Message not found after insertion"}), 404
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

# Get program's modules
@app.route('/programs/<int:program_id>/modules', methods=['GET'])
def get_modules_for_program(program_id):
    conn = get_db_connection()
    modules = conn.execute('SELECT * FROM tbl_modules WHERE program_ID = ?', (program_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in modules])

# Student authentication (passing student information)
@app.route('/login/student', methods=['POST'])
def login_student():
    credentials = request.json
    conn = get_db_connection()
    try:
        query = '''
        SELECT s.student_ID, s.student_name, s.program_ID, u.user_ID
        FROM tbl_students s
        JOIN tbl_user u ON s.student_ID = u.student_ID
        WHERE s.student_username = ? AND s.student_password = ?
        '''
        student = conn.execute(query, (credentials['username'], credentials['password'])).fetchone()
        if student:
            return jsonify({
                "success": True,
                "user_ID": student["user_ID"],
                "id": student["student_ID"],
                "name": student["student_name"],
                "program_ID": student["program_ID"],
                "role": "student"
            }), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    finally:
        conn.close()

# Staff authentication (passing staff information)
@app.route('/login/staff', methods=['POST'])
def login_staff():
    credentials = request.json
    conn = get_db_connection()
    try:
        query = '''
        SELECT st.staff_ID, st.staff_name, st.program_ID, u.user_ID
        FROM tbl_staff st
        JOIN tbl_user u ON st.staff_ID = u.staff_ID
        WHERE st.staff_username = ? AND st.staff_password = ?
        '''
        staff = conn.execute(query, (credentials['username'], credentials['password'])).fetchone()
        if staff:
            return jsonify({
                "success": True,
                "user_ID": staff["user_ID"],
                "id": staff["staff_ID"],
                "name": staff["staff_name"],
                "program_ID": staff["program_ID"],
                "role": "staff"
            }), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    finally:
        conn.close()

# Get module's channels
@app.route('/modules/<int:module_ID>/channels', methods=['GET'])
def get_channels_for_module(module_ID):
    user_id = request.args.get('user_id')
    user_role = request.args.get('user_role')
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_role == 'staff':
        # Staff see all channels in module
        channels = cursor.execute('SELECT * FROM tbl_channels WHERE module_ID = ?', (module_ID,)).fetchall()
    else:
        # Students see channels based on type and group membership
        channels = cursor.execute('''
            SELECT c.* FROM tbl_channels c
            LEFT JOIN tbl_group_members gm ON gm.group_ID = c.group_ID
            WHERE c.module_ID = ? AND (
                c.channel_type IN ('task-info', 'both', 'private') AND (c.group_ID IS NULL OR gm.student_ID = ?)
                OR c.channel_type = 'private' AND gm.student_ID = ?
            )
        ''', (module_ID, user_id, user_id)).fetchall()

    conn.close()
    return jsonify([dict(row) for row in channels])

# Use student details to check if student exists
@app.route('/students/<int:student_ID>/info', methods=['GET'])
def get_student_info(student_ID):
    print(f"Fetching info for student ID: {student_ID}")
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM tbl_students WHERE student_ID = ?', (student_ID,)).fetchone()
    conn.close()
    if student:
        print(f"Student found: {student['student_username']}")
        return jsonify({"username": student["student_username"]}), 200
    else:
        print("Student not found")
        return jsonify({"error": "Student not found"}), 404

# Use staff details to check if staff exists
@app.route('/staff/<int:staff_id>/info', methods=['GET'])
def get_staff_info(staff_id):
    conn = get_db_connection()
    staff = conn.execute('SELECT * FROM tbl_staff WHERE staff_ID = ?', (staff_id,)).fetchone()
    conn.close()
    if staff:
        return jsonify({"username": staff["staff_username"]}), 200
    else:
        return jsonify({"error": "Staff not found"}), 404

###############################################################################################
# Socket Setup
###############################################################################################
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Message handler for channels
@socketio.on('send_message')
def handle_message(data):
    print(f"Received message: {data}")
    conn = get_db_connection()
    try:
        # Insert the message into the database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tbl_messages (message_content, message_timestamp, channel_ID, student_ID, staff_ID)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['content'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['channel'], data.get('student_ID'), data.get('staff_ID')))
        conn.commit()
        message_id = cursor.lastrowid
        data['message_ID'] = message_id

        # Determine whether to call user a student or staff based on username
        if data.get('student_ID'):
            user = conn.execute('SELECT student_username FROM tbl_students WHERE student_ID = ?', (data['student_ID'],)).fetchone()
            if user:
                data['username'] = "Student " + user['student_username']
        elif data.get('staff_ID'):
            user = conn.execute('SELECT staff_username FROM tbl_staff WHERE staff_ID = ?', (data['staff_ID'],)).fetchone()
            if user:
                data['username'] = "Staff " + user['staff_username']

        emit('receive_message', data, broadcast=True)
    except Exception as e:
        print(f"Failed to insert message: {str(e)}")
    finally:
        conn.close()

# Get information for users using their staff/student ID
def fetch_user_info(user_id, is_staff):
    if not user_id:
        return "Unknown"  # Return 'Unknown' if user_id is None or undefined
    conn = get_db_connection()
    try:
        if is_staff:
            user = conn.execute('SELECT * FROM tbl_staff WHERE staff_ID = ?', (user_id,)).fetchone()
        else:
            user = conn.execute('SELECT * FROM tbl_students WHERE student_ID = ?', (user_id,)).fetchone()
        if user:
            return user['staff_username'] if is_staff else user['student_username']
    finally:
        conn.close()
    return "Unknown"

###############################################################################################
# Grouping Algorithm Setup
###############################################################################################
# Dictionary for each module's queue
module_queues = {}

# Weights for score factors
weights = {
    'w1': 1,
    'w2': 0.5,
    'w3': 2,
    'w4': 1,
}

# Check if student is in existing group before allowing them into queue
def is_student_in_group_for_module(student_ID, module_ID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.module_ID FROM tbl_group_members gm
        JOIN tbl_groups g ON gm.group_ID = g.group_ID
        WHERE gm.student_ID = ? AND g.module_ID = ?
    ''', (student_ID, module_ID))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Checks if student is in group to send logs, if student is allowed in queue a calculation is made and queue is entered
@socketio.on('join_group_queue')
def handle_join_group_queue(data):
    try:
        student_ID = data.get('student_ID')
        module_ID = data.get('module_ID')

        if not student_ID or not module_ID:
            print("Missing student_ID or module_ID in data:", data)
            emit('error', {'message': 'Missing student_ID or module_ID'})
            return

        with lock:
            print(f"Student {student_ID} is attempting to join the queue for module {module_ID}")

            if is_student_in_group_for_module(student_ID, module_ID):
                print(f"Student {student_ID} is already in a group for module {module_ID}.")
                emit('error', {'message': 'Student is already in a group for this module'})
                return

            if module_ID not in module_queues:
                module_queues[module_ID] = []

            if any(student['student_ID'] == student_ID for student in module_queues[module_ID]):
                print(f"Student {student_ID} is already in the queue for module {module_ID}")
                emit('error', {'message': 'Student is already in the queue for this module'})
                return

            score = calculate_student_score(student_ID, module_ID, weights)
            module_queues[module_ID].append({'student_ID': student_ID, 'score': score, 'timestamp': datetime.now()})
            print(f"Student {student_ID} with score {score} added to queue for module {module_ID}")
            print(f"Current queue for module {module_ID}: {module_queues[module_ID]}")

        process_groups_if_ready(module_ID)

    except Exception as e:
        print(f"Error in handle_join_group_queue: {e}")
        emit('error', {'message': str(e)})

# Exit queue for groups
@socketio.on('leave_group_queue')
def handle_leave_group_queue(data):
    student_ID = data.get('student_ID')
    module_ID = data.get('module_ID')
    
    with lock:
        if module_ID in module_queues:
            module_queues[module_ID] = [student for student in module_queues[module_ID] if student['student_ID'] != student_ID]
            
            formatted_queue = []
            for student in module_queues[module_ID]:
                student_copy = student.copy()
                student_copy['timestamp'] = student['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                formatted_queue.append(student_copy)
            
            print(f"Student {student_ID} has been removed from the queue for module {module_ID}")
            print(f"Updated queue for module {module_ID}: {formatted_queue}")
            
            emit('queue_update', {'module_ID': module_ID, 'queue': formatted_queue})

# Check groups every X seconds to see if a group can be formed and send message
def periodically_check_groups():
    for module_ID in module_queues:
        try:
            process_groups_if_ready(module_ID)
        except Exception as e:
            print(f"Error processing groups for module {module_ID}: {e}")

    # Schedule the next check in X seconds
    Timer(30.0, periodically_check_groups).start()

# Add scores of students in queue up and checks if any combination's total score fits within range for balanced group formation
def process_groups_if_ready(module_ID):
    with lock:
        queue = module_queues.get(module_ID, [])
        current_time = datetime.now()

        score_ranges = {
            3: (700, 900),
            4: (900, 1300),
            5: (1300, 1600)
        }

        timing_thresholds = {
            3: timedelta(minutes=30),
            4: timedelta(seconds=20),
            5: timedelta(seconds=0)
        }

        formed_groups = False
        for size in [5, 4, 3]:
            if formed_groups:
                break

            if len(queue) < size:
                continue

            target_score_range = score_ranges[size]
            combinations_list = list(combinations(queue, size))
            for group in combinations_list:
                group_time = min(student['timestamp'] for student in group)
                time_elapsed = current_time - group_time
                total_score = sum(student['score'] for student in group)

                if time_elapsed >= timing_thresholds[size] and target_score_range[0] <= total_score <= target_score_range[1]:
                    for student in group:
                        queue.remove(student)
                    finalize_group(module_ID, group)
                    print(f"Group of {size} formed with scores in range {target_score_range}. Announcing group formation.")
                    formed_groups = True
                    break

            if formed_groups:
                break

        if not formed_groups and len(queue) >= 3:
            print(f"Continued waiting to form a group in module {module_ID}")

        module_queues[module_ID] = queue

# Start checks
periodically_check_groups()

###############################################################################################
## Direct Messaging
###############################################################################################

# Direct message sending
@app.route('/send_private_message', methods=['POST'])
def send_private_message():
    try:
        sender_user_id = request.form.get('sender_user_id')
        receiver_user_id = request.form.get('receiver_user_id')
        message_content = request.form.get('content')
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_url = url_for('uploaded_file', filename=filename, _external=True)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                message_content = f"file:image|{file_url}|{filename}"
            else:
                message_content = f"file:other|{file_url}|{filename}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO tbl_private_messages 
            (sender_ID, receiver_ID, message_content, message_timestamp) 
            VALUES (?, ?, ?, ?)
            ''',
            (sender_user_id, receiver_user_id, message_content, current_timestamp)
        )
        conn.commit()
        message_id = cursor.lastrowid

        response_data = {
            "message_ID": message_id,
            "sender_user_id": sender_user_id,
            "receiver_user_id": receiver_user_id,
            "message_content": message_content,
            "message_timestamp": current_timestamp,
            "success": True,
            "message": "Message sent successfully"
        }

        socketio.emit('receive_private_message', response_data, room=str(sender_user_id))
        socketio.emit('receive_private_message', response_data, room=str(receiver_user_id))

        return jsonify(response_data), 201
    except Exception as e:
        print(f"Error sending private message: {e}")
        conn.rollback()
        return jsonify({"error": str(e), "success": False}), 500
    finally:
        conn.close()
        
# Separate rooms for each user to join and listen to sockets for private messages
class DirectMessageNamespace(Namespace):
    def on_connect(self):
        user_id = request.args.get('user_ID')
        if user_id:
            join_room(user_id)
            print(f'User {user_id} connected and joined room {user_id}')

    def on_disconnect(self):
        user_id = request.args.get('user_ID')
        if user_id:
            leave_room(user_id)
            print(f'User {user_id} disconnected and left room {user_id}')

    def on_send_private_message(self, data):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COALESCE(s.student_name, st.staff_name) as sender_name
                FROM tbl_user u
                LEFT JOIN tbl_students s ON u.student_ID = s.student_ID
                LEFT JOIN tbl_staff st ON u.staff_ID = st.staff_ID
                WHERE u.user_ID = ?
            ''', (data['sender_ID'],))
            sender = cursor.fetchone()

            if sender:
                data['sender_name'] = sender['sender_name']

            emit('receive_private_message', data, room=str(data['receiver_ID']))
            emit('receive_private_message', data, room=str(data['sender_ID']))

            print(f'Message sent from user {data["sender_ID"]} to user {data["receiver_ID"]}')
        except Exception as e:
            print(f"Error in on_send_private_message: {str(e)}")

        finally:
            if conn:
                conn.close()

socketio.on_namespace(DirectMessageNamespace('/direct'))

# Gets user's private messages
@app.route('/private_messages', methods=['GET'])
def get_private_messages():
    user_id = request.args.get('user_id')
    target_user_id = request.args.get('target_user_id')
    conn = get_db_connection()
    try:
        query = '''
        SELECT pm.message_ID, pm.message_content, pm.message_timestamp, pm.message_read,
               COALESCE(s.student_name, st.staff_name) as sender_name
        FROM tbl_private_messages pm
        JOIN tbl_user u ON pm.sender_ID = u.user_ID
        LEFT JOIN tbl_students s ON u.student_ID = s.student_ID
        LEFT JOIN tbl_staff st ON u.staff_ID = st.staff_ID
        WHERE 
        ((pm.sender_ID = ? AND pm.receiver_ID = ?) OR 
        (pm.receiver_ID = ? AND pm.sender_ID = ?))
        ORDER BY pm.message_timestamp ASC
        '''
        params = (user_id, target_user_id, user_id, target_user_id)
        messages = conn.execute(query, params).fetchall()
        messages_list = [dict(message) for message in messages]
        return jsonify(messages_list), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

# Gets users info
@app.route('/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    try:
        query = '''
        SELECT u.user_ID as user_ID, COALESCE(s.student_name, st.staff_name) as name, 
               CASE WHEN s.student_ID IS NOT NULL THEN 'student' ELSE 'staff' END as role
        FROM tbl_user u
        LEFT JOIN tbl_students s ON u.student_ID = s.student_ID
        LEFT JOIN tbl_staff st ON u.staff_ID = st.staff_ID
        '''
        users = conn.execute(query).fetchall()
        users_list = [dict(user) for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        print(f"An error occurred: {e}") 
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

###############################################################################################
# Setup for file uploads
###############################################################################################
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads')
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} # Optional file restriction

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check upload folder exists, create if not
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS # Optional file restriction
    return True

# Uploads each file and generates web-accessible URL
@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_url = request.host_url.rstrip('/') + url_for('uploaded_file', filename=filename)
        
        return jsonify({"success": True, "filepath": file_url}), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400

# Returns file
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    socketio.run(app, debug=True)