import os
import uuid

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from services.gemini_service import generate_recommendation
from services.mock_data import get_mock_products

app = Flask(__name__)
app.config.from_object(Config)

# The frontend lives on GitHub Pages (a different origin), so CORS must
# list that origin explicitly and allow credentials for the session cookie.
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def _get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@app.route("/")
def index():
    return jsonify({"service": "PocketSmart AI API", "status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "PocketSmart AI (Flask)"})


@app.route("/generate-home", methods=["POST"])
def generate_home():
    data = request.get_json(silent=True) or {}
    budget = _to_float(data.get("budget"))
    details = (data.get("details") or "").strip()

    if not budget or budget <= 0 or not details:
        return jsonify({"error": "A positive budget and room details are required."}), 400

    session_id = _get_session_id()
    recommendation = generate_recommendation("home", {"budget": budget, "details": details})
    products = get_mock_products("home", budget)

    return jsonify(
        {
            "session_id": session_id,
            "planner": "home",
            "recommendation": recommendation,
            "suggested_products": products,
        }
    )


@app.route("/generate-party", methods=["POST"])
def generate_party():
    data = request.get_json(silent=True) or {}
    budget = _to_float(data.get("budget"))
    event_type = (data.get("event_type") or "").strip()
    guests = _to_float(data.get("guests"))

    if not budget or budget <= 0 or not event_type or not guests or guests < 1:
        return jsonify(
            {"error": "A positive budget, event type and at least 1 guest are required."}
        ), 400

    session_id = _get_session_id()
    recommendation = generate_recommendation(
        "party", {"budget": budget, "event_type": event_type, "guests": int(guests)}
    )
    products = get_mock_products("party", budget)

    return jsonify(
        {
            "session_id": session_id,
            "planner": "party",
            "recommendation": recommendation,
            "suggested_products": products,
        }
    )


@app.route("/generate-jewelry", methods=["POST"])
def generate_jewelry():
    # multipart/form-data because an outfit image may be attached
    budget = _to_float(request.form.get("budget"))
    occasion = (request.form.get("occasion") or "").strip()
    image_file = request.files.get("outfit_image")

    if not budget or budget <= 0 or not occasion:
        return jsonify({"error": "A positive budget and occasion are required."}), 400

    image_path = None
    if image_file and image_file.filename:
        if not _allowed_file(image_file.filename):
            return jsonify({"error": "Unsupported image type. Use PNG, JPG or WEBP."}), 400
        filename = secure_filename(f"{uuid.uuid4().hex}_{image_file.filename}")
        image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        image_file.save(image_path)

    try:
        session_id = _get_session_id()
        recommendation = generate_recommendation(
            "jewelry", {"budget": budget, "occasion": occasion}, image_path=image_path
        )
    finally:
        # Images are only needed for this one request; free hosts have
        # ephemeral disks anyway, so don't let uploads pile up.
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    products = get_mock_products("jewelry", budget)

    return jsonify(
        {
            "session_id": session_id,
            "planner": "jewelry",
            "recommendation": recommendation,
            "suggested_products": products,
            "image_used": bool(image_path),
        }
    )


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": "Image is too large (max 8 MB)."}), 413


if __name__ == "__main__":
    app.run(debug=(Config.FLASK_ENV == "development"))
