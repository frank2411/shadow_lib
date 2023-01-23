from dotenv import load_dotenv

load_dotenv()

wsgi_app = "wsgi:app"
workers = 1
loglevel = "debug"
accesslog = "-"
errorlog = "-"
bind = "0.0.0.0:8090"
