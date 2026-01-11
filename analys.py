
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def create_weather_df():
    # --------------------------------------------------------------------------------------------------------
    # Генерирует синтетический датасет погодных данных для тестирования анализа.
    # Создаёт реалистичные температуры по сезонам для 15 городов за 10 лет.
    
    # Параметры:
    # ----------
    # Нет (генерирует фиксированный датасет)
    
    # Логика:
    # --------
    # * 15 городов с реальными сезонными температурами
    # * 10 лет ежедневных данных (3650 дней на город)
    # * Температуры ~ N(сезонная_ср, σ=5°C)
    # * Сезоны: winter(12-2), spring(3-5), summer(6-8), autumn(9-11)
    
    # Возвращает:
    # --------
    # pd.DataFrame
    #     * city - город (15 вариантов)
    #     * timestamp - дата (2010-01-01 по 365*10 дней)
    #     * temperature - температура °C (нормальное распределение)
    #     * season - сезон (winter/spring/summer/autumn)
    
    # Использование:
    # weather_df = create_weather_df()
    # print(weather_df.head())
    # --------------------------------------------------------------------------------------------------------

    # Реальные средние температуры (примерные данные) для городов по сезонам
    seasonal_temperatures = {
        "New York": {"winter": 0, "spring": 10, "summer": 25, "autumn": 15},
        "London": {"winter": 5, "spring": 11, "summer": 18, "autumn": 12},
        "Paris": {"winter": 4, "spring": 12, "summer": 20, "autumn": 13},
        "Tokyo": {"winter": 6, "spring": 15, "summer": 27, "autumn": 18},
        "Moscow": {"winter": -10, "spring": 5, "summer": 18, "autumn": 8},
        "Sydney": {"winter": 12, "spring": 18, "summer": 25, "autumn": 20},
        "Berlin": {"winter": 0, "spring": 10, "summer": 20, "autumn": 11},
        "Beijing": {"winter": -2, "spring": 13, "summer": 27, "autumn": 16},
        "Rio de Janeiro": {"winter": 20, "spring": 25, "summer": 30, "autumn": 25},
        "Dubai": {"winter": 20, "spring": 30, "summer": 40, "autumn": 30},
        "Los Angeles": {"winter": 15, "spring": 18, "summer": 25, "autumn": 20},
        "Singapore": {"winter": 27, "spring": 28, "summer": 28, "autumn": 27},
        "Mumbai": {"winter": 25, "spring": 30, "summer": 35, "autumn": 30},
        "Cairo": {"winter": 15, "spring": 25, "summer": 35, "autumn": 25},
        "Mexico City": {"winter": 12, "spring": 18, "summer": 20, "autumn": 15},
    }

    # Сопоставление месяцев с сезонами
    month_to_season = {12: "winter", 1: "winter", 2: "winter",
                    3: "spring", 4: "spring", 5: "spring",
                    6: "summer", 7: "summer", 8: "summer",
                    9: "autumn", 10: "autumn", 11: "autumn"}

    # Генерация данных о температуре
    def generate_realistic_temperature_data(cities, num_years=10):
        dates = pd.date_range(start="2010-01-01", periods=365 * num_years, freq="D")
        data = []

        for city in cities:
            for date in dates:
                season = month_to_season[date.month]
                mean_temp = seasonal_temperatures[city][season]
                # Добавляем случайное отклонение
                temperature = np.random.normal(loc=mean_temp, scale=5)
                data.append({"city": city, "timestamp": date, "temperature": temperature})

        df = pd.DataFrame(data)
        df['season'] = df['timestamp'].dt.month.map(lambda x: month_to_season[x])
        return df

    # Генерация данных
    data = generate_realistic_temperature_data(list(seasonal_temperatures.keys()))
    return data



