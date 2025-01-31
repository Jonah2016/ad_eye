import os

from app import create_app

app = create_app(os.getenv("CONFIG_MODE"))

if __name__ == "__main__":
    app.run(debug=True)
