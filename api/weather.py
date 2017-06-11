import json, requests, os

def weather_init():
    weather_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.json')
    json_data = open(weather_file, 'r+') if os.path.exists(weather_file) else open(weather_file, 'w+')

    return (json_data, weather_file)

def config_init():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    config_data = open(config_file, 'r+')
    config_weather = json.load(config_data)['weather']

    return config_weather

def get_weather():
    json_data, weather_file = weather_init()

    if os.stat(weather_file).st_size > 0 :
        print("get weather json from json file")
        weather = json.load(json_data)
    else:
        weather = update_weather()
    conditions = weather["conditions"]["current_observation"]
    forecast_10day = weather["forecast10day"]["forecast"]["simpleforecast"]["forecastday"]
    weather_details = {
        "conditions" : {
          "location" : conditions["display_location"]["full"],
          "weather" : conditions["weather"],
          "icon_url" : conditions["icon_url"],
          "temp_c" : conditions["temp_c"],
          "feelslike_c" : conditions["feelslike_c"],
          "temp_f" : conditions["temp_f"],
          "feelslike_f" : conditions["feelslike_f"],
          "wind_kph" : conditions["wind_kph"],
          "wind_dir": conditions["wind_dir"],
          "pressure_mb" : conditions["pressure_mb"],
          "visibility_km" : conditions["visibility_km"],
          "dewpoint_c" : conditions["dewpoint_c"],
          "relative_humidity" : conditions["relative_humidity"]
        },
        "forecast_6day" : [ forecast_10day[1:4], forecast_10day[5:8] ]
     }
    return weather_details

def update_weather(default = False):
    print("get weather json from weather site")

    config_weather = config_init()
    json_data = weather_init()[0]

    weather = json.load(json_data)
    url_list = ['conditions', 'forecast10day']

    if not default:
        for request in url_list:
            url = "http://api.wunderground.com/api/{0}/{1}/q/{2}.json".format(config_weather['api_key'], request, config_weather['location'])
            weather[request] = requests.get(url).json()

    else:
        request = url_list[0]
        url = "http://api.wunderground.com/api/{0}/{1}/q/{2}.json".format(config_weather['api_key'], request, config_weather['location'])
        weather[request] = requests.get(url).json()

    json_data.seek(0)
    json_data.truncate()
    json.dump(weather, json_data, indent= 4)

    return weather
