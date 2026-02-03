from app import create_app, db
from app.services.importer import import_data
import os

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()
    print("Database tables created.")
    
    data_file = 'data-sample-small.json'
    if os.path.exists(data_file):
        print(f"Importing data from {data_file}...")
        success = import_data(data_file)
        if success:
            print("Import successful!")
        else:
            print("Import failed.")
    else:
        print(f"File {data_file} not found.")