def create_historical_forecast_dataset(weather_df):
    # --------------------------------------------------------------------------------------------------------
    # Преобразует сырые данные погоды в исторический датасет со статистиками.
    
    # Параметры:
    # ----------
    # weather_df : pd.DataFrame
    #     Исходные данные с колонками:
    #     * 'city' - название города
    #     * 'timestamp' - дата (строка или datetime)
    #     * 'temperature' - температура
    #     * 'season' - сезон ('winter', 'spring', 'summer', 'autumn')
    
    
    # Возвращает:
    # --------
    # pd.DataFrame
    #     Агрегированные статистики по каждому городу и дню года:
    #     * city - город
    #     * day_of_year - день года (1-365)
    #     * month - месяц (1-12)
    #     * season - сезон
    #     * historical_mean - ср. температура по дню года
    #     * historical_std - стд. откл. по дню года
    #     *  ma_2, ma_4, ma_7, ma_30 - скользящие средние
    #     * ma_*_mean - ср. скользящие средние (если есть в данных)
    #     * ma_all_mean - ср. всех ma_*_mean
    #     * month_mean - ср. по месяцу
    #     * season_mean - ср. по сезону
    #     * tunnel_upper/lower - границы "нормального туннеля" (±2σ от ma_30)
    # Использование:
    # forecast_stats = create_historical_forecast_dataset(weather_df)
    # --------------------------------------------------------------------------------------------------------

    # Вычисление скользящего среднего и стандартного отклонения для сглаживания температурных колебаний.
    # Вычисление скользящих средних.
    windows = [2, 4, 7, 30]  # Размер окна для скользящего среднего.
    weather_df = weather_df.sort_values(['city', 'season', 'timestamp'])

    for window in windows:
        weather_df[f'ma_{window}'] = (
            weather_df
            .groupby(['city', 'season'])['temperature']
            .transform(lambda s: s.rolling(window=window, min_periods=1).mean())
        )
        weather_df[f'std_{window}'] = (
            weather_df
            .groupby(['city', 'season'])['temperature']
            .transform(lambda s: s.rolling(window=window, min_periods=1).std())
        )
    
    # Определение аномалий на основе отклонений температуры от скользящее среднее±2𝜎.
    k = 2  # коэффициент при 𝜎 = 1

    weather_df['upper_30'] = weather_df['ma_30'] + k * weather_df['std_30']
    weather_df['lower_30'] = weather_df['ma_30'] - k * weather_df['std_30']
    weather_df['is_anomaly_30'] = ((weather_df['temperature'] > weather_df['upper_30']) |(weather_df['temperature'] < weather_df['lower_30']))
    
    # Приводим timestamp к datetime
    df = weather_df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Аномалии
    anomalies_summary = (
        df
        .groupby(['city', 'season'])['is_anomaly_30']
        .agg([
            'count',           # общее количество дней в сезон
            'sum',             # количество аномалий
            lambda x: x.sum() / x.count()  # доля аномалий (%)
        ])
        .round(4)
    )

    anomalies_summary.columns = ['total_days', 'anomaly_count', 'anomaly_rate']
    anomalies_summary = anomalies_summary.reset_index()
    
    # День года + месяц
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year

    
    stats = []
    
    print("Обработка городов...")
    for i, city in enumerate(df['city'].unique()):
        if i % 5 == 0:
            print(f"Город {i+1}/{len(df['city'].unique())}: {city}")
            
        df_city = df[df['city'] == city]
        
        for doy in range(1, 366):
            day_data = df_city[df_city['day_of_year'] == doy]
            if len(day_data) == 0:
                continue
                
            season = day_data['season'].iloc[0]
            month = day_data['month'].iloc[0]
            year = day_data['year'].iloc[0]
            
            # База
            mean_temp = day_data['temperature'].mean()
            std_temp = day_data['temperature'].std()
            
            # ma
            ma_stats = {}
            for w in [2, 4, 7, 30]:
                if f'ma_{w}' in day_data.columns:
                    ma_stats[f'ma_{w}_mean'] = day_data[f'ma_{w}'].mean()
            
            ma_all = np.mean(list(ma_stats.values())) if ma_stats else np.nan
            
        
            month_mean = df_city[df_city['month'] == month]['temperature'].mean()
            season_mean = df_city[df_city['season'] == season]['temperature'].mean()
            
            # ma ±2σ (ma_30 как основной)
            tunnel_upper = ma_stats.get('ma_30_mean', mean_temp) + 2 * std_temp
            tunnel_lower = ma_stats.get('ma_30_mean', mean_temp) - 2 * std_temp
            
            stats.append({
                'city': city,
                'year': year,
                'season': season,
                'month': month,
                'day_of_year': doy,
                'historical_mean': mean_temp,
                'historical_std': std_temp,
                **ma_stats,
                'ma_all_mean': ma_all,
                'month_mean': month_mean,
                'season_mean': season_mean,
                'tunnel_upper': tunnel_upper,
                'tunnel_lower': tunnel_lower
            })
    
    result_df = pd.DataFrame(stats)
    print(f"Создано {len(result_df)} записей")
    # ДОБАВИТЬ ЭТУ СТРОКУ:
    result_df['city_ru'] = result_df['city']  # Сохраняем для совместимости
    return anomalies_summary, result_df

