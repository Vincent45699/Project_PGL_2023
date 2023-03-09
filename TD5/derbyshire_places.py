import requests

response = requests.get('https://opendomesday.org/api/1.0/county/dby/')

data = response.json()

place_ids = [place['id'] for place in data['places_in_county']]

print(place_ids)
