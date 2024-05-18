from models import db, User, State, Patient, Disease
from sqlalchemy import or_

def login(email, password):
    try:
        user = User.query.filter(or_(User.email == email, User.username == email)).first()
        if user and user.verify_password(password):
            return user
    except Exception as e:
        print(f"Error during login: {e}")
    return None

def get_user_by_id(user_id):
    try:
        return User.query.get(user_id)
    except Exception as e:
        print(f"Error retrieving user by ID: {e}")
        return None

def report_by_state(state=None, disease=None):
    try:
        query = db.session.query(
            db.func.count(Patient.id).label('total'),
            Patient.last_state,
            Patient.state
        ).group_by(Patient.last_state, Patient.state)
        
        if state:
            query = query.filter(Patient.state == state)
        if disease:
            query = query.filter(Patient.diseases.any(Disease.id.in_(disease)))

        patients = query.all()

        return [{
            'total': patient.total,
            'data': patient.last_state,
            'state': State.query.get(patient.state).name
        } for patient in patients]

    except Exception as e:
        print(f"Error generating report: {e}")
        return []

# Example usage:
# user = login('email@example.com', 'password123')
# user = get_user_by_id(1)
# report = report_by_state(state=1, disease=[1, 2])
