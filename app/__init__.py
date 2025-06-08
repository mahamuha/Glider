from app.database import engine, Base
from app import models

# Create all database tables defined in models if they don't exist
Base.metadata.create_all(bind=engine)

# Inform that the database tables have been created successfully
print("Database tables created successfully.")
