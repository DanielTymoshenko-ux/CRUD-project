from flask import Blueprint, request, jsonify
from services.weather_client import geocode_city, fetch_weather, WeatherError

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/weather", methods=["GET"])
def weather_api():
    try:
        city = request.args.get("city")
        if not city:
            return jsonify({"error": "city parameter is required"}), 400

        lat, lon = geocode_city(city)
        data = fetch_weather(lat, lon)

        return jsonify(data), 200

    except WeatherError as e:
        return jsonify({"error": e.msg}), e.status

    except Exception:
        return jsonify({"error": "Weather service failed"}), 502
