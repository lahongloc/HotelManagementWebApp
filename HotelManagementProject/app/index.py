from app import app, dao
from flask import render_template


@app.route('/')
def home():
    room_types = dao.get_room_types()
    return render_template('index.html', room_types=room_types)


if __name__ == "__main__":
    app.run(debug=True)
