from app import app, dao
from flask import render_template, request


@app.route('/')
def home():
    room_types = dao.get_room_types()
    # rt = request.args.get('')
    return render_template('index.html', room_types=room_types)


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    return data


if __name__ == "__main__":
    app.run(debug=True)
