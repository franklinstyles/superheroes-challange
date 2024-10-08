from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_all_heroes():
    try:
        heroes = Hero.query.all()
        heroes_data = [hero.to_dict(rules=('-hero_powers',)) for hero in heroes]
        return jsonify(heroes_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    try:
        hero = Hero.query.get(id)
        if not hero:
            return make_response({"error": "Hero not found"}, 404)
        return jsonify(hero.to_dict(rules=('-power.hero', '-hero_powers.hero'))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/powers', methods=['GET'])
def get_all_powers():
    try:
        powers = Power.query.all()
        powers_data = [power.to_dict(rules=('-hero_powers',)) for power in powers]
        return jsonify(powers_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    try:
        power = Power.query.get(id)
        if not power:
            return make_response({"error": "Power not found"}, 404)
        return jsonify(power.to_dict(rules=('-hero_powers',))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    try:
        power = Power.query.get(id)
        if not power:
            return make_response({"error": "Power not found"}, 404)

        data = request.get_json()
        if "description" in data:
            description = data.get("description")
            if not isinstance(description, str) or len(description) < 20:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
            power.description = description
            db.session.commit()

        return jsonify(power.to_dict(rules=('-hero_powers',))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    try:
        data = request.get_json()

        strength = data.get('strength')
        if strength not in ["Strong", "Weak", "Average"]:
            return jsonify({'errors': ["validation errors"]}), 400

        hero_id = data.get('hero_id')
        power_id = data.get('power_id')

        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if not hero:
            return jsonify({'errors': ["Hero not found"]}), 404
        if not power:
            return jsonify({'errors': ["Power not found"]}), 404

        hero_power = HeroPower(
            hero_id=hero_id,
            power_id=power_id,
            strength=strength
        )

        db.session.add(hero_power)
        db.session.commit()

        response = {
            'id': hero_power.id,
            'hero_id': hero_power.hero_id,
            'power_id': hero_power.power_id,
            'strength': hero_power.strength,
            'hero': hero.name,
            'power': power.name    
            }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
