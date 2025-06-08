from app.database import engine
from app import models

# Create all tables in the database based on the models' metadata.
# If the tables already exist, this will update them without deleting data.
models.Base.metadata.create_all(bind=engine)

# Inform the user that the database has been successfully created or updated.
print("Database successfully created/updated.")
