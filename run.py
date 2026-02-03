from app import create_app, db
from app.models import Student, Subject

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Student': Student, 'Subject': Subject}

if __name__ == '__main__':
    app.run(debug=True)
