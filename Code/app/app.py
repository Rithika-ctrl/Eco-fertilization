import sqlite3
import datetime
import requests  # Added to handle location lookup
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for
from BestTimeToFertilizeModule import BestTimeToFertilize
from NPKEstimatorModule import NPKEstimator

app = Flask(__name__)
app.secret_key = "eco_secret_key_123"
DATABASE = 'users.db'

# ==========================================================
# 1. API KEY (Integrated)
# ==========================================================
OPENWEATHER_API_KEY = "a2b002602129dc21ab0935cab87ef027" 


# --- AGRO-CLIMATIC ZONES DATABASE ---
# --- AGRO-CLIMATIC ZONES DATABASE (FINAL COMPLETE VERSION) ---
AGRO_ZONES = {
    "andaman & nicobar": [
        "RICE", "COCONUT", "ARECANUT", "BANANA", "PAPAYA", "BLACK PEPPER", "RUBBER", 
        "GINGER", "TURMERIC", "CLOVE", "CINNAMON", "NUTMEG", "SWEET POTATO", 
        "TAPIOCA", "YAM", "PINEAPPLE", "MANGO", "LEMONGRASS", "ALOE VERA"
    ],

    "andhra pradesh": [
        "RICE", "COTTON", "CHILLI", "TOOR", "BENGAL GRAM", "GROUNDNUT", "SUNFLOWER", 
        "SUGARCANE", "MAIZE", "JOWAR", "BAJRA", "RAGI", "CHICKPEA", "PIGEON PEA", 
        "GREEN GRAM", "BLACK GRAM", "COWPEA", "TOBACCO", "TURMERIC", "ONION", 
        "TOMATO", "BRINJAL", "OKRA", "MANGO", "BANANA", "PAPAYA", "SWEET POTATO", 
        "YAM", "BEETROOT", "SUGAR BEET", "ALFALFA", "NAPIER GRASS", "CORIANDER", 
        "COCONUT", "FODDER SORGHUM", "LEMONGRASS"
    ],

    "arunachal pradesh": [
        "RICE", "MAIZE", "MILLET", "POTATO", "GINGER", "TURMERIC", "ORANGE", 
        "PINEAPPLE", "TEA", "CARDAMOM", "KIWI", "APPLE", "CABBAGE", "CAULIFLOWER", 
        "RADISH", "BEANS", "MUSTARD", "SOYBEAN", "BLACK GRAM"
    ],

    "assam": [
        "RICE", "TEA", "JUTE", "SUGARCANE", "POTATO", "MUSTARD", "BANANA", "GINGER", 
        "TURMERIC", "BLACK PEPPER", "ARECANUT", "COCONUT", "ORANGE", "PAPAYA", 
        "PINEAPPLE", "JACKFRUIT", "GREEN GRAM", "BLACK GRAM", "LENTIL", "PEAS", 
        "CABBAGE", "CAULIFLOWER", "BRINJAL", "OKRA", "TOOR", "LEMONGRASS"
    ],

    "bihar": [
        "RICE", "WHEAT", "MAIZE", "TOOR", "BENGAL GRAM", "JUTE", "SUGARCANE", "POTATO", 
        "LENTIL", "PEAS", "CHICKPEA", "PIGEON PEA", "MUSTARD", "LINSEED", "SUNFLOWER", 
        "BANANA", "MANGO", "GUAVA", "LITCHI", "BRINJAL", "CAULIFLOWER", "CABBAGE", 
        "ONION", "TOMATO", "OKRA", "YAM", "BEETROOT", "FODDER MAIZE", "BERSEEM"
    ],

    "chandigarh": [
        "WHEAT", "RICE", "MAIZE", "MUSTARD", "POTATO", "CAULIFLOWER", "CABBAGE", 
        "CARROT", "RADISH", "SPINACH", "FODDER MAIZE", "FODDER SORGHUM", "BERSEEM", 
        "TULSI", "ALOE VERA", "MINT"
    ],

    "chhattisgarh": [
        "RICE", "MAIZE", "KODO MILLET", "TOOR", "BENGAL GRAM", "SOYBEAN", "GROUNDNUT", 
        "SUNFLOWER", "PIGEON PEA", "CHICKPEA", "GREEN GRAM", "BLACK GRAM", "MUSTARD", 
        "LINSEED", "WHEAT", "TOMATO", "BRINJAL", "OKRA", "CABBAGE", "CAULIFLOWER", 
        "POTATO", "GINGER", "TURMERIC", "LEMONGRASS"
    ],

    "dadra & nagar haveli": [
        "RICE", "RAGI", "JOWAR", "TOOR", "PIGEON PEA", "BEANS", "BANANA", "MANGO", 
        "CHICKPEA", "GROUNDNUT", "SUGARCANE", "BRINJAL", "TOMATO", "CABBAGE"
    ],

    "daman & diu": [
        "BAJRA", "JOWAR", "GROUNDNUT", "COCONUT", "BEANS", "SAPOTA", "BANANA", 
        "MANGO", "VEGETABLES", "FODDER SORGHUM"
    ],

    "delhi": [
        "WHEAT", "MUSTARD", "JOWAR", "BAJRA", "PADDY", "CAULIFLOWER", "CABBAGE", 
        "CARROT", "RADISH", "SPINACH", "OKRA", "TOMATO", "BRINJAL", "PEAS", 
        "BERSEEM", "TULSI", "ALOE VERA", "MINT", "NEEM"
    ],

    "goa": [
        "RICE", "COCONUT", "CASHEW", "ARECANUT", "MANGO", "BANANA", "PINEAPPLE", 
        "JACKFRUIT", "BLACK PEPPER", "SWEET POTATO", "RAGI", "COWPEA", "GROUNDNUT", 
        "TURMERIC"
    ],

    "gujarat": [
        "COTTON", "GROUNDNUT", "CASTOR", "SESAME", "WHEAT", "RICE", "BAJRA", "JOWAR", 
        "MAIZE", "TOOR", "PIGEON PEA", "CHICKPEA", "BENGAL GRAM", "GREEN GRAM", 
        "BLACK GRAM", "MUSTARD", "CUMIN", "FENNEL", "ONION", "GARLIC", "POTATO", 
        "BANANA", "MANGO", "PAPAYA", "POMEGRANATE", "GUAVA", "SUGARCANE", "TOBACCO", 
        "SUGAR BEET", "ALFALFA", "ALOE VERA", "LEMONGRASS"
    ],

    "haryana": [
        "WHEAT", "RICE", "COTTON", "MUSTARD", "SUGARCANE", "BARLEY", "MAIZE", "BAJRA", 
        "JOWAR", "CHICKPEA", "BENGAL GRAM", "SUNFLOWER", "GUAVA", "ORANGE", "KINNOW", 
        "POTATO", "CAULIFLOWER", "CABBAGE", "BERSEEM", "FODDER MAIZE", "FODDER SORGHUM", 
        "SUGAR BEET", "TULSI", "ALOE VERA", "MUSHROOM"
    ],

    "himachal pradesh": [
        "APPLE", "MAIZE", "WHEAT", "BARLEY", "POTATO", "PEAS", "GINGER", "TOMATO", 
        "CABBAGE", "CAULIFLOWER", "BEANS", "PLUM", "PEACH", "APRICOT", "PEAR", 
        "ORANGE", "MANGO", "LITCHI", "GUAVA", "POMEGRANATE", "TEA", "FLAX", 
        "HEMP", "BEETROOT", "MINT"
    ],

    "jammu & kashmir": [
        "APPLE", "RICE", "MAIZE", "WHEAT", "BARLEY", "RAJMASH", "FODDER MAIZE", 
        "WALNUT", "ALMOND", "CHERRY", "APRICOT", "PEAR", "PLUM", "SAFFRON", 
        "MUSTARD", "POTATO", "CABBAGE", "CAULIFLOWER"
    ],

    "jharkhand": [
        "RICE", "MAIZE", "WHEAT", "CHICKPEA", "BENGAL GRAM", "TOOR", "PIGEON PEA", 
        "BLACK GRAM", "GREEN GRAM", "MUSTARD", "GROUNDNUT", "POTATO", "BRINJAL", 
        "TOMATO", "CABBAGE", "CAULIFLOWER", "OKRA", "MANGO", "GUAVA", "JACKFRUIT", 
        "PAPAYA", "NIGER"
    ],

    "karnataka": [
        "RICE", "RAGI", "JOWAR", "MAIZE", "BAJRA", "WHEAT", "TOOR", "PIGEON PEA", 
        "CHICKPEA", "BENGAL GRAM", "GREEN GRAM", "BLACK GRAM", "COWPEA", "GROUNDNUT", 
        "SUNFLOWER", "SOYBEAN", "COTTON", "SUGARCANE", "TOBACCO", "COCONUT", 
        "ARECANUT", "COFFEE", "CASHEW", "CARDAMOM", "BLACK PEPPER", "GRAPES", 
        "POMEGRANATE", "MANGO", "BANANA", "TOMATO", "ONION", "POTATO", "GINGER", 
        "TURMERIC", "SUGAR BEET", "NAPIER GRASS", "YAM", "BEETROOT", "COCOA", 
        "ALOE VERA", "ASHWAGANDHA"
    ],

    "kerala": [
        "RICE", "COCONUT", "RUBBER", "TEA", "COFFEE", "BLACK PEPPER", "CARDAMOM", 
        "ARECANUT", "GINGER", "TURMERIC", "BANANA", "TAPIOCA", "NUTMEG", "CLOVE", 
        "CINNAMON", "CASHEW", "PINEAPPLE", "MANGO", "JACKFRUIT", "PAPAYA", 
        "YAM", "BEETROOT", "NAPIER GRASS", "COCOA", "LEMONGRASS"
    ],

    "lakshadweep": [
        "COCONUT", "BANANA", "PAPAYA", "GUAVA", "SAPOTA", "CHILLI", "TOMATO", 
        "BRINJAL", "SWEET POTATO", "DRUMSTICK", "BREADFRUIT"
    ],

    "madhya pradesh": [
        "SOYBEAN", "WHEAT", "CHICKPEA", "BENGAL GRAM", "MAIZE", "RICE", "JOWAR", 
        "BAJRA", "TOOR", "PIGEON PEA", "LENTIL", "GREEN GRAM", "BLACK GRAM", "PEAS", 
        "MUSTARD", "LINSEED", "SESAME", "GROUNDNUT", "COTTON", "SUGARCANE", "ONION", 
        "GARLIC", "POTATO", "TOMATO", "CORIANDER", "CHILLI", "GINGER", "ORANGE", 
        "GUAVA", "MANGO", "BANANA", "FLAX", "BEETROOT", "BERSEEM", "ASHWAGANDHA", 
        "ALOE VERA", "LEMONGRASS"
    ],

    "maharashtra": [
        "COTTON", "SOYBEAN", "SUGARCANE", "JOWAR", "BAJRA", "WHEAT", "RICE", "MAIZE", 
        "TOOR", "PIGEON PEA", "CHICKPEA", "BENGAL GRAM", "GREEN GRAM", "BLACK GRAM", 
        "GROUNDNUT", "SUNFLOWER", "SAFFLOWER", "SESAME", "ONION", "GRAPES", 
        "POMEGRANATE", "BANANA", "MANGO", "ORANGE", "CASHEW", "TOMATO", "BRINJAL", 
        "TURMERIC", "GINGER", "SUGAR BEET", "ALFALFA", "NAPIER GRASS", "BEETROOT"
    ],

    "manipur": [
        "RICE", "MAIZE", "POTATO", "MUSTARD", "PEAS", "CABBAGE", "CAULIFLOWER", 
        "PINEAPPLE", "ORANGE", "BANANA", "PASSION FRUIT", "GINGER", "TURMERIC", 
        "CHILLI", "KING CHILLI", "SOYBEAN", "BLACK GRAM", "RICE BEAN"
    ],

    "meghalaya": [
        "RICE", "MAIZE", "POTATO", "GINGER", "TURMERIC", "BLACK PEPPER", "ARECANUT", 
        "BETELVINE", "ORANGE", "PINEAPPLE", "BANANA", "PLUM", "PEAR", "PEACH", 
        "CASHEW", "TEA", "TOMATO", "CABBAGE", "CAULIFLOWER"
    ],

    "mizoram": [
        "RICE", "MAIZE", "MUSTARD", "SESAME", "POTATO", "GINGER", "TURMERIC", 
        "CHILLI", "SUGARCANE", "BANANA", "ORANGE", "PINEAPPLE", "PAPAYA", 
        "PASSION FRUIT", "HATKORA", "OIL PALM", "COFFEE", "TEA"
    ],

    "nagaland": [
        "RICE", "MAIZE", "MILLET", "PEAS", "MUSTARD", "POTATO", "GINGER", "TURMERIC", 
        "CHILLI", "CARDAMOM", "COFFEE", "TEA", "PINEAPPLE", "ORANGE", "PAPAYA", 
        "BANANA", "PASSION FRUIT", "VEGETABLES", "BAMBOO"
    ],

    "orissa": [
        "RICE", "GREEN GRAM", "BLACK GRAM", "TOOR", "PIGEON PEA", "CHICKPEA", 
        "BENGAL GRAM", "GROUNDNUT", "SESAME", "MUSTARD", "CASTOR", "SUNFLOWER", 
        "JUTE", "MESTA", "SUGARCANE", "COTTON", "POTATO", "BRINJAL", "TOMATO", 
        "CABBAGE", "CAULIFLOWER", "OKRA", "MANGO", "BANANA", "COCONUT", "CASHEW", 
        "TURMERIC", "GINGER", "SWEET POTATO", "YAM"
    ],

    "pondicherry": [
        "RICE", "SUGARCANE", "GROUNDNUT", "COTTON", "BLACK GRAM", "GREEN GRAM", 
        "COCONUT", "BANANA", "MANGO", "TAPIOCA", "BRINJAL", "OKRA", "FLOWERS", 
        "ARECANUT"
    ],

    "punjab": [
        "WHEAT", "RICE", "COTTON", "MAIZE", "SUGARCANE", "POTATO", "MUSTARD", 
        "SUNFLOWER", "BARLEY", "GREEN GRAM", "BLACK GRAM", "PEAS", "KINNOW", 
        "GUAVA", "MANGO", "PEAR", "PEACH", "GRAPES", "BER", "CARROT", "RADISH", 
        "MUSHROOM", "BERSEEM", "FODDER MAIZE", "FODDER SORGHUM", "BENGAL GRAM", 
        "SUGAR BEET", "MINT"
    ],

    "rajasthan": [
        "BAJRA", "JOWAR", "MAIZE", "WHEAT", "BARLEY", "CHICKPEA", "BENGAL GRAM", 
        "GREEN GRAM", "BLACK GRAM", "MOTH BEAN", "GROUNDNUT", "MUSTARD", "SOYBEAN", 
        "SESAME", "CASTOR", "COTTON", "CUMIN", "CORIANDER", "FENNEL", "FENUGREEK", 
        "ISABGOL", "GUAR", "ORANGE", "KINNOW", "POMEGRANATE", "GUAVA", "DATE PALM", 
        "BER", "ONION", "GARLIC", "BERSEEM", "ALFALFA", "FODDER SORGHUM", "ALOE VERA"
    ],

    "sikkim": [
        "MAIZE", "RICE", "WHEAT", "BUCKWHEAT", "MILLET", "BARLEY", "BLACK GRAM", 
        "RAJMASH", "SOYBEAN", "MUSTARD", "CARDAMOM", "GINGER", "TURMERIC", 
        "ORANGE", "POTATO", "TEA", "CHERRY PEPPER", "CABBAGE"
    ],

    "tamil nadu": [
        "RICE", "JOWAR", "BAJRA", "RAGI", "MAIZE", "TOOR", "PIGEON PEA", "GREEN GRAM", 
        "BLACK GRAM", "CHICKPEA", "BENGAL GRAM", "HORSE GRAM", "GROUNDNUT", "SESAME", 
        "SUNFLOWER", "COCONUT", "COTTON", "SUGARCANE", "BANANA", "MANGO", "TAPIOCA", 
        "COFFEE", "TEA", "RUBBER", "CASHEW", "TURMERIC", "CHILLI", "ONION", "TOMATO", 
        "BRINJAL", "OKRA", "JASMINE", "SUGAR BEET", "YAM", "BEETROOT", "NAPIER GRASS", 
        "COCOA", "ASHWAGANDHA"
    ],

    "tripura": [
        "RICE", "WHEAT", "MAIZE", "BLACK GRAM", "GREEN GRAM", "POTATO", "SUGARCANE", 
        "JUTE", "MESTA", "TEA", "RUBBER", "PINEAPPLE", "ORANGE", "JACKFRUIT", 
        "BANANA", "LITCHI", "LEMON", "CASHEW", "COCONUT", "ARECANUT", "GINGER", 
        "TURMERIC", "CHILLI"
    ],

    "uttar pradesh": [
        "WHEAT", "RICE", "SUGARCANE", "MAIZE", "BAJRA", "JOWAR", "BARLEY", 
        "CHICKPEA", "BENGAL GRAM", "TOOR", "PIGEON PEA", "LENTIL", "PEAS", 
        "BLACK GRAM", "GREEN GRAM", "MUSTARD", "GROUNDNUT", "LINSEED", "SESAME", 
        "SUNFLOWER", "POTATO", "ONION", "GARLIC", "TOMATO", "BRINJAL", "CABBAGE", 
        "CAULIFLOWER", "OKRA", "MANGO", "GUAVA", "AONLA", "PAPAYA", "BANANA", 
        "MENTHA", "BERSEEM", "FODDER MAIZE", "FODDER SORGHUM", "HEMP", "MINT", 
        "BEETROOT", "TULSI", "ALOE VERA", "NEEM"
    ],

    "uttaranchal": [
        "RICE", "WHEAT", "MAIZE", "RAGI", "BARLEY", "LENTIL", "PEAS", "SOYBEAN", 
        "MUSTARD", "GROUNDNUT", "SUGARCANE", "POTATO", "ONION", "CABBAGE", "TOMATO", 
        "APPLE", "PEAR", "PEACH", "PLUM", "APRICOT", "WALNUT", "LITCHI", "MANGO", 
        "ORANGE", "MALTA", "LEMON", "TEA", "HEMP", "FLAX", "BEETROOT", "MINT", 
        "TULSI", "BENGAL GRAM"
    ],

    "west bengal": [
        "RICE", "JUTE", "POTATO", "WHEAT", "MAIZE", "LENTIL", "CHICKPEA", "BENGAL GRAM", 
        "PEAS", "TOOR", "MUSTARD", "SESAME", "GROUNDNUT", "SUGARCANE", "TOBACCO", 
        "TEA", "BETELVINE", "MANGO", "BANANA", "PINEAPPLE", "GUAVA", "LITCHI", 
        "PAPAYA", "JACKFRUIT", "BRINJAL", "CABBAGE", "CAULIFLOWER", "OKRA", "TOMATO", 
        "CHILLI", "GINGER", "TURMERIC", "BEETROOT", "YAM", "FODDER MAIZE"
    ]
}