def plot_city_seasonal_ma(df, city):
    # --------------------------------------------------------------------------------------------------------
    # Интерактивная визуализация скользящих средних температуры по сезонам для города.
    # Построение графика с выпадающим меню переключения окон MA.
    
    # Параметры:
    # ----------
    # df : pd.DataFrame
    #     Данные для визуализации с колонками:
    #     * 'timestamp' - datetime
    #     * 'temperature' - температура
    #     * ma_2, ma_4, ma_7, ma_30 - скользящие средние (обязательно)
    #     * std_2, std_4, std_7, std_30 - стандартные отклонения MA
    # city : str
    #     Название города из df['city']
    
    # Визуализация:
    # --------
    # Plotly Figure:
    # * Чёрная линия - исходная температура
    # * Цветные линии MA (2d=синий, 4d=оранжевый, 7d=зелёный, 30d=красный)
    # * Заливка ±σ для выбранного окна (прозрачность 20%)
    # * Выпадающее меню: Window 2d/4d/7d/30d
    # * Hover с точными значениями
    # * Полная временная шкала города
    
    # Использование:
    # plot_city_seasonal_ma(weather_df, 'Moscow')
    # --------------------------------------------------------------------------------------------------------
    # Код создан с помощью Perplexity AI

    df_city = (df[df['city'] == city]
               .sort_values('timestamp'))

    windows = [2, 4, 7, 30]
    colors_rgb = ['rgb(0,100,255)', 'rgb(255,165,0)', 'rgb(0,128,0)', 'rgb(255,0,0)']

    fig = go.Figure()

    # температура
    fig.add_trace(go.Scatter(x=df_city['timestamp'], y=df_city['temperature'],
                             mode='lines', name='Temperature',
                             line=dict(color='black', width=1),
                             hovertemplate='<b>%{x}</b><br>Temp: %{y:.1f}°C<extra></extra>'))

    for i, w in enumerate(windows):
        ma_col = f'ma_{w}'
        std_col = f'std_{w}'

        # MA линия
        fig.add_trace(go.Scatter(x=df_city['timestamp'], y=df_city[ma_col],
                                 mode='lines', name=f'MA {w}d (seasonal)',
                                 line=dict(color=colors_rgb[i], width=2),
                                 visible=(w == 30)))

        # +σ пунктир
        fig.add_trace(go.Scatter(x=df_city['timestamp'],
                                 y=df_city[ma_col] + df_city[std_col],
                                 mode='lines', line=dict(color=colors_rgb[i], width=1, dash='dash'),
                                 showlegend=False, visible=(w == 30)))

        # -σ заливка (ПОЛНЫЙ RGBA)
        fig.add_trace(go.Scatter(x=df_city['timestamp'],
                                 y=df_city[ma_col] - df_city[std_col],
                                 fill='tonexty',
                                 fillcolor=colors_rgb[i].replace('rgb', 'rgba').replace(')', ',0.2)'),
                                 line=dict(color='rgba(0,0,0,0)'),
                                 showlegend=False, visible=(w == 30)))

    # выпадающее меню
    buttons = []
    num_windows = len(windows)
    for i, w in enumerate(windows):
        visible = [True]  # температура всегда видна
        for j in range(num_windows):
            if j == i:
                visible.extend([True, True, True])  # MA, +σ, -σ для текущего окна
            else:
                visible.extend([False, False, False])
        buttons.append(dict(label=f"Window {w}d", method="update", args=[{"visible": visible}]))

    fig.update_layout(
        updatemenus=[dict(type="dropdown", buttons=buttons,
                          direction="down", showactive=True, x=0.01, y=1.1)],
        title=f"{city}: Seasonal Rolling Windows (Full Timeline)",
        xaxis_title="Date", yaxis_title="Temperature, °C",
        height=500
    )
    fig.show()
def mean_years_temp_from_season(df, city, season):
    """
    Статистики по одному городу, за один сезон 
    (средняя температура, средние MA, средние туннели за ВСЕ годы)
    
    Параметры:
    ----------
    df : pd.DataFrame (forecast_stats)
    city : str
    season : str ('winter', 'spring', 'summer', 'autumn')
    
    Возвращает:
    --------
    dict с ключами:
    * mean_temp, std_temp
    * ma_2_mean, ma_4_mean, ma_7_mean, ma_30_mean
    * tunnel_upper, tunnel_lower
    * month_means (dict по месяцам)
    """
    # Фильтруем город + сезон
    city_df = df[(df['city'] == city) & (df['season'] == season)].copy()
    
    if city_df.empty:
        return {"error": f"Нет данных для {city} {season}"}
    
    # 1. Базовые статистики
    mean_temp = city_df['historical_mean'].mean()
    std_temp = city_df['historical_std'].mean()
    
    # 2. Средние скользящие средние
    ma_stats = {}
    for w in [2, 4, 7, 30]:
        col = f'ma_{w}_mean'
        if col in city_df.columns:
            ma_stats[col] = city_df[col].mean()
    
    # 3. Средние туннели
    tunnel_upper = city_df['tunnel_upper'].mean()
    tunnel_lower = city_df['tunnel_lower'].mean()
    
    # 4. Средние по месяцам
    month_means = city_df.groupby('month')['historical_mean'].mean().to_dict()
    
    # 5. Кол-во дней в сезоне
    total_days = len(city_df)
    
    return {
        'city': city,
        'season': season,
        'total_days': total_days,
        'mean_temp': round(mean_temp, 1),
        'std_temp': round(std_temp, 1),
        **ma_stats,
        'tunnel_upper': round(tunnel_upper, 1),
        'tunnel_lower': round(tunnel_lower, 1),
        'month_means': {k: round(v, 1) for k, v in month_means.items()}
    }


