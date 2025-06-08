from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router

# Create a FastAPI application instance
app = FastAPI()

# Add session middleware to handle user sessions securely
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Mount the static files directory at '/static' URL path to serve static content like CSS, images, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the main application routes from the router
app.include_router(router)