# --- DATABASE SETUP ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
        db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                state TEXT,
                city TEXT,
                crop TEXT,
                acres REAL,
                cost REAL,
                date_applied TEXT,
                npk_values TEXT
            )
        ''')
        db.commit()

init_db()

# Load AI Models
try:
    npk_estimator = NPKEstimator("nutrient_recommendation_full-2.csv")
except:
    print("Warning: CSV not found. AI features may be limited.")

# ==========================================================
# 2. PREDICTIVE SAFETY FUNCTION (48-Hour Forecast)
# ==========================================================
def check_forecast_safety(city, api_key):
    """
    Checks forecast for next 48 hours (16 blocks).
    Returns: (Is_Safe_Bool, Reason_String, Forecast_List_Data)
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        
        # Fallback if API fails
        if response.status_code != 200:
            return True, None, []

        data = response.json()
        total_rain_24h = 0.0
        high_pop_count = 0
        forecast_display = [] # List to store data for HTML

        # Check next 16 blocks (16 blocks * 3 hours = 48 hours)
        blocks_to_check = min(len(data['list']), 16)
        
        for i in range(blocks_to_check):
            item = data['list'][i]
            
            # 1. Extract Display Data
            date_part = item['dt_txt'].split(" ")[0][8:] # Get Day (e.g. "10")
            time_part = item['dt_txt'].split(" ")[1][:5] # Get Time (e.g. "12:00")
            display_time = f"{date_part}th {time_part}" 

            temp = int(item['main']['temp'])
            pop = int(item.get('pop', 0) * 100) # Probability %
            icon_code = item['weather'][0]['icon']
            
            forecast_display.append({
                "time": display_time,
                "temp": temp,
                "rain_prob": pop,
                "icon": f"https://openweathermap.org/img/wn/{icon_code}.png"
            })

            # 2. Safety Calculations (Prioritize first 24h / 8 blocks for safety logic)
            if i < 8: 
                if 'rain' in item and '3h' in item['rain']:
                    total_rain_24h += item['rain']['3h']
                if pop > 60:
                    high_pop_count += 1
            
        # --- THE DECISION LOGIC (Based on first 24h risk) ---
        if total_rain_24h > 5.0:
            return False, f"Heavy Rain ({total_rain_24h:.1f}mm) expected in next 24hrs.", forecast_display

        if high_pop_count >= 6:
            return False, "Continuous rain expected all day. Soil saturation risk.", forecast_display

        return True, None, forecast_display
        
    except Exception as e:
        print(f"Forecast Check Error: {e}")
        return True, None, [] # Fail safe

# --- ROUTES ---

@app.route("/", methods=["GET"])
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html", mode="auth")

@app.route("/scan", methods=["GET"])
def scan():
    return render_template("index.html", mode="scan", is_logged_in=('user' in session))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))

    db = get_db()
    cursor = db.execute(
        'SELECT * FROM history WHERE user_email = ? ORDER BY id DESC',
        (session['user'],)
    )
    return render_template("dashboard.html", user=session['user'], history=cursor.fetchall())

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# --- AUTH API ---
@app.route("/signup_api", methods=["POST"])
def signup_api():
    data = request.json
    try:
        db = get_db()
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)', (data.get("email"), data.get("password")))
        db.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists."})

@app.route("/login_api", methods=["POST"])
def login_api():
    data = request.json
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (data.get("email"),)).fetchone()
    if user and user['password'] == data.get("password"):
        session['user'] = user['email']
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials."})

# --- PROCESSING ---
# --- PROCESSING ---
@app.route("/processing", methods=["POST"])
def processing():
    # Initialize variables
    forecast_list = []
    duplicate_warning = False  # Default is False

    crop = request.form.get("crop", "").strip().upper()
    if crop == "CORN": crop = "MAIZE"

    state = request.form.get("state", "").strip().lower()
    city = request.form.get("city", "").strip()

    # --- LOCATION FIX ---
    if not state or not city:
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        if lat and lon:
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
                headers = {'User-Agent': 'EcoFertilizerApp/1.0'} 
                response = requests.get(url, headers=headers, timeout=5).json()
                address = response.get('address', {})
                state = address.get('state', '').lower()
                city = address.get('city', address.get('town', address.get('village', address.get('county', 'Unknown')))).strip()
            except Exception as e:
                print(f"Geocoding Error: {e}")
                state = "unknown"
                city = "Unknown"

    acres = float(request.form.get("acres", 1))
    price_n = float(request.form.get("price_n", 0))
    price_p = float(request.form.get("price_p", 0))
    price_k = float(request.form.get("price_k", 0))

    manual_temp = request.form.get("manual_temp", "").strip()
    manual_humid = request.form.get("manual_humid", "").strip()
    manual_rain = request.form.get("manual_rain", "").strip()

    # ==========================================================
    #  DUPLICATE CHECK LOGIC (Must be logged in)
    # ==========================================================
    if 'user' in session:
        try:
            today = datetime.date.today().strftime("%Y-%m-%d")
            db = get_db()
            # Check specifically for this user, city, crop, and date
            check = db.execute(
                'SELECT id FROM history WHERE user_email=? AND city=? AND crop=? AND date_applied=?',
                (session['user'], city, crop, today)
            ).fetchone()
            
            if check:
                duplicate_warning = True 
                print(f"DUPLICATE DETECTED for {session['user']} on {today}") # Debugging
        except Exception as e:
            print(f"Duplicate Check Error: {e}")

    # Check Zone Validity
    if state in AGRO_ZONES and crop not in AGRO_ZONES[state]:
        return render_template("alert.html",
                               alert_type="zone_mismatch",
                               city=city,
                               state=state.title(),
                               crop=crop,
                               is_logged_in=('user' in session))

    CALL_SUCCESS = [0]
    temperature = humidity = rainfall = 0
    weather_desc = "Unavailable"
    SEVEN_DAYS = []

    if manual_temp and manual_humid and manual_rain:
        temperature = float(manual_temp)
        humidity = float(manual_humid)
        rainfall = float(manual_rain)
        CALL_SUCCESS = [1]
        weather_desc = "Manual Input"
    else:
        is_safe, unsafe_reason, forecast_list = check_forecast_safety(city, OPENWEATHER_API_KEY)
        
        if not is_safe:
            return render_template("alert.html",
                                   alert_type="forecast_unsafe",
                                   city=city,
                                   state=state,
                                   reason=unsafe_reason,
                                   crop=crop,
                                   forecast=forecast_list,
                                   is_logged_in=('user' in session))

        bttf = BestTimeToFertilize(city_name=city, state_name=state)
        bttf.api_caller()
        if bttf.is_api_call_success():
            CALL_SUCCESS = [1]
            weather = bttf.weather_data
            temperature = weather["main"]["temp"]
            humidity = weather["main"]["humidity"]
            rainfall = weather.get("rain", {}).get("1h", 0)
            SEVEN_DAYS = bttf.seven_day_forecast()

    NPK = [{"Label_N": 0, "Label_P": 0, "Label_K": 0}]
    render_type = "alert"
    total_cost = None

    if CALL_SUCCESS[0] == 1:
        if rainfall >= 150:
            return render_template("alert.html",
                                   alert_type="heavy_rain",
                                   city=city,
                                   state=state,
                                   crop=crop,
                                   rainfall=rainfall,
                                   is_logged_in=('user' in session))

        render_type = "recommendation"
        prediction = npk_estimator.get_npk_values(
            crop=crop.lower(),
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall
        )
        NPK = [prediction]

        if temperature < 10:
            NPK[0]["Label_P"] = int(NPK[0]["Label_P"] * 1.2)
        elif temperature > 35:
            NPK[0]["Label_N"] = int(NPK[0]["Label_N"] * 0.8)

        total_cost = round(
            (NPK[0]["Label_N"] * acres * price_n) +
            (NPK[0]["Label_P"] * acres * price_p) +
            (NPK[0]["Label_K"] * acres * price_k), 2
        )

    return render_template(
        "update.html",
        CALL_SUCCESS=CALL_SUCCESS,
        render_type=render_type,
        NPK=NPK,
        SEVEN_DAYS=SEVEN_DAYS,
        weather_desc=weather_desc,
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        city=city,
        state=state,
        crop=crop,
        acres=acres,
        total_cost=total_cost,
        forecast=forecast_list,
        duplicate_warning=duplicate_warning, # Passing the flag!
        is_logged_in=('user' in session)
    )
# --- SAVE RECORD API ---
@app.route("/record_application", methods=["POST"])
def record_application():
    if 'user' not in session:
        return jsonify({"success": False})

    data = request.json
    today = datetime.date.today().strftime("%Y-%m-%d")

    if 'status' in data:
        npk_str = data['status']
    else:
        npk_str = f"N:{data['N']} P:{data['P']} K:{data['K']}"

    db = get_db()
    check = db.execute(
        'SELECT * FROM history WHERE user_email=? AND city=? AND crop=? AND date_applied=?',
        (session['user'], data['city'], data['crop'], today)
    ).fetchone()

    if not check:
        db.execute(
            '''INSERT INTO history
               (user_email, state, city, crop, acres, cost, date_applied, npk_values)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                session['user'],
                data['state'],
                data['city'],
                data['crop'],
                data.get("acres", 0),
                data.get("cost", 0),
                today,
                npk_str
            )
        )
        db.commit()

    return jsonify({"success": True})

# ==========================================
#   SECURE DELETE API
# ==========================================
@app.route("/secure_delete", methods=["POST"])
def secure_delete():
    if 'user' not in session:
        return jsonify({"success": False})

    data = request.json
    db = get_db()

    user_record = db.execute('SELECT * FROM users WHERE email = ?', (data.get("email"),)).fetchone()
    if not user_record or user_record['password'] != data.get("password"):
        return jsonify({"success": False, "message": "Incorrect Password."})

    if data.get("email") != session['user']:
        return jsonify({"success": False, "message": "Email mismatch."})

    if str(data.get("target")) == "all":
        db.execute('DELETE FROM history WHERE user_email = ?', (session['user'],))
    else:
        db.execute('DELETE FROM history WHERE id = ? AND user_email = ?', (int(data.get("target")), session['user']))

    db.commit()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)