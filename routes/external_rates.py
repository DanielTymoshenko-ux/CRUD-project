from flask import Blueprint, request, jsonify
from services.currency_client import fetch_rates, CurrencyError

rates_bp = Blueprint("rates", __name__)

@rates_bp.route("/rates", methods=["GET"])
def rates_api():
    try:
        base = request.args.get("base")
        symbols = request.args.get("symbols")

        data = fetch_rates(base, symbols)
        return jsonify(data), 200

    except CurrencyError as e:
        return jsonify({"error": e.msg}), e.status
    except Exception:
        return jsonify({"error": "Currency service failed"}), 502
