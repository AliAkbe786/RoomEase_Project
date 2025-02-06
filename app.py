from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from functools import wraps
from openai import OpenAI
import traceback

# Define the conversion functions first
def convert_sleep_schedule(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    schedules = {
        '1': 'Very late (after midnight)',
        '2': 'Late (11 PM - 12 AM)',
        '3': 'Moderate (10 PM - 11 PM)',
        '4': 'Early (9 PM - 10 PM)',
        '5': 'Very early (before 9 PM)'
    }
    return schedules.get(str(value).strip(), 'Not specified')

def convert_cleanliness(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    levels = {
        '1': 'Very messy',
        '2': 'Somewhat messy',
        '3': 'Neutral',
        '4': 'Somewhat clean',
        '5': 'Very clean'
    }
    return levels.get(str(value).strip(), 'Not specified')

def convert_study_environment(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    environments = {
        '1': 'Very noisy',
        '2': 'Somewhat noisy',
        '3': 'Neutral',
        '4': 'Quiet',
        '5': 'Very quiet'
    }
    return environments.get(str(value).strip(), 'Not specified')

def convert_smoking_preference(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    preferences = {
        '1': 'No preference',
        '2': 'Prefer non-smoker but okay with smoker',
        '3': 'Neutral',
        '4': 'Prefer non-smoker',
        '5': 'Absolutely no smokers'
    }
    return preferences.get(str(value).strip(), 'Not specified')

def convert_social_level(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    levels = {
        '1': 'Very introverted',
        '2': 'Somewhat introverted',
        '3': 'Neutral',
        '4': 'Somewhat extroverted',
        '5': 'Very extroverted'
    }
    return levels.get(str(value).strip(), 'Not specified')

def convert_conflict_tolerance(value):
    if not value or not str(value).strip():  # Handle empty/None values
        return 'Not specified'
    levels = {
        '1': 'Avoid conflict entirely',
        '2': 'Low tolerance for conflict',
        '3': 'Neutral',
        '4': 'Can handle some conflict',
        '5': 'Open to resolving conflicts'
    }
    return levels.get(str(value).strip(), 'Not specified')

# Then initialize Flask and register the filters
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Add template filters
app.jinja_env.filters['convert_sleep_schedule'] = convert_sleep_schedule
app.jinja_env.filters['convert_cleanliness'] = convert_cleanliness
app.jinja_env.filters['convert_study_environment'] = convert_study_environment
app.jinja_env.filters['convert_smoking_preference'] = convert_smoking_preference
app.jinja_env.filters['convert_social_level'] = convert_social_level
app.jinja_env.filters['convert_conflict_tolerance'] = convert_conflict_tolerance

# Set up Google Sheets authentication
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet
sheet = client.open_by_key('1BzfvLFMHfbQb5x_YOFf63G4jPt02YLlvvAUQMq1M0xA').worksheet('Table1')

# Initialize OpenAI client with your API key
client = OpenAI(api_key='sk-k343y-_bcqi5gCfODKACE5GAppoaGaFEWOhF8fwC70T3BlbkFJJY8W17JYH-lTG5sK3Xuf5ZNpX57QtV4sW32ImM-JMA')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matric_number = request.form.get('matric_number')
        ic_number = request.form.get('ic_number')
        
        try:
            # Find the user in the spreadsheet
            cell = sheet.find(matric_number)
            if cell is None:
                return render_template('login.html', error="Invalid credentials")
            
            row = sheet.row_values(cell.row)
            stored_ic = row[0]  # ic_number is in first column
            
            if stored_ic == ic_number:
                # Get question_status (column 16)
                question_status = row[15] if len(row) > 15 else 'FALSE'  # Adjusted index
                print(f"Question status from database: {question_status}")  # Debug print
                
                # Store user info in session
                session['user'] = {
                    'matric_number': matric_number,
                    'name': row[2],  # name is in third column
                    'profile': {
                        'age': row[3] if len(row) > 3 else '',
                        'semester': row[4] if len(row) > 4 else '',
                        'sleep_schedule': row[6] if len(row) > 6 else '',
                        'cleanliness': row[7] if len(row) > 7 else '',
                        'study_environment': row[8] if len(row) > 8 else '',
                        'smoking_preference': row[9] if len(row) > 9 else '',
                        'hobbies': row[10] if len(row) > 10 else '',
                        'extroversion_level': row[11] if len(row) > 11 else '',
                        'conflict_tolerance': row[12] if len(row) > 12 else '',
                        'roommate_cleanliness': row[13] if len(row) > 13 else '',
                        'gender': row[14] if len(row) > 14 else '',
                        'question_status': question_status
                    }
                }
                
                # Check if user has roommate
                roommate_name = row[17] if len(row) > 17 else None
                
                print(f"Roommate name: {roommate_name}")  # Debug print
                print(f"Question status: {question_status}")  # Debug print
                
                if roommate_name:
                    return redirect(url_for('profile'))
                elif question_status.strip().upper() == 'TRUE':  # Added strip()
                    return redirect(url_for('find_matches'))
                else:
                    return redirect(url_for('questions'))
            else:
                return render_template('login.html', error="Invalid credentials")
                
        except Exception as e:
            print(f"Login error: {e}")
            return render_template('login.html', error="An error occurred during login")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome {session['user']['name']}!"  # Replace this with your dashboard template

@app.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    # First check if questions are already answered
    user_cell = sheet.find(session['user']['matric_number'])
    user_row = sheet.row_values(user_cell.row)
    current_status = user_row[15] if len(user_row) > 15 else 'FALSE'  # Adjusted index
    
    if current_status.strip().upper() == 'TRUE':
        return redirect(url_for('find_matches'))

    if request.method == 'POST':
        try:
            # Get form data with validation
            data = {
                'sleep_schedule': int(request.form.get('sleep_schedule')),
                'cleanliness': int(request.form.get('cleanliness')),
                'study_environment': int(request.form.get('study_environment')),
                'smoking_preference': int(request.form.get('smoking_preference')),
                'hobbies': request.form.getlist('hobbies[]'),
                'extroversion_level': int(request.form.get('extroversion_level')),
                'conflict_tolerance': int(request.form.get('conflict_tolerance')),
                'roommate_cleanliness': int(request.form.get('roommate_cleanliness'))
            }

            # Find the user's row in the sheet
            cell = sheet.find(session['user']['matric_number'])
            
            # Update the sheet with new data
            sheet.update_cell(cell.row, 7, data['sleep_schedule'])
            sheet.update_cell(cell.row, 8, data['cleanliness'])
            sheet.update_cell(cell.row, 9, data['study_environment'])
            sheet.update_cell(cell.row, 10, data['smoking_preference'])
            sheet.update_cell(cell.row, 11, ','.join(data['hobbies']))
            sheet.update_cell(cell.row, 12, data['extroversion_level'])
            sheet.update_cell(cell.row, 13, data['conflict_tolerance'])
            sheet.update_cell(cell.row, 14, data['roommate_cleanliness'])
            sheet.update_cell(cell.row, 16, 'TRUE')  # Adjusted index for question_status

            # Update session data
            session['user']['profile'].update(data)
            session['user']['profile']['question_status'] = 'TRUE'
            
            print(f"Updated question status to TRUE for user {session['user']['matric_number']}")  # Debug print
            
            return redirect(url_for('find_matches'))
            
        except Exception as e:
            print(f"Error updating profile: {e}")
            import traceback
            print(traceback.format_exc())
            return render_template('questions.html', error="Please fill in all required fields")

    return render_template('questions.html')

def calculate_compatibility(student_a, student_b):
    """
    Calculates compatibility score between two students.
    Returns a score between 0 and 1.
    """
    try:
        # Define weights for each factor
        weights = {
            'sleep_schedule': 0.15,
            'cleanliness': 0.2,
            'study_environment': 0.15,
            'smoking_preference': 0.1,
            'hobbies': 0.1,
            'extroversion_level': 0.1,
            'conflict_tolerance': 0.1,
            'roommate_cleanliness': 0.1,
        }

        total_score = 0

        # Calculate numerical compatibility
        numerical_columns = [
            'sleep_schedule', 'cleanliness', 'study_environment',
            'smoking_preference', 'extroversion_level', 'conflict_tolerance',
            'roommate_cleanliness'
        ]
        
        for column in numerical_columns:
            # Convert values to integers and handle potential None/empty values
            val_a = int(student_a.get(column, 0) or 0)
            val_b = int(student_b.get(column, 0) or 0)
            
            if val_a == 0 or val_b == 0:  # Skip if either value is missing
                continue
                
            # Calculate normalized difference
            score = 1 - abs(val_a - val_b) / 4
            total_score += weights[column] * score

        # Calculate hobbies compatibility
        hobbies_a = set(str(student_a.get('hobbies', '')).split(',')) if student_a.get('hobbies') else set()
        hobbies_b = set(str(student_b.get('hobbies', '')).split(',')) if student_b.get('hobbies') else set()
        
        # Remove empty strings from sets
        hobbies_a = {h.strip() for h in hobbies_a if h.strip()}
        hobbies_b = {h.strip() for h in hobbies_b if h.strip()}
        
        if hobbies_a and hobbies_b:  # Only calculate if both have hobbies
            intersection = hobbies_a & hobbies_b
            union = hobbies_a | hobbies_b
            if union:  # Avoid division by zero
                hobbies_similarity = len(intersection) / len(union)
                total_score += weights['hobbies'] * hobbies_similarity

        print(f"Compatibility score between {student_a['matric_number']} and {student_b['matric_number']}: {total_score}")
        return round(total_score, 3)

    except Exception as e:
        print(f"Error calculating compatibility: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return 0

@app.route('/find_matches')
@login_required
def find_matches():
    try:
        all_data = sheet.get_all_records()
        matches = []
        
        # Get current user's data
        current_user = None
        for student in all_data:
            if student['matric_number'] == session['user']['matric_number']:
                current_user = student
                break
        
        if not current_user:
            return "Error: User data not found"

        # Debug current user's status
        print("Current User Data:")
        print(f"Name: {current_user['name']}")
        print(f"Gender: {current_user.get('gender', '').upper()}")  # Add .upper()
        print(f"Question Status: {current_user.get('question_status')}")

        # First verify current user has completed questionnaire
        if current_user.get('question_status', '').upper() != 'TRUE':
            return render_template('matches.html', 
                                matches=[], 
                                show_questionnaire_prompt=True)

        current_user_gender = current_user.get('gender', '').strip().upper()
        if not current_user_gender:
            print("Current user has no gender specified")
            return render_template('matches.html', 
                                matches=[], 
                                no_matches_reason=["Please update your gender information"])

        for student in all_data:
            # Skip self
            if student['matric_number'] == current_user['matric_number']:
                continue

            # Skip if they haven't completed the questionnaire
            if student.get('question_status', '').upper() != 'TRUE':
                print(f"Skipping {student['name']} - Incomplete questionnaire")
                continue

            # Skip if either has a roommate
            if student.get('roommate_name') or current_user.get('roommate_name'):
                print(f"Skipping {student['name']} - Has roommate")
                continue

            # Check gender match
            student_gender = student.get('gender', '').strip().upper()
            if student_gender != current_user_gender:
                print(f"Skipping {student['name']} - Gender mismatch ({student_gender} != {current_user_gender})")
                continue

            # Calculate compatibility
            compatibility = calculate_compatibility(current_user, student)
            
            # Create profile for summary generation
            student_profile = {
                'name': student['name'],
                'matric_number': student['matric_number'],
                'age': student['age'],
                'semester': student['semester'],
                'sleep_schedule': student['sleep_schedule'],
                'cleanliness': student['cleanliness'],
                'study_environment': student['study_environment'],
                'smoking_preference': student['smoking_preference'],
                'hobbies': student['hobbies'],
                'extroversion_level': student['extroversion_level']
            }
            
            # Generate AI summary
            preference_summary = generate_preference_summary(student_profile)
            
            # Add to matches
            matches.append({
                'name': student['name'],
                'matric_number': student['matric_number'],
                'age': student['age'],
                'semester': student['semester'],
                'compatibility': round(compatibility * 100, 1),
                'sleep_schedule': convert_sleep_schedule(student['sleep_schedule']),
                'cleanliness': convert_cleanliness(student['cleanliness']),
                'study_environment': convert_study_environment(student['study_environment']),
                'smoking_preference': convert_smoking_preference(student['smoking_preference']),
                'hobbies': student['hobbies'],
                'extroversion_level': convert_social_level(student['extroversion_level']),
                'preference_summary': preference_summary  # Add the AI summary
            })

        # Sort matches by compatibility
        matches.sort(key=lambda x: x['compatibility'], reverse=True)
        
        print(f"\nFinal Matches Found: {len(matches)}")

        if not matches:
            return render_template('matches.html', 
                                matches=[], 
                                show_questionnaire_prompt=False,
                                no_matches_reason=["No available roommates of your gender found"])

        return render_template('matches.html', 
                             matches=matches,
                             show_questionnaire_prompt=False)

    except Exception as e:
        print(f"Error in find_matches: {e}")
        import traceback
        print(traceback.format_exc())
        return "An error occurred while finding matches", 500

def generate_preference_summary(profile):
    """Generate a natural language summary of roommate preferences"""
    try:
        # Convert numeric preferences to text
        preferences = {
            'sleep_schedule': convert_sleep_schedule(profile['sleep_schedule']),
            'cleanliness': convert_cleanliness(profile['cleanliness']),
            'study_environment': convert_study_environment(profile['study_environment']),
            'smoking_preference': convert_smoking_preference(profile['smoking_preference']),
            'social_type': convert_social_level(profile['extroversion_level']),
            'hobbies': profile['hobbies']
        }
        
        # Create prompt for OpenAI
        prompt = f"""Write a friendly, natural paragraph summarizing these roommate preferences:
        Sleep Schedule: {preferences['sleep_schedule']}
        Cleanliness: {preferences['cleanliness']}
        Study Environment: {preferences['study_environment']}
        Smoking Preference: {preferences['smoking_preference']}
        Social Type: {preferences['social_type']}
        Hobbies: {preferences['hobbies']}
        
        Make it sound conversational and highlight key compatibility factors. Keep it concise (2-3 sentences).
        """
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes natural, friendly summaries of roommate preferences."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating preference summary: {e}")
        return None

@app.route('/send_request', methods=['POST'])
@login_required
def send_request():
    try:
        # Handle both JSON and form data
        if request.is_json:
            target_matric = request.json.get('matric_number')
        else:
            target_matric = request.form.get('matric_number')

        if not target_matric:
            return jsonify({'error': 'No matric number provided'}), 400

        # Get current user's row
        current_user_cell = sheet.find(session['user']['matric_number'])
        current_user_row = sheet.row_values(current_user_cell.row)
        
        # Get target student's row
        target_cell = sheet.find(target_matric)
        if not target_cell:
            return jsonify({'error': 'Student not found'}), 404
            
        target_row = sheet.row_values(target_cell.row)

        # Check if either student already has a roommate (column 18 - roommate_name)
        if (len(current_user_row) > 17 and current_user_row[17]) or (len(target_row) > 17 and target_row[17]):
            return jsonify({'error': 'One of the students already has a roommate'}), 400

        # Get current requests_received for target (column 17)
        current_requests = target_row[16] if len(target_row) > 16 else ''
        current_requests_list = [r.strip() for r in current_requests.split('\n') if r.strip()]
        
        # Format current user's info
        current_user_matric = session['user']['matric_number']
        
        # Check if request already exists
        if current_user_matric in current_requests_list:
            return jsonify({'error': 'Request already sent to this student'}), 400
            
        # Add new request to requests_received
        current_requests_list.append(current_user_matric)
        new_requests = '\n'.join(current_requests_list)
        
        # Update the target's requests_received (column 17)
        sheet.update_cell(target_cell.row, 17, new_requests)

        print(f"Request sent successfully from {current_user_matric} to {target_matric}")
        return jsonify({'message': 'Request sent successfully'}), 200

    except Exception as e:
        print(f"Error sending request: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to send request'}), 500

@app.route('/get_requests')
@login_required
def get_requests():
    try:
        print("\n=== Starting Request Processing ===")
        current_user_matric = session['user']['matric_number']
        
        user_cell = sheet.find(current_user_matric)
        user_row = sheet.row_values(user_cell.row)
        requests_received = user_row[16] if len(user_row) > 16 else ''
        
        # Format current user data for compatibility calculation
        current_user = {
            'matric_number': current_user_matric,
            'sleep_schedule': int(float(user_row[6])) if user_row[6] and user_row[6].strip() != '' else 0,
            'cleanliness': int(float(user_row[7])) if user_row[7] and user_row[7].strip() != '' else 0,
            'study_environment': int(float(user_row[8])) if user_row[8] and user_row[8].strip() != '' else 0,
            'smoking_preference': int(float(user_row[9])) if user_row[9] and user_row[9].strip() != '' else 0,
            'hobbies': user_row[10] if user_row[10] and user_row[10].strip() != '' else '',
            'extroversion_level': int(float(user_row[11])) if user_row[11] and user_row[11].strip() != '' else 0,
            'conflict_tolerance': int(float(user_row[12])) if user_row[12] and user_row[12].strip() != '' else 0,
            'roommate_cleanliness': int(float(user_row[13])) if user_row[13] and user_row[13].strip() != '' else 0
        }

        if not requests_received:
            return jsonify([])
        
        all_data = sheet.get_all_records()
        requests = []
        
        for requester_matric in requests_received.strip().split('\n'):
            if not requester_matric.strip():
                continue
                
            try:
                # Find requester data
                requester_data = next(
                    (row for row in all_data if str(row['matric_number']).strip() == requester_matric.strip()),
                    None
                )
                
                if not requester_data:
                    continue

                # Format requester data for compatibility calculation
                student_data = {
                    'matric_number': str(requester_data['matric_number']),
                    'name': str(requester_data['name']),
                    'age': str(requester_data['age']),
                    'semester': str(requester_data['semester']),
                    'sleep_schedule': int(float(requester_data['sleep_schedule'])) if requester_data['sleep_schedule'] and str(requester_data['sleep_schedule']).strip() != '' else 0,
                    'cleanliness': int(float(requester_data['cleanliness'])) if requester_data['cleanliness'] and str(requester_data['cleanliness']).strip() != '' else 0,
                    'study_environment': int(float(requester_data['study_environment'])) if requester_data['study_environment'] and str(requester_data['study_environment']).strip() != '' else 0,
                    'smoking_preference': int(float(requester_data['smoking_preference'])) if requester_data['smoking_preference'] and str(requester_data['smoking_preference']).strip() != '' else 0,
                    'hobbies': str(requester_data['hobbies']) if requester_data['hobbies'] else '',
                    'extroversion_level': int(float(requester_data['extroversion_level'])) if requester_data['extroversion_level'] and str(requester_data['extroversion_level']).strip() != '' else 0,
                    'conflict_tolerance': int(float(requester_data['conflict_tolerance'])) if requester_data['conflict_tolerance'] and str(requester_data['conflict_tolerance']).strip() != '' else 0,
                    'roommate_cleanliness': int(float(requester_data['roommate_cleanliness'])) if requester_data['roommate_cleanliness'] and str(requester_data['roommate_cleanliness']).strip() != '' else 0
                }

                # Calculate compatibility
                compatibility = calculate_compatibility(student_data, current_user)
                compatibility_percentage = round(compatibility * 100, 1)
                
                print(f"Calculated compatibility: {compatibility_percentage}%")  # Debug print
                
                request_data = {
                    'name': student_data['name'],
                    'matric_number': student_data['matric_number'],
                    'age': student_data['age'],
                    'semester': student_data['semester'],
                    'preference_summary': generate_preference_summary(student_data),
                    'compatibility': compatibility_percentage
                }
                requests.append(request_data)
                
            except Exception as e:
                print(f"\nError processing requester {requester_matric}:")
                print(f"Error message: {str(e)}")
                import traceback
                print(traceback.format_exc())
                continue
        
        # Sort requests by compatibility score
        requests.sort(key=lambda x: x['compatibility'], reverse=True)
        return jsonify(requests)
        
    except Exception as e:
        print(f"Error in get_requests: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Failed to get requests'}), 500

@app.route('/requests')
@login_required
def view_requests():
    try:
        # Get current user's requests received
        user_cell = sheet.find(session['user']['matric_number'])
        user_row = sheet.row_values(user_cell.row)
        requests_received = user_row[16] if len(user_row) > 16 and user_row[16] else ''
        
        if not requests_received:
            return render_template('requests.html', requests=[])
        
        # Get requesters' profiles
        requests_list = []
        for request_matric in requests_received.strip().split('\n'):
            if request_matric:
                requester_cell = sheet.find(request_matric)
                if requester_cell:
                    requester_row = sheet.row_values(requester_cell.row)
                    requests_list.append({
                        'matric_number': request_matric,
                        'name': requester_row[2],
                        'age': requester_row[3],
                        'semester': requester_row[4],
                        'phone_number': requester_row[5],
                        'sleep_schedule': convert_sleep_schedule(requester_row[6]),
                        'cleanliness': convert_cleanliness(requester_row[7]),
                        'study_environment': convert_study_environment(requester_row[8]),
                        'smoking_preference': convert_smoking_preference(requester_row[9]),
                        'hobbies': requester_row[10],
                        'extroversion_level': convert_social_level(requester_row[11]),
                        'conflict_tolerance': convert_conflict_tolerance(requester_row[12]),
                        'roommate_cleanliness': convert_cleanliness(requester_row[13]),
                        'gender': requester_row[14]
                    })
        
        return render_template('requests.html', requests=requests_list)
        
    except Exception as e:
        print(f"Error viewing requests: {e}")
        return "An error occurred while viewing requests"

@app.route('/handle_request', methods=['POST'])
@login_required
def handle_request():
    try:
        data = request.get_json()
        roommate_matric = data.get('requested_matric')
        action = data.get('action')
        user_matric = session['user']['matric_number']

        if action == 'accept':
            # Find roommate's row by searching specifically in the matric_number column (column B, index 2)
            roommate_cell = sheet.find(roommate_matric, in_column=2)
            if not roommate_cell:
                return jsonify({'error': 'Roommate not found'}), 404
            roommate_row = sheet.row_values(roommate_cell.row)
            roommate_name = roommate_row[2].strip()  # Column C (index 2) is name

            # Find user's row by searching in the matric_number column
            user_cell = sheet.find(user_matric, in_column=2)
            if not user_cell:
                return jsonify({'error': 'User not found'}), 404
            user_row = sheet.row_values(user_cell.row)
            user_name = user_row[2].strip()  # Column C (index 2) is name

            # Format the strings exactly as required
            roommate_info = f"{roommate_name}(({roommate_matric}))"  # This goes in the user's roommate_name
            user_info = f"{user_name}(({user_matric}))"               # This goes in the roommate's roommate_name

            # Update the roommate_name column (Column R, which is column index 18)
            sheet.update_cell(user_cell.row, 18, roommate_info)        # Update user's roommate_name
            sheet.update_cell(roommate_cell.row, 18, user_info)         # Update roommate's roommate_name

            # Clear the request from received requests (column Q, index 17, for requests_received)
            requests_received = user_row[16] if len(user_row) > 16 else ''
            requests_list = [r.strip() for r in requests_received.split('\n') if r.strip()]

            # Remove the accepted request if present
            if roommate_matric in requests_list:
                requests_list.remove(roommate_matric)

            # Update the requests_received column
            updated_requests = '\n'.join(requests_list) if requests_list else ''
            sheet.update_cell(user_cell.row, 17, updated_requests)     # Update requests_received for user

            # Update session data with new roommate info
            if 'user' in session:
                session['user']['profile']['roommate_name'] = roommate_info
                session.modified = True

            return jsonify({'message': 'Request accepted successfully', 'redirect': url_for('profile')})

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({'error': error_message}), 500

@app.route('/profile')
@login_required
def profile():
    try:
        # Get current user's profile
        user_cell = sheet.find(session['user']['matric_number'])
        user_row = sheet.row_values(user_cell.row)
        
        user_profile = {
            'name': user_row[2],
            'age': user_row[3],
            'semester': user_row[4],
            'phone_number': user_row[5],
            'sleep_schedule': user_row[6],
            'cleanliness': user_row[7],
            'study_environment': user_row[8],
            'smoking_preference': user_row[9],
            'hobbies': user_row[10],
            'extroversion_level': user_row[11],
            'conflict_tolerance': user_row[12],
            'roommate_cleanliness': user_row[13],
            'gender': user_row[14]
        }
        
        # Store raw values for compatibility calculation
        user_raw_values = {
            'matric_number': session['user']['matric_number'],
            'sleep_schedule': user_row[6],
            'cleanliness': user_row[7],
            'study_environment': user_row[8],
            'smoking_preference': user_row[9],
            'hobbies': user_row[10],
            'extroversion_level': user_row[11],
            'conflict_tolerance': user_row[12],
            'roommate_cleanliness': user_row[13]
        }
        
        # Check if user has a roommate
        roommate_info = user_row[17] if len(user_row) > 17 and user_row[17] else None
        roommate_profile = None
        compatibility_score = None
        
        if roommate_info:
            try:
                # Extract matric number from roommate_info format: name((matric))
                roommate_matric = roommate_info.split('((')[1].split('))')[0]
                roommate_cell = sheet.find(roommate_matric)
                roommate_row = sheet.row_values(roommate_cell.row)
                
                roommate_profile = {
                    'name': roommate_row[2],
                    'age': roommate_row[3],
                    'semester': roommate_row[4],
                    'phone_number': roommate_row[5],
                    'sleep_schedule': roommate_row[6],
                    'cleanliness': roommate_row[7],
                    'study_environment': roommate_row[8],
                    'smoking_preference': roommate_row[9],
                    'hobbies': roommate_row[10],
                    'extroversion_level': roommate_row[11],
                    'conflict_tolerance': roommate_row[12],
                    'roommate_cleanliness': roommate_row[13],
                    'gender': roommate_row[14]
                }
                
                # Store raw values for compatibility calculation
                roommate_raw_values = {
                    'matric_number': roommate_matric,
                    'sleep_schedule': roommate_row[6],
                    'cleanliness': roommate_row[7],
                    'study_environment': roommate_row[8],
                    'smoking_preference': roommate_row[9],
                    'hobbies': roommate_row[10],
                    'extroversion_level': roommate_row[11],
                    'conflict_tolerance': roommate_row[12],
                    'roommate_cleanliness': roommate_row[13]
                }
                
                # Calculate compatibility score
                compatibility_score = calculate_compatibility(user_raw_values, roommate_raw_values)
                compatibility_score = round(compatibility_score * 100, 1)  # Convert to percentage
                
            except Exception as e:
                print(f"Error processing roommate data: {e}")
                import traceback
                print(traceback.format_exc())
        
        # Generate preference summary for user
        user_summary = generate_preference_summary(user_profile)
        
        # Generate summary for roommate if exists
        roommate_summary = None
        if roommate_profile:
            roommate_summary = generate_preference_summary(roommate_profile)
        
        print(f"User Profile: {user_profile}")
        print(f"Roommate Profile: {roommate_profile}")
        print(f"Compatibility Score: {compatibility_score}")
        
        return render_template('profile.html', 
                             user_profile=user_profile, 
                             roommate_profile=roommate_profile,
                             user_summary=user_summary,
                             roommate_summary=roommate_summary,
                             compatibility_score=compatibility_score,
                             convert_sleep_schedule=convert_sleep_schedule,
                             convert_cleanliness=convert_cleanliness,
                             convert_study_environment=convert_study_environment,
                             convert_smoking_preference=convert_smoking_preference,
                             convert_social_level=convert_social_level,
                             convert_conflict_tolerance=convert_conflict_tolerance)
                             
    except Exception as e:
        print(f"Error viewing profile: {e}")
        import traceback
        print(traceback.format_exc())
        return "An error occurred while viewing profile"

@app.route('/get_recommendations')
@login_required
def get_recommendations():
    try:
        print("\n=== Getting Recommendations ===")
        # Get current user's data
        current_user_matric = session['user']['matric_number']
        user_cell = sheet.find(current_user_matric)
        user_row = sheet.row_values(user_cell.row)
        
        # Get current user's preferences - format exactly as in recommendations
        current_user = {
            'sleep_schedule': int(float(user_row[6])) if user_row[6] and user_row[6].strip() else 0,
            'cleanliness': int(float(user_row[7])) if user_row[7] and user_row[7].strip() else 0,
            'study_environment': int(float(user_row[8])) if user_row[8] and user_row[8].strip() else 0,
            'smoking_preference': int(float(user_row[9])) if user_row[9] and user_row[9].strip() else 0,
            'hobbies': user_row[10] if user_row[10] and user_row[10].strip() else '',
            'extroversion_level': int(float(user_row[11])) if user_row[11] and user_row[11].strip() else 0,
            'conflict_tolerance': int(float(user_row[12])) if user_row[12] and user_row[12].strip() else 0,
            'roommate_cleanliness': int(float(user_row[13])) if user_row[13] and user_row[13].strip() else 0,
            'gender': user_row[14] if user_row[14] and user_row[14].strip() else ''
        }
        
        print("\nCurrent User Data:")
        print(current_user)
        
        # Get all students
        all_students = sheet.get_all_records()
        
        # Calculate compatibility for each student
        recommendations = []
        for student in all_students:
            try:
                if str(student['matric_number']).strip() == current_user_matric:
                    continue
                    
                student_data = {
                    'sleep_schedule': int(float(student['sleep_schedule'])) if student['sleep_schedule'] else 0,
                    'cleanliness': int(float(student['cleanliness'])) if student['cleanliness'] else 0,
                    'study_environment': int(float(student['study_environment'])) if student['study_environment'] else 0,
                    'smoking_preference': int(float(student['smoking_preference'])) if student['smoking_preference'] else 0,
                    'hobbies': str(student['hobbies']) if student['hobbies'] else '',
                    'extroversion_level': int(float(student['extroversion_level'])) if student['extroversion_level'] else 0,
                    'conflict_tolerance': int(float(student['conflict_tolerance'])) if student['conflict_tolerance'] else 0,
                    'roommate_cleanliness': int(float(student['roommate_cleanliness'])) if student['roommate_cleanliness'] else 0,
                    'gender': str(student['gender']) if student['gender'] else ''
                }
                
                compatibility = calculate_compatibility(student_data, current_user)
                print(f"\nCompatibility with {student['name']}: {compatibility * 100}%")
                
                # Rest of the code...
            except Exception as e:
                print(f"Error calculating compatibility for {student['name']}: {e}")
                import traceback
                print(traceback.format_exc())
                continue

        # Sort recommendations by compatibility
        recommendations.sort(key=lambda x: x['compatibility'], reverse=True)
        
        print(f"\nFinal Recommendations Found: {len(recommendations)}")

        if not recommendations:
            return render_template('recommendations.html', 
                                    recommendations=[], 
                                    no_recommendations_reason=["No recommendations found"])

        return render_template('recommendations.html', 
                             recommendations=recommendations,
                             no_recommendations_reason=[])

    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        import traceback
        print(traceback.format_exc())
        return "An error occurred while getting recommendations", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 