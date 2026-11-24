from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Ekstensi dibuat terpisah agar mudah dipakai oleh application factory dan test.
db = SQLAlchemy()
migrate = Migrate()
