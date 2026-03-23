import requests
from langchain_core.tools import tool
from utils.config_handler import weather_conf
from utils.logger_handler import logger

# 预定义的 WMO 天气代码映射
WMO_CODE_MAP = {
    0: "晴朗", 1: "多云", 2: "阴天", 3: "阴天",
    45: "雾", 48: "雾冻", 
    51: "毛毛雨", 53: "毛毛雨", 55: "密集毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "阵雨", 82: "暴雨",
    95: "雷风暴", 96: "雷风暴伴冰雹", 99: "雷风暴伴重冰雹"
}

def _get_coordinates(city: str) -> tuple:
    """内部辅助函数：获取城市经纬度"""
    try:
        url = weather_conf["geocoding"]["url"]
        timeout = weather_conf["geocoding"]["timeout"]
        params = {
            "name": city,
            "count": 1,
            "language": "zh",
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            return lat, lon
        return None, None
    except Exception as e:
        logger.error(f"[WeatherTool] 获取{city}坐标失败: {e}")
        return None, None


@tool(description="获取指定城市当前的实时天气，以消息字符串的形式返回，包含气温、体感温度、湿度、风速、气压等")
def get_current_weather(city: str) -> str:
    """获取当前天气详细信息"""
    lat, lon = _get_coordinates(city)
    if lat is None:
        return f"无法获取 {city} 的位置信息，请检查城市名称是否正确。"
        
    try:
        url = weather_conf["weather"]["url"]
        timeout = weather_conf["weather"]["timeout"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,surface_pressure,wind_speed_10m",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
        temp = current["temperature_2m"]
        apparent_temp = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]
        pressure = current["surface_pressure"]
        precipitation = current["precipitation"]
        is_day = "白天" if current["is_day"] else "夜晚"
        
        weather_code = current["weather_code"]
        weather_desc = WMO_CODE_MAP.get(weather_code, "未知天气")
        
        result = f"【{city}当前实时天气 ({is_day})】\n"
        result += f"- 天气状况：{weather_desc}\n"
        result += f"- 实际气温：{temp}℃ (体感温度 {apparent_temp}℃)\n"
        result += f"- 空气湿度：{humidity}%\n"
        result += f"- 降水量：{precipitation}mm\n"
        result += f"- 风速：{wind_speed}km/h\n"
        result += f"- 气压：{pressure}hPa\n\n"
        
        result += "【扫地机清洁建议】"
        if humidity > 80 or precipitation > 0:
            result += " 当前湿度高或有降水。如果使用扫拖机器人，建议适当减少拖地出水量或开启强力风干模式，防止地面湿滑。同时注意检查门厅处是否有泥水带入，可设置重点清扫。"
        elif humidity < 30:
            result += " 空气较为干燥。可以正常使用扫拖机器人进行拖地，地面容易变干；但干燥环境容易起静电吸附灰尘，建议开启强力吸尘模式。"
        else:
            result += " 环境温湿度适宜，适合执行全局标准清扫任务。"
            
        return result
    except Exception as e:
        logger.error(f"[WeatherTool] 获取当前天气失败: {e}")
        return f"暂时无法获取 {city} 的实时天气数据，请稍后再试。"


@tool(description="获取指定城市过去几天的历史天气（最多支持前15天），以消息字符串的形式返回")
def get_history_weather(city: str, days: int) -> str:
    """获取历史天气信息"""
    days = min(days, 15)
    lat, lon = _get_coordinates(city)
    if lat is None:
        return f"无法获取 {city} 的位置信息，请检查城市名称是否正确。"
        
    try:
        url = weather_conf["weather"]["url"]
        timeout = weather_conf["weather"]["timeout"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "past_days": days,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        daily = data["daily"]
        times = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        precipitations = daily["precipitation_sum"]
        
        # 仅截取过去的天数（不包含今天）
        past_times = times[:days]
        avg_max_temp = round(sum(max_temps[:days]) / len(past_times), 1)
        avg_min_temp = round(sum(min_temps[:days]) / len(past_times), 1)
        total_precip = round(sum(precipitations[:days]), 1)
        
        rain_days = sum(1 for p in precipitations[:days] if p > 0)
        
        result = f"【{city}过去{days}天历史天气概况】\n"
        result += f"平均最高气温 {avg_max_temp}℃，平均最低气温 {avg_min_temp}℃。\n"
        result += f"总降水量 {total_precip}mm，其中有 {rain_days} 天出现降雨。\n"
        
        if rain_days > days / 2:
            result += "提示：过去一段时间降雨频繁，室内可能积聚较多湿气或泥沙，建议建议使用扫地机器人进行深度清洁和拖地。"
        else:
            result += "提示：过去一段时间天气相对干燥，适合扫地机器人的日常规律清洁。"
            
        return result
    except Exception as e:
        logger.error(f"[WeatherTool] 获取历史天气失败: {e}")
        return f"暂时无法获取 {city} 的历史天气数据，请稍后再试。"


@tool(description="获取指定城市未来几天的天气预报（最多支持后15天），以消息字符串的形式返回")
def get_forecast_weather(city: str, days: int) -> str:
    """获取未来天气预报"""
    days = min(days, 15)
    lat, lon = _get_coordinates(city)
    if lat is None:
        return f"无法获取 {city} 的位置信息，请检查城市名称是否正确。"
        
    try:
        url = weather_conf["weather"]["url"]
        timeout = weather_conf["weather"]["timeout"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "forecast_days": days,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        daily = data["daily"]
        times = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        precip_probs = daily["precipitation_probability_max"]
        
        forecast_lines = []
        high_prob_rain_days = 0
        
        for i in range(days):
            date = times[i]
            code = daily["weather_code"][i]
            desc = WMO_CODE_MAP.get(code, "未知")
            t_max = max_temps[i]
            t_min = min_temps[i]
            prob = precip_probs[i]
            
            forecast_lines.append(f"{date}: {desc}，气温 {t_min}~{t_max}℃，降水概率 {prob}%")
            if prob > 50:
                high_prob_rain_days += 1
                
        result = f"【{city}未来{days}天天气预报】\n" + "\n".join(forecast_lines) + "\n"
        
        if high_prob_rain_days > 0:
            result += f"\n建议：未来有 {high_prob_rain_days} 天降雨概率较高。雨天可能导致门厅处出现泥水脚印，可提前在扫拖机器人的 App 中设置门厅区域的「重点拖地」计划。"
        else:
            result += "\n建议：未来天气晴好，适合执行全局标准清扫任务。"
            
        return result
    except Exception as e:
        logger.error(f"[WeatherTool] 获取未来天气失败: {e}")
        return f"暂时无法获取 {city} 的未来天气数据，请稍后再试。"


@tool(description="获取指定城市当前的空气质量（包括AQI、PM2.5、PM10、臭氧等），以消息字符串的形式返回，评估灰尘和开窗通风情况")
def get_air_quality(city: str) -> str:
    """获取详细空气质量信息，结合扫地机器人给出建议"""
    lat, lon = _get_coordinates(city)
    if lat is None:
        return f"无法获取 {city} 的位置信息，请检查城市名称是否正确。"
        
    try:
        url = weather_conf["air_quality"]["url"]
        timeout = weather_conf["air_quality"]["timeout"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,dust",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
        aqi = current.get("european_aqi", "未知")
        pm2_5 = current.get("pm2_5", 0)
        pm10 = current.get("pm10", 0)
        ozone = current.get("ozone", 0)
        dust = current.get("dust", 0)
        
        result = f"【{city}当前空气质量详情】\n"
        result += f"- 欧洲AQI指数：{aqi} (数值越大空气越差)\n"
        result += f"- PM2.5浓度：{pm2_5} μg/m³\n"
        result += f"- PM10浓度：{pm10} μg/m³\n"
        result += f"- 臭氧(O3)浓度：{ozone} μg/m³\n"
        result += f"- 浮尘浓度：{dust} μg/m³\n\n"
        
        result += "【扫地机与环境建议】"
        if pm10 > 100 or pm2_5 > 75 or dust > 50:
            result += " 空气质量较差或浮尘较多，室外灰尘极易进入室内。强烈建议关闭门窗，开启扫地机器人的「强力吸尘」模式，并缩短主刷和 HEPA 滤网的清理/更换周期，以防滤网堵塞影响吸力。"
        elif pm10 < 50 and pm2_5 < 35:
            result += " 空气质量优良，室内落灰较少。建议开窗通风，扫地机器人可以使用「安静/标准」模式进行日常节能清扫。"
        else:
            result += " 空气质量中等，按日常常规设置清扫即可，适度通风。"
            
        return result
    except Exception as e:
        logger.error(f"[WeatherTool] 获取空气质量失败: {e}")
        return f"暂时无法获取 {city} 的空气质量数据，请稍后再试。"


@tool(description="获取指定城市当前的气象灾害预警信息（如暴雨、台风、大风、冰雹等），以消息字符串的形式返回，用于判断是否需要采取紧急设备保护措施")
def get_weather_alerts(city: str) -> str:
    """获取气象灾害预警信息，结合扫地机器人给出安全建议"""
    lat, lon = _get_coordinates(city)
    if lat is None:
        return f"无法获取 {city} 的位置信息，请检查城市名称是否正确。"
        
    # Open-Meteo 目前没有全球完善的 Alert API，这里使用模拟逻辑，但保留真实的接口框架
    # 实际生产中可替换为和风天气或国家气象局的灾害预警 API
    try:
        url = weather_conf["weather"]["url"]
        timeout = weather_conf["weather"]["timeout"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "weather_code,wind_speed_10m,precipitation",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]
        precipitation = current["precipitation"]
        
        alerts = []
        if weather_code in [82, 95, 96, 99] or precipitation > 10:
            alerts.append("暴雨/雷暴预警：当前存在强降水或雷暴天气。")
        if wind_speed > 40:
            alerts.append(f"大风预警：当前风速高达 {wind_speed}km/h。")
        if weather_code in [71, 73, 75]:
            alerts.append("暴雪/冰冻预警：当前存在降雪天气。")
            
        if not alerts:
            return f"【{city}气象预警】当前无极端气象灾害预警，扫地机器人可安全运行。"
            
        result = f"【{city}气象预警】注意：\n" + "\n".join([f"- {a}" for a in alerts]) + "\n\n"
        result += "【设备安全建议】\n"
        result += "1. 强烈建议关闭所有门窗，防止雨水/雪水飘入室内打湿地板，导致扫地机器人吸入液体损坏电机。\n"
        result += "2. 请确保扫地机器人的基站（充电座）未放置在容易漏水的阳台或窗边。\n"
        result += "3. 雷暴天气建议拔掉基站电源，防止雷击浪涌损坏电子元器件。"
        
        return result
        
    except Exception as e:
        logger.error(f"[WeatherTool] 获取气象预警失败: {e}")
        return f"暂时无法获取 {city} 的气象预警数据，请稍后再试。"
