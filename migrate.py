from main import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW()'))
        conn.commit()
    db.create_all()
    print("Migration complete — all tables up to date.")
