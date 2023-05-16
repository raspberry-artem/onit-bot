import requests

CONST_URL = 'http://api.openweathermap.org/data/2.5/{method}'


class OpenWeather:
    def __init__(self, apikey, url=CONST_URL):
        self.url = url
        self.apikey = apikey

    def weather(self, lat, lon, units='metric', lang='ru'):
        res = requests.get(self.url.format(method='weather'), params={'appid': self.apikey, 'lat': lat,
                                                     'lon': lon, 'units': units, 'lang': lang})
        return res.json()

