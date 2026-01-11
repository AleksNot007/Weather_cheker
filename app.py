# app.py

import streamlit as st
import pandas as pd
from API import get_current_weather
from analys import create_historical_forecast_dataset, plot_city_seasonal_ma, mean_years_temp_from_season
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

if 'weather_shown' not in st.session_state:
    st.session_state.weather_shown = False
st.set_page_config(page_title="Анализатор погоды", layout="wide")

st.title("🌤️ Сравнение погоды с историческими данными")

# 1. Загрузка исторических данных
uploaded_file = st.file_uploader("Загрузите CSV с историческими данными", type=['csv'])
if uploaded_file is not None:
    forecast_dataset = pd.read_csv(uploaded_file)
    forecast_dataset['timestamp'] = pd.to_datetime(forecast_dataset['timestamp'])
    st.success(f"✅ Загружено {len(forecast_dataset):,} записей")
    
    # 2. Координаты городов
    coords_df = pd.read_csv('https://github.com/AleksNot007/Weather_cheker/blob/main/city_coordinates.csv')
    selected_city_ru = st.selectbox("Выберите город", coords_df['ru'].tolist())
    selected_city_en = coords_df[coords_df['ru'] == selected_city_ru]['Город (EN)'].iloc[0]
    
    # 3. API ключ
    st.info("📝 Введите API ключ")
    api_key = st.text_input("API ключ OpenWeatherMap", help="https://openweathermap.org/api")
    
    # 4. Получение текущей погоды
    current_temp = None
    if api_key:
        current_temp = get_current_weather(selected_city_ru, api_key)
        
        if current_temp is not None:
            st.metric("🌤️ Температура сейчас", f"{current_temp:.1f}°C")

        else:
            st.error("❌ Ошибка API: неверный ключ или город не найден")
            st.info("Проверьте: 1) API ключ 2) город в city_coordinates.csv")
    else:
        st.info("🔑 Введите API ключ для текущей погоды")
    
    
    #5. Получение результатов (норм./не норм. погода)
    anomalies, forecast_stats_df = create_historical_forecast_dataset(forecast_dataset)
    today = pd.Timestamp(date.today())
    today_month = today.month  

    if today_month in [12, 1, 2]:     
        today_season = 'winter'
    elif today_month in [3, 4, 5]:
        today_season = 'spring'
    elif today_month in [6, 7, 8]:
        today_season = 'summer'
    else:
        today_season = 'autumn'


    city_stats = mean_years_temp_from_season(forecast_stats_df, selected_city_en, today_season)
    def check_weather(temp, city_stats, city_ru, today_season):
        """Проверка погоды"""
        col1, col2 = st.columns(2)
        
        with col1:
            lower_bound = city_stats['tunnel_lower']
            upper_bound = city_stats['tunnel_upper']
            status = "✅ Норма" if lower_bound <= temp <= upper_bound else "❌ Аномалия"
            st.metric("Статус", status)
        
        with col2:
            st.metric("Туннель", f"{lower_bound:.1f}° ↔ {upper_bound:.1f}°")
        
        st.subheader(f"📊 {city_ru} — {today_season}")
        st.json({
            'Дней в сезоне': city_stats['total_days'],
            'Средняя T°': f"{city_stats['mean_temp']:.1f}°C",
            'MA 30d': f"{city_stats.get('ma_30_mean', 'N/A'):.1f}°C"
        })

    # ✅ ПРАВИЛЬНЫЙ вызов (в самом конце):
    if current_temp is not None and not city_stats.get('error'):
        day_of_year = today.dayofyear
        check_weather(current_temp, city_stats, selected_city_ru, today_season)
     



    

