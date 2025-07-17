import requests
from django.shortcuts import render
from .forms import CityForm
from datetime import datetime

def get_weather_data(city):
    API_KEY = 'b171184711284c58957115337251607'
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3"
    response = requests.get(url)
    return response.json()

def classify_weather(desc):
    desc = desc.lower()
    if "sun" in desc or "clear" in desc:
        return "sunny"
    elif "cloud" in desc:
        return "cloudy"
    elif "rain" in desc:
        return "rain"
    else:
        return "default"

def home(request):
    form = CityForm()
    weather_data = None
    error = None

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city'].strip()
            data = get_weather_data(city)

            if "error" not in data:
                current = data['current']
                location = data['location']
                forecast_days = data['forecast']['forecastday']
                desc = current['condition']['text']

                weather_data = {
                    'city': location['name'],
                    'country': location['country'],
                    'temperature': current['temp_c'],
                    'description': desc,
                    'icon': current['condition']['icon'],
                    'wind': current['wind_kph'],
                    'weather_class': classify_weather(desc),
                    'forecast': []
                }

                for day in forecast_days:
                    weather_data['forecast'].append({
                        'date': datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A, %b %d'),
                        'icon': day['day']['condition']['icon'],
                        'temp': day['day']['avgtemp_c'],
                        'description': day['day']['condition']['text']
                    })
            else:
                error = f"City not found! ({data.get('error', {}).get('message', 'Unknown error')})"

    return render(request, 'weather.html', {
        'form': form,
        'weather': weather_data,
        'error': error,
        'now': datetime.now()
    })
