def test_home():
    """Test the home page loads successfully and contains expected content."""

    from starlette.testclient import TestClient  # Test client for simulating HTTP requests
    from app import app                          # The FastAPI (or Starlette) app instance

    client = TestClient(app)                     # Create a test client for the app

    response = client.get("/")                    # Send a GET request to the home page

    assert response.status_code == 200            # Check if the response status code is 200 OK
    assert "TaskPlant" in response.text           # Verify the response contains the expected text
