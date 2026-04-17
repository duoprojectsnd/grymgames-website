"""
OKUBI Website — Steam Login Backend
Handles Steam OpenID authentication and links Steam IDs to DynamoDB.
Run: python auth_server.py
"""

import os, json, copy, re, secrets, smtplib, ssl, hashlib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decimal import Decimal
from urllib.parse import urlencode, parse_qs
import requests
import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from flask import Flask, redirect, request, session, jsonify, send_from_directory

# ─── Config ───────────────────────────────────────────────────────────────────
# Load Render secret file (config.env) into os.environ if it exists
_secret_file = os.environ.get("SECRET_FILE_PATH", "/etc/secrets/config.env")
if os.path.exists(_secret_file):
    with open(_secret_file) as _sf:
        for _line in _sf:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

# Load local config file if available (dev mode)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "website_config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        _cfg = json.load(f)
else:
    _cfg = {}

# Override config with environment variables when deployed
_cfg["aws_access_key_id"] = os.environ.get("AWS_ACCESS_KEY_ID", _cfg.get("aws_access_key_id", ""))
_cfg["aws_secret_access_key"] = os.environ.get("AWS_SECRET_ACCESS_KEY", _cfg.get("aws_secret_access_key", ""))
_cfg["aws_region"] = os.environ.get("AWS_REGION", _cfg.get("aws_region", "us-east-1"))
_cfg["table_name"] = os.environ.get("TABLE_NAME", _cfg.get("table_name", "Users"))
_cfg["steam_api_key"] = os.environ.get("STEAM_API_KEY", _cfg.get("steam_api_key", ""))
_cfg["square_access_token"] = os.environ.get("SQUARE_ACCESS_TOKEN", _cfg.get("square_access_token", ""))
_cfg["square_location_id"] = os.environ.get("SQUARE_LOCATION_ID", _cfg.get("square_location_id", ""))
_cfg["square_application_id"] = os.environ.get("SQUARE_APPLICATION_ID", _cfg.get("square_application_id", ""))
_cfg["square_environment"] = os.environ.get("SQUARE_ENVIRONMENT", _cfg.get("square_environment", "sandbox"))

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def _sanitize(obj):
    """Convert Decimal values to int/float for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(i) for i in obj]
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    return obj

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000")

# Gmail SMTP for confirmation emails
GMAIL_USER = os.environ.get("APPUSERNAME", _cfg.get("gmail_user", ""))
GMAIL_APP_PASSWORD = os.environ.get("APPPASSWORD", _cfg.get("gmail_app_password", ""))

_serializer = TypeSerializer()
_deserializer = TypeDeserializer()

# In-memory pending email confirmations: {token: {steam_id, email, ts}}
_pending_confirms = {}

# ─── DynamoDB helpers ─────────────────────────────────────────────────────────
def _dynamo():
    return boto3.client(
        "dynamodb",
        region_name=_cfg["aws_region"],
        aws_access_key_id=_cfg["aws_access_key_id"],
        aws_secret_access_key=_cfg["aws_secret_access_key"],
    )


def _deser(item: dict) -> dict:
    return {k: _deserializer.deserialize(v) for k, v in item.items()}


def fetch_user(steam_id: str) -> dict | None:
    resp = _dynamo().get_item(
        TableName=_cfg["table_name"],
        Key={"steamID": {"S": steam_id}},
    )
    if "Item" in resp:
        return _deser(resp["Item"])
    return None


def create_user_from_template(steam_id: str, persona: str = "", email: str = "") -> dict | None:
    template = fetch_user("DefaultPlayer")
    if not template:
        return None
    user = copy.deepcopy(template)
    user["steamID"] = steam_id
    if email:
        info = user.get("Info", {})
        info["email"] = email
        user["Info"] = info
    if persona:
        stat = user.get("Stat", {})
        stat["SteamName"] = persona
        user["Stat"] = stat
    item = {k: _serializer.serialize(v) for k, v in user.items()}
    _dynamo().put_item(TableName=_cfg["table_name"], Item=item)
    return user


def update_user_email(steam_id: str, email: str):
    user = fetch_user(steam_id)
    info = user.get("Info", {}) if user else {}
    info["email"] = email
    _dynamo().update_item(
        TableName=_cfg["table_name"],
        Key={"steamID": {"S": steam_id}},
        UpdateExpression="SET #info = :i",
        ExpressionAttributeNames={"#info": "Info"},
        ExpressionAttributeValues={":i": _serializer.serialize(info)},
    )


# ─── Steam OpenID helpers ────────────────────────────────────────────────────
def get_steam_profile(steam_id: str) -> dict:
    """Fetch Steam display name and avatar via Steam Web API."""
    api_key = _cfg.get("steam_api_key", "")
    if not api_key:
        return {"name": "", "avatar": ""}
    try:
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_id}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        players = data.get("response", {}).get("players", [])
        if players:
            return {
                "name": players[0].get("personaname", ""),
                "avatar": players[0].get("avatarmedium", ""),
            }
    except Exception:
        pass
    return {"name": "", "avatar": ""}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/welcome")
def welcome_page():
    return send_from_directory(".", "welcome.html")


@app.route("/auth/steam/login")
def steam_login():
    """Redirect the user to Steam's OpenID login page."""
    params = {
        "openid.ns":         "http://specs.openid.net/auth/2.0",
        "openid.mode":       "checkid_setup",
        "openid.return_to":  f"{SITE_URL}/auth/steam/callback",
        "openid.realm":      SITE_URL,
        "openid.identity":   "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return redirect(f"{STEAM_OPENID_URL}?{urlencode(params)}")


@app.route("/auth/steam/callback")
def steam_callback():
    """Handle Steam's OpenID callback and verify the assertion."""
    args = request.args.to_dict()

    # Build verification request
    verify_params = dict(args)
    verify_params["openid.mode"] = "check_authentication"

    try:
        resp = requests.post(STEAM_OPENID_URL, data=verify_params, timeout=10)
        if "is_valid:true" not in resp.text:
            return redirect("/?login=failed")
    except Exception:
        return redirect("/?login=failed")

    # Extract Steam ID from claimed_id
    claimed = args.get("openid.claimed_id", "")
    match = re.search(r"(\d{17})$", claimed)
    if not match:
        return redirect("/?login=failed")

    steam_id = match.group(1)
    session["steam_id"] = steam_id

    # Fetch Steam profile (name + avatar)
    profile = get_steam_profile(steam_id)
    persona = profile["name"]
    session["avatar"] = profile["avatar"]

    # Check if user exists in DynamoDB
    user = fetch_user(steam_id)
    if user:
        session["username"] = persona or user.get("Stat", {}).get("SteamName", steam_id)
        session["is_new"] = False
    else:
        user = create_user_from_template(steam_id, persona=persona)
        if user:
            session["username"] = persona or steam_id
            session["is_new"] = True
        else:
            session["username"] = persona or steam_id
            session["is_new"] = False

    return redirect("/welcome")


@app.route("/auth/steam/logout")
def steam_logout():
    session.clear()
    return redirect("/")


@app.route("/auth/me")
def auth_me():
    """Return current logged-in user info as JSON."""
    if "steam_id" not in session:
        return jsonify({"logged_in": False})
    user = fetch_user(session["steam_id"])
    stat = user.get("Stat", {}) if user else {}
    currencies = user.get("Currencies", {}) if user else {}
    return jsonify({
        "logged_in":  True,
        "steam_id":   session["steam_id"],
        "username":   stat.get("SteamName", session.get("username", "")),
        "avatar":     session.get("avatar", ""),
        "curr03":     str(currencies.get("curr03", currencies.get("Curr03", "0"))),
        "is_new":     session.get("is_new", False),
    })


@app.route("/auth/set-email", methods=["POST"])
def set_email():
    """Set email for logged-in user."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "No email provided"}), 400
    try:
        update_user_email(session["steam_id"], email)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/auth/claim-welcome-gift", methods=["POST"])
def claim_welcome_gift():
    """Send confirmation email. Gift is awarded when email is confirmed."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "No email provided"}), 400
    steam_id = session["steam_id"]
    try:
        user = fetch_user(steam_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        stat = user.get("Stat", {})
        if stat.get("WelcomeGiftClaimed") == "True":
            return jsonify({"ok": True, "already_claimed": True})

        # Generate confirmation token
        token = secrets.token_urlsafe(32)
        _pending_confirms[token] = {
            "steam_id": steam_id,
            "email": email,
            "ts": time.time(),
        }
        # Clean old tokens (>1 hour)
        cutoff = time.time() - 3600
        for k in list(_pending_confirms):
            if _pending_confirms[k]["ts"] < cutoff:
                del _pending_confirms[k]

        confirm_url = f"{SITE_URL}/auth/confirm-email?token={token}"
        _send_confirmation_email(email, confirm_url)
        return jsonify({"ok": True, "pending": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _send_confirmation_email(to_email: str, confirm_url: str):
    """Send a styled confirmation email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "OKUBI — Confirm Your Email"
    msg["From"] = f"OKUBI <{GMAIL_USER}>"
    msg["To"] = to_email

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OKUBI — Confirm Your Email</title>
  <style type="text/css">
    body, table, td, a {{ -webkit-text-size-adjust: 100%%; -ms-text-size-adjust: 100%%; }}
    body {{ margin: 0; padding: 0; width: 100% !important; }}
    a {{ text-decoration: none; }}
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
  </style>
</head>
<body style="margin:0; padding:0; background-color:#08080c;">
  <div style="display:none; max-height:0; overflow:hidden;">Confirm your email to claim 500 Void Pearls!</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#08080c;">
    <tr>
      <td align="center" style="padding: 24px 12px;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="background-color:#0e0e14; overflow:hidden;">
          <!-- NEON BAR -->
          <tr>
            <td style="height:3px; background: linear-gradient(90deg, #d4a853, #f0d060, #d4a853); background-size: 300% 100%;"></td>
          </tr>
          <!-- LOGO -->
          <tr>
            <td align="center" style="padding: 40px 0 4px 0;">
              <a href="https://grymgames.net" target="_blank"><img src="https://i.ibb.co/KzpCwCVR/okubi-logo.png" alt="OKUBI" width="120" style="display:block; width:120px; height:auto;" /></a>
            </td>
          </tr>
          <!-- HEADLINE -->
          <tr>
            <td align="center" style="padding: 20px 32px 0 32px;">
              <h1 style="margin:0; font-family:'Bebas Neue',Impact,sans-serif; font-size:42px; font-weight:400; letter-spacing:0.04em; line-height:1.0; color:#ffffff; text-transform:uppercase;">
                Confirm Your<br>
                <span style="color:#d4a853;">Email Address</span>
              </h1>
            </td>
          </tr>
          <!-- SUBHEADLINE -->
          <tr>
            <td align="center" style="padding: 16px 40px 0 40px;">
              <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:400; color:#9a9ab0; line-height:1.6;">
                Click the button below to verify your email and claim your welcome gift of <strong style="color:#d4a853;">500 Void Pearls</strong>.
              </p>
            </td>
          </tr>
          <!-- REWARD BOX -->
          <tr>
            <td align="center" style="padding: 28px 40px 0 40px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="background:rgba(212,168,83,0.06); border:1px solid rgba(212,168,83,0.2); border-radius:8px;">
                <tr>
                  <td align="center" style="padding: 20px 40px;">
                    <p style="margin:0; font-family:'Bebas Neue',Impact,sans-serif; font-size:36px; color:#d4a853; line-height:1;">500</p>
                    <p style="margin:4px 0 0 0; font-family:'Space Grotesk',sans-serif; font-size:12px; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#9a9ab0;">Void Pearls</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- CTA BUTTON -->
          <tr>
            <td align="center" style="padding: 28px 40px 0 40px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                <tr>
                  <td align="center" style="border-radius:6px; background:linear-gradient(135deg, #d4a853, #b8912e);">
                    <a href="{confirm_url}" target="_blank" style="display:block; padding:18px 32px; font-family:'Bebas Neue',Impact,sans-serif; font-size:18px; font-weight:400; letter-spacing:0.14em; text-transform:uppercase; color:#0a0908; text-decoration:none; text-align:center;">
                      &#10003;&ensp;Confirm Email &amp; Claim Gift
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- SMALL PRINT -->
          <tr>
            <td align="center" style="padding: 20px 40px 0 40px;">
              <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:11px; color:#4a4a5e; line-height:1.5;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:6px 0 0 0; font-family:'Space Grotesk',sans-serif; font-size:11px; color:#d4a853; word-break:break-all;">
                {confirm_url}
              </p>
            </td>
          </tr>
          <!-- FOOTER -->
          <tr>
            <td align="center" style="padding: 40px 32px 24px 32px; border-top: 1px solid #1a1a28;">
              <p style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:11px; color:#3a3a4e;">
                &copy; 2026 Grym Games &middot; OKUBI
              </p>
              <p style="margin:6px 0 0 0; font-family:'Space Grotesk',sans-serif; font-size:10px; color:#2a2a3a;">
                If you didn't request this, you can safely ignore this email.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls(context=ctx)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())


@app.route("/auth/confirm-email")
def confirm_email():
    """Verify token from email link, save email + award gift."""
    token = request.args.get("token", "")
    pending = _pending_confirms.pop(token, None)
    if not pending:
        return redirect("/?error=invalid_or_expired_token")

    steam_id = pending["steam_id"]
    email = pending["email"]

    try:
        update_user_email(steam_id, email)
        user = fetch_user(steam_id)
        if user:
            stat = user.get("Stat", {})
            if stat.get("WelcomeGiftClaimed") != "True":
                currencies = user.get("Currencies", {})
                current_pearls = int(currencies.get("curr03", currencies.get("Curr03", "0")))
                currencies["curr03"] = str(current_pearls + 500)
                stat["WelcomeGiftClaimed"] = "True"
                dynamo = _dynamo()
                table = _cfg["table_name"]
                key = {"steamID": {"S": steam_id}}
                dynamo.update_item(
                    TableName=table, Key=key,
                    UpdateExpression="SET #curr = :c, #st = :s",
                    ExpressionAttributeNames={"#curr": "Currencies", "#st": "Stat"},
                    ExpressionAttributeValues={
                        ":c": _serializer.serialize(currencies),
                        ":s": _serializer.serialize(stat),
                    },
                )
    except Exception:
        pass

    return redirect("/?confirmed=true")


@app.route("/auth/profile")
def auth_profile():
    """Return full player profile data for the character page."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    user = fetch_user(session["steam_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    stat = user.get("Stat", {})
    currencies = user.get("Currencies", {})
    return jsonify({
        "steam_id":          session["steam_id"],
        "avatar":            session.get("avatar", ""),
        "username":          stat.get("Username", "Unknown"),
        "level":             stat.get("Level", "0"),
        "mmr":               stat.get("MMR", "0"),
        "default_character": stat.get("Default_Character", "Unknown"),
        "alliance":          stat.get("Alliance", "None"),
        "ban_status":        stat.get("BanStatus", "False"),
        "match_found_id":    stat.get("MatchFoundID", ""),
        "currencies":        _sanitize(currencies),
        "stat":              _sanitize(stat),
    })


# ─── Shop endpoints ──────────────────────────────────────────────────────────
SHOP_PRICES = {
    "weap01001": 2500,
    "weap01002": 1800,
    "weap01003": 1200,
    "outfit001": 4800,
    "outfit002": 2400,   # sale price
    "outfit003": 1600,
    "outfit004": 2800,
    "outfit005": 5200,
    "pet01001":  5500,
    "pet01002":  3000,
    "emote01001": 800,
    "emote01002": 1200,
    "acc01001":  6000,
    "acc01002":  1500,
    "acc01003":  1400,
    # Set bundles
    "setbundle01": 9800,
    "setbundle02": 8500,
    "setbundle03": 11000,
    # Set pieces
    "sets01001": 4800,
    "sets01002": 2500,
    "sets01003": 3500,
    "sets01004": 1200,
    "sets01005": 900,
    "sets01006": 800,
    "sets02001": 2400,  # sale price
    "sets02002": 2200,
    "sets02003": 1800,
    "sets02004": 1000,
    "sets02005": 850,
    "sets02006": 750,
    "sets03001": 4500,
    "sets03002": 2800,
    "sets03003": 2000,
    "sets03004": 1100,
    "sets03005": 4000,
    "sets03006": 1600,
}


@app.route("/auth/shop-data")
def shop_data():
    """Return player's owned items for the shop page."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    user = fetch_user(session["steam_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    items = user.get("Items", {})
    return jsonify({"owned_items": _sanitize(items)})


@app.route("/auth/shop-buy", methods=["POST"])
def shop_buy():
    """Purchase an item: deduct curr03, add item to Items map."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id", "")
    if item_id not in SHOP_PRICES:
        return jsonify({"error": "Invalid item"}), 400

    price = SHOP_PRICES[item_id]
    steam_id = session["steam_id"]
    dynamo = _dynamo()
    table = _cfg["table_name"]
    key = {"steamID": {"S": steam_id}}

    # Read raw DynamoDB item (same pattern as _credit_pearls_for_order)
    raw = dynamo.get_item(TableName=table, Key=key).get("Item")
    if not raw:
        return jsonify({"error": "User not found"}), 404

    currencies_map = raw.get("Currencies", {}).get("M", {})
    curr_key = "curr03" if "curr03" in currencies_map else "Curr03"
    curr03 = int(currencies_map.get(curr_key, {}).get("S", "0"))

    if curr03 < price:
        return jsonify({"error": "Insufficient Void Pearl balance"}), 400

    items_map = raw.get("Items", {}).get("M", {})
    if item_id in items_map:
        return jsonify({"error": "Already owned"}), 400

    new_balance = curr03 - price

    # If Items map doesn't exist yet, create it with the item in one shot
    if "Items" not in raw:
        dynamo.update_item(
            TableName=table, Key=key,
            UpdateExpression="SET Currencies.#ck = :nb, #items = :imap",
            ExpressionAttributeNames={"#ck": curr_key, "#items": "Items"},
            ExpressionAttributeValues={
                ":nb": {"S": str(new_balance)},
                ":imap": {"M": {item_id: {"S": "1"}}},
            },
        )
    else:
        dynamo.update_item(
            TableName=table, Key=key,
            UpdateExpression="SET Currencies.#ck = :nb, #items.#ik = :iv",
            ExpressionAttributeNames={"#ck": curr_key, "#items": "Items", "#ik": item_id},
            ExpressionAttributeValues={
                ":nb": {"S": str(new_balance)},
                ":iv": {"S": "1"},
            },
        )

    print(f"[SHOP] {steam_id} bought {item_id} for {price} VP (balance: {new_balance})")
    return jsonify({"success": True, "new_balance": new_balance})


# ─── Square Checkout (Void Pearls) ───────────────────────────────────────────
SQUARE_ENV = _cfg.get("square_environment", "sandbox")
SQUARE_ACCESS_TOKEN = _cfg.get("square_access_token", "")
SQUARE_LOCATION_ID = _cfg.get("square_location_id", "")
SQUARE_BASE_URL = (
    "https://connect.squareupsandbox.com" if SQUARE_ENV == "sandbox"
    else "https://connect.squareup.com"
)

VOID_PEARL_PACKS = {
    "vp300":  {"name": "300 Void Pearls",    "pearls": 300,   "price_cents": 299},
    "vp800":  {"name": "800 Void Pearls",    "pearls": 800,   "price_cents": 699},
    "vp1700": {"name": "1,700 Void Pearls",  "pearls": 1700,  "price_cents": 1299},
    "vp3500": {"name": "3,500 Void Pearls",  "pearls": 3500,  "price_cents": 2499},
    "vp7500": {"name": "7,500 Void Pearls",  "pearls": 7500,  "price_cents": 4999},
}


def _credit_pearls_for_order(order_id):
    """
    Look up a Square order, verify payment, credit pearls, mark claimed.
    Returns (success: bool, detail: str).
    """
    sq_headers = {
        "Square-Version": "2024-12-18",
        "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    }
    resp = requests.get(
        f"{SQUARE_BASE_URL}/v2/orders/{order_id}",
        headers=sq_headers,
        timeout=15,
    )
    if resp.status_code != 200:
        return False, "order_not_found"

    order_data = resp.json().get("order", {})
    metadata = order_data.get("metadata", {})
    steam_id = metadata.get("steam_id", "")
    pack_id = metadata.get("pack_id", "")

    if not steam_id or pack_id not in VOID_PEARL_PACKS:
        return False, "invalid_metadata"

    # Already claimed?
    if metadata.get("claimed") == "true":
        return False, "already_claimed"

    # Has payment?
    tenders = order_data.get("tenders", [])
    if not tenders:
        return False, "not_paid"

    pearls_to_add = VOID_PEARL_PACKS[pack_id]["pearls"]

    # Read current balance
    try:
        item = _dynamo().get_item(
            TableName=_cfg["table_name"],
            Key={"steamID": {"S": steam_id}},
        ).get("Item", {})
        currencies_map = item.get("Currencies", {}).get("M", {})
        curr_key = "curr03" if "curr03" in currencies_map else "Curr03"
        current = int(currencies_map.get(curr_key, {}).get("S", "0"))
    except Exception:
        curr_key = "curr03"
        current = 0

    new_balance = current + pearls_to_add

    _dynamo().update_item(
        TableName=_cfg["table_name"],
        Key={"steamID": {"S": steam_id}},
        UpdateExpression="SET Currencies.#ck = :nb",
        ExpressionAttributeNames={"#ck": curr_key},
        ExpressionAttributeValues={":nb": {"S": str(new_balance)}},
    )

    # Mark claimed in Square
    try:
        requests.put(
            f"{SQUARE_BASE_URL}/v2/orders/{order_id}",
            json={
                "order": {
                    "location_id": SQUARE_LOCATION_ID,
                    "version": order_data.get("version", 1),
                    "metadata": {**metadata, "claimed": "true"},
                }
            },
            headers={**sq_headers, "Content-Type": "application/json"},
            timeout=15,
        )
    except Exception:
        pass

    print(f"[CREDIT] {pearls_to_add} pearls -> {steam_id} (order {order_id})")
    return True, f"{pearls_to_add}"


@app.route("/auth/buy-pearls", methods=["POST"])
def buy_pearls():
    """Create a Square Checkout link for a Void Pearl pack."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(force=True)
    pack_id = data.get("pack_id", "")
    if pack_id not in VOID_PEARL_PACKS:
        return jsonify({"error": "Invalid pack"}), 400

    pack = VOID_PEARL_PACKS[pack_id]
    idempotency_key = secrets.token_hex(16)

    payload = {
        "idempotency_key": idempotency_key,
        "order": {
            "location_id": SQUARE_LOCATION_ID,
            "line_items": [
                {
                    "name": pack["name"],
                    "quantity": "1",
                    "base_price_money": {
                        "amount": pack["price_cents"],
                        "currency": "CAD",
                    },
                }
            ],
            "metadata": {
                "steam_id": session["steam_id"],
                "pack_id": pack_id,
            },
        },
        "checkout_options": {
            "redirect_url": request.host_url.rstrip("/") + "/payment/success",
        },
    }

    headers = {
        "Square-Version": "2024-12-18",
        "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        f"{SQUARE_BASE_URL}/v2/online-checkout/payment-links",
        json=payload,
        headers=headers,
        timeout=15,
    )

    if resp.status_code not in (200, 201):
        return jsonify({"error": "Payment service error", "detail": resp.text}), 502

    result = resp.json()
    checkout_url = result.get("payment_link", {}).get("url", "")
    order_id = result.get("payment_link", {}).get("order_id", "")

    return jsonify({"checkout_url": checkout_url, "order_id": order_id})


@app.route("/auth/claim-pearls", methods=["POST"])
def claim_pearls():
    """Client calls this after returning from Square checkout."""
    if "steam_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(force=True)
    order_id = data.get("order_id", "")
    if not order_id:
        return jsonify({"error": "No order_id"}), 400

    # Verify the order belongs to this user via Square lookup
    sq_headers = {
        "Square-Version": "2024-12-18",
        "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    }
    resp = requests.get(
        f"{SQUARE_BASE_URL}/v2/orders/{order_id}",
        headers=sq_headers,
        timeout=15,
    )
    if resp.status_code != 200:
        return jsonify({"error": "Order not found"}), 404

    metadata = resp.json().get("order", {}).get("metadata", {})
    if metadata.get("steam_id") != session["steam_id"]:
        return jsonify({"error": "Order mismatch"}), 403

    success, detail = _credit_pearls_for_order(order_id)
    if success:
        return jsonify({"success": True, "pearls": int(detail)})
    elif detail == "already_claimed":
        return jsonify({"error": "Already claimed", "status": "already_claimed"}), 200
    elif detail == "not_paid":
        return jsonify({"error": "Payment not completed yet", "status": "pending"}), 402
    else:
        return jsonify({"error": detail}), 400


@app.route("/webhook/square", methods=["POST"])
def square_webhook():
    """
    Square sends payment.completed events here.
    Credits pearls server-side — no client involvement needed.
    """
    event = request.get_json(force=True)
    event_type = event.get("type", "")
    print(f"[WEBHOOK] Received event: {event_type}")

    if event_type != "payment.completed":
        return "", 200

    payment = event.get("data", {}).get("object", {}).get("payment", {})
    order_id = payment.get("order_id", "")
    if not order_id:
        print("[WEBHOOK] No order_id in payment event")
        return "", 200

    success, detail = _credit_pearls_for_order(order_id)
    print(f"[WEBHOOK] order={order_id} result={success} detail={detail}")
    return "", 200


@app.route("/payment/success")
def payment_success():
    """Square redirect fallback — just sends user back to shop."""
    return redirect("/shop.html?payment=success")


if __name__ == "__main__":
    print("=== OKUBI Auth Server -- http://localhost:5000 ===")
    app.run(host="0.0.0.0", port=5000, debug=True)
