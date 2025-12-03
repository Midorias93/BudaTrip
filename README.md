**BudaTrip**
=================

*Smart City Project*

Romain LABBE\
Silvain CLISSON

## Project Structure

The project is organized into two main directories:

- **backend/** - Contains all backend Python code (Flask app, routes, database models, etc.)
- **frontend/** - Contains all frontend assets (HTML templates, CSS, JavaScript)

## Setup Instructions

You should create a virtual environment to run the project.\
to do so, run the following command:
```bash
python -m venv venv .venv
# if you are on linux or macos
source .venv/bin/activate
# if you are on windows
.venv\Scripts\activate
```

To set up the project install the python packages in requirements.txt
```bash
cd backend
pip install -r requirement.txt
```

to launch the data base ( to do on the VM ubuntu )
```bash
cd backend
docker compose up -d
```
to stop the data base ( to do on the VM ubuntu )
```bash
cd backend
# you can add the -v option to remove the volumes
docker compose down 
```

## Running the Application

To run the Flask application:
```bash
cd backend
python app.py
```

How to launch the ngrok server : ( To do on the VM ubuntu )
```bash
ngrok http 8000 
```