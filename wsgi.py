import os

from app import create_app

app = create_app(os.getenv("CONFIG_MODE"))


# ----------------------------------------------- #

# Hello World!
@app.route('/')
def hello():
    return "Deep Eye!"


# ----------------------------------------------- #

if __name__ == "__main__":
    app.run(debug=True)
