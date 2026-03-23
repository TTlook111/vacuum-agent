from langchain_core.tools import tool
from utils.logger_handler import logger
import json

# 模拟设备的内存状态（数字孪生）
_device_state = {
    "is_online": True,
    "status": "idle",  # 状态枚举：idle(空闲/充电中), cleaning(清扫中), paused(暂停), error(故障)
    "battery_level": 100,  # 电量百分比 0-100
    "water_level": "high",  # 水箱水量：high, medium, low, empty
    "dustbox_full": False,  # 尘盒是否已满
    "consumables": {
        "main_brush": 85,  # 主刷寿命百分比
        "side_brush": 5,   # 边刷寿命百分比 (模拟需要更换的情况)
        "hepa_filter": 60  # 滤网寿命百分比
    },
    "current_mode": {
        "suction": "standard", # 吸力：quiet, standard, strong, max
        "water_volume": "medium" # 出水量：low, medium, high
    },
    "last_error": None # 故障信息，例如 "Error 8: 激光雷达被遮挡"
}

@tool(description="获取扫地机器人当前的整体运行状态、电量、水箱及尘盒情况，以 JSON 字符串形式返回。当用户询问机器状态或准备下发清扫指令前，应先调用此工具确认设备是否就绪。")
def get_device_status() -> str:
    """获取设备实时状态"""
    logger.info("[DeviceTool] 查询设备状态")
    # 组装对 LLM 友好的状态描述
    status_desc = {
        "idle": "空闲/在基站充电中",
        "cleaning": "正在清扫中",
        "paused": "已暂停",
        "error": "设备发生故障"
    }
    
    current_status = _device_state.copy()
    current_status["status_description"] = status_desc.get(current_status["status"], "未知状态")
    
    # 移除不需要每次都展示的详细耗材信息，保持核心状态简洁
    current_status.pop("consumables", None)
    
    return json.dumps(current_status, ensure_ascii=False)


@tool(description="获取扫地机器人各项耗材（主刷、边刷、HEPA滤网）的剩余寿命百分比。当用户询问耗材情况，或在日常维护场景下，调用此工具。")
def get_consumables_life() -> str:
    """获取耗材寿命"""
    logger.info("[DeviceTool] 查询耗材寿命")
    return json.dumps(_device_state["consumables"], ensure_ascii=False)


@tool(description="向扫地机器人下发指令以改变其运行状态。支持的指令包括：start_clean(开始清扫), pause(暂停), return_to_dock(返回基站回充)。调用前建议先通过 get_device_status 确认当前状态。")
def control_device(command: str) -> str:
    """控制设备运行状态"""
    logger.info(f"[DeviceTool] 下发设备控制指令: {command}")
    
    if not _device_state["is_online"]:
        return "指令下发失败：设备当前离线，请检查设备网络连接。"
        
    if command == "start_clean":
        if _device_state["battery_level"] < 15:
            return f"指令下发失败：设备电量过低（{_device_state['battery_level']}%），请等待充电完成。"
        if _device_state["status"] == "error":
            return f"指令下发失败：设备处于故障状态（{_device_state['last_error']}），请先排除故障。"
            
        _device_state["status"] = "cleaning"
        return "指令下发成功：扫地机器人已开始清扫。"
        
    elif command == "pause":
        if _device_state["status"] == "cleaning":
            _device_state["status"] = "paused"
            return "指令下发成功：扫地机器人已暂停清扫。"
        else:
            return "指令下发忽略：设备当前未在清扫中。"
            
    elif command == "return_to_dock":
        _device_state["status"] = "idle"
        return "指令下发成功：扫地机器人正在返回基站充电。"
        
    else:
        return f"指令下发失败：不支持的指令 '{command}'。支持的指令为 start_clean, pause, return_to_dock。"


@tool(description="设置扫地机器人的清扫参数。suction_power(吸力)可选值: quiet(安静), standard(标准), strong(强力), max(Max)。water_volume(出水量)可选值: low(低), medium(中), high(高)。必须同时传入这两个参数。")
def set_cleaning_mode(suction_power: str, water_volume: str) -> str:
    """设置清扫模式（吸力和出水量）"""
    logger.info(f"[DeviceTool] 设置清扫模式 - 吸力: {suction_power}, 出水量: {water_volume}")
    
    valid_suction = ["quiet", "standard", "strong", "max"]
    valid_water = ["low", "medium", "high"]
    
    if suction_power not in valid_suction:
        return f"设置失败：吸力参数 '{suction_power}' 无效，请使用 {valid_suction} 中的一个。"
        
    if water_volume not in valid_water:
        return f"设置失败：出水量参数 '{water_volume}' 无效，请使用 {valid_water} 中的一个。"
        
    _device_state["current_mode"]["suction"] = suction_power
    _device_state["current_mode"]["water_volume"] = water_volume
    
    return f"设置成功：吸力已调整为 '{suction_power}'，出水量已调整为 '{water_volume}'。"
