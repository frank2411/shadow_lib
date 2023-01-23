from dotenv import load_dotenv

load_dotenv()

wsgi_app = "wsgi:app"
workers = 5
loglevel = "info"
accesslog = "-"
errorlog = "-"
bind = "0.0.0.0:8090"
