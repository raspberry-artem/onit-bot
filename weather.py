import requests

CONST_URL = 'https://geocode-maps.yandex.ru/1.x/?'


class weather:
    def __init__(self, apikey, url=CONST_URL):
        self.apikey = apikey
        self.url = url

    def get_coordinates(self, place):
        res = requests.get(self.url, params=dict(apikey=self.apikey, geocode=place, format='json')).json()
        if res['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == '0':
            result = {'existence': False}
            return result
        else:
            position = res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            lon, lat = [float(i) for i in position.split()]
            current_location = res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            result = {'existence': True, 'lon': lon, 'lat': lat, 'location': current_location}
            return result

    def get_place(self, lat, lon):
        res = requests.get(self.url, params=dict(apikey=self.apikey, geocode=str(lat) + ', ' + str(lon), sco='latlong',
                                            format='json')).json()
        current_location = res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['text']
        result = {'existence': True, 'location': current_location}
        return result

