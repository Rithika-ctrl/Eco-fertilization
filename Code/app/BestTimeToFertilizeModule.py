import requests


class BestTimeToFertilize:

    def __init__(self, city_name, state_name):
        self.city = city_name
        self.state = state_name
        self.weather_data = {}
        self.daily_forecast = []
        self.api_success = False

    # --------------------------------------------------
    # FETCH WEATHER + FORECAST
    # --------------------------------------------------
    def api_caller(self):

        API_KEY = "a2b002602129dc21ab0935cab87ef027"

        print("🌍 Weather API HIT for city:", self.city)

        current_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={self.city},IN&appid={API_KEY}&units=metric"
        )

        try:
            response = requests.get(current_url, timeout=10)
            data = response.json()

            print("RAW CURRENT WEATHER →", data)

            if "main" not in data:
                self.api_success = False
                return

            self.weather_data = data

            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/onecall"
                f"?lat={lat}&lon={lon}"
                f"&exclude=minutely,hourly,alerts"
                f"&appid={API_KEY}&units=metric"
            )

            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_data = forecast_response.json()

            print("RAW 7-DAY FORECAST →", forecast_data)

            self.daily_forecast = forecast_data.get("daily", [])

            self.api_success = True
            print("✅ Weather API SUCCESS")

        except Exception as e:
            print("❌ WEATHER API ERROR:", e)
            self.api_success = False

    # --------------------------------------------------
    def is_api_call_success(self):
        return self.api_success

    # --------------------------------------------------
    def best_time_fertilize(self):

        if not self.api_success:
            return ("error", "Weather Error", "Unable to fetch weather data")

        temp = self.weather_data["main"]["temp"]
        humidity = self.weather_data["main"]["humidity"]
        rainfall = self.weather_data.get("rain", {}).get("1h", 0)

        print("TODAY WEATHER →", temp, humidity, rainfall)

        if rainfall >= 200:
            return ("danger", "Not Favorable", "Heavy rainfall detected")

        elif temp < 15:
            return ("warning", "Caution", "Low temperature detected")

        else:
            return ("safe", "Optimal", "Safe to fertilize today")

    # --------------------------------------------------
    def seven_day_forecast(self):

        forecast = []

        if not self.api_success:
            return forecast

        for i in range(min(7, len(self.daily_forecast))):
            rain = self.daily_forecast[i].get("rain", 0)

            if rain >= 200:
                status = "Not Favorable"
            elif rain >= 80:
                status = "Moderate"
            else:
                status = "Favorable"

            forecast.append({
                "Day": f"Day {i+1}",
                "Status": status
            })

        print("7-DAY FERTILIZER FORECAST →", forecast)
        return forecast
