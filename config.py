import datetime
import os

SECRET_KEY = '8705c08a-1975-4b1b-9daa-073945569331'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'files')
