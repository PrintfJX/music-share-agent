from langchain.tools import tool
@tool
def calculator(expression:str ) -> str:
    """执行数学计算
    使用此工具来解决计算数学问题，例如加法、减法、乘法、除法。
    支持基本的数学表达式如"2+2"、"100*5"、"1000/4"等。
    Args:
        expression: 数学表达式，例如 "2+2" 或 "sqrt(16)"
    
    Returns:
        计算结果
    """
    try:
        result=eval(expression)
        return f"{expression}={result}"
    except Exception as e:
        return f"计算错误：{str(e)}"
    
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。
    
    使用此工具当用户询问任何关于天气的问题时。
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息（温度、条件等）
    """
    weather_data = {
        "北京": "晴，25°C，东风2级",
        "上海": "多云，23°C，无风",
        "深圳": "阴，28°C，南风3级",
        "成都": "小雨，20°C，西南风4级"
    }
    
    result = weather_data.get(city, f"暂无 {city} 的天气数据")
    return f"{city}：{result}"
