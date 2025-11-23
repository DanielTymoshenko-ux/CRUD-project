
from flask import Blueprint, request, jsonify
from services.currency_client import fetch_rates, CurrencyError

rates_bp = Blueprint("rates", __name__)

@rates_bp.route("/rates_api", methods=["GET"])
def rates_api():
    base = request.args.get("base", "EUR").upper()
    symbols_raw = request.args.get("symbols")
    symbols = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()] if symbols_raw else None

    try:
        data = fetch_rates(base=base, symbols=symbols)
        rates_list = [{"currency": k, "value": v} for k, v in sorted(data["rates"].items())]
        return jsonify({"base": data["base"], "rates": rates_list}), 200

    except CurrencyError as e:
        return jsonify({
            "timestamp": None,
            "status": e.status,
            "error": "Currency Service",
            "message": e.msg
        }), e.status

    except Exception as ex:
        return jsonify({
            "timestamp": None,
            "status": 502,
            "error": "Bad Gateway",
            "message": "Unexpected error while fetching rates"
        }), 502
