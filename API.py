import requests
import pandas as pd

def get_current_weather(city_ru, api_key):
    try:
        coords_df = pd.read_csv('city_coordinates.csv')
        city_coords = coords_df[coords_df['ru'] == city_ru]
        
        if city_coords.empty:
            print(f"Город {city_ru} не найден!")  # только для терминала
            return None
            
        city_en = city_coords['Город (EN)'].iloc[0]
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # ОБРАБОТКА 401
        if data.get('cod') == 401:
            print("Invalid API key!")  # для терминала
            return None
            
        if response.status_code == 200:
            temp = data['main']['temp']
            print(f"{city_ru}: {temp}°C")  # для терминала
            return temp
        else:
            print(f"API Error {response.status_code}: {data}")
            return None
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
