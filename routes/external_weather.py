from flask import Blueprint, request, jsonify
from services.weather_client import geocode_city, fetch_weather

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/weather", methods=["GET"])
def weather_api():
    try:
        city = request.args.get("city")
        if not city:
            return jsonify({"error": "city parameter is required"}), 400

        geo = geocode_city(city)
        lat, lon = geo["lat"], geo["lon"]

        data = fetch_weather(lat, lon)
        return jsonify(data), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception:
        return jsonify({"error": "Weather service failed"}), 502
