from langchain_core.tools import tool
from utils.logger_handler import logger
import json
import time
import random
from datetime import datetime, timedelta

# 模拟设备的内存状态（数字孪生）
_device_state = {
    "is_online": True,
    "status": "idle",  # 状态枚举：idle(空闲/充电中), cleaning(清扫中), paused(暂停), self_cleaning(洗拖布/自清洁), error(故障)
    "battery_level": 100,  # 电量百分比 0-100
    "water_level": "high",  # 水箱水量：high, medium, low, empty
    "dustbox_full": False,  # 尘盒是否已满
    "current_task": None,   # 记录当前清扫任务的信息（如开始时间、区域）
    "scheduled_tasks": [],  # 预约任务列表，元素为字典，如 {"id": 1, "time": "2025-06-15 10:00", "region": "客厅", "mode": "standard"}
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

def _simulate_tick():
    """内部辅助函数：模拟时间的流逝和设备状态的变化（动态状态演进）"""
    if _device_state["status"] == "cleaning" and _device_state["current_task"]:
        # 每次查询或操作时，模拟清扫过程中的消耗
        start_time = _device_state["current_task"]["start_time"]
        elapsed_minutes = (time.time() - start_time) / 60.0
        
        # 模拟电量消耗 (假设每分钟掉 1% 电)
        drop = int(elapsed_minutes * 1)
        if drop > 0:
            _device_state["battery_level"] = max(10, _device_state["battery_level"] - drop)
            _device_state["current_task"]["start_time"] = time.time() # 重置时间以便下次计算
            _device_state["current_task"]["cleaned_area"] += drop * 1.5 # 模拟每分钟扫 1.5 平米
            
            # 随机触发模拟故障 (极小概率，或者当电量低于 15% 时强制回充)
            if _device_state["battery_level"] <= 15:
                _device_state["status"] = "idle"
                _device_state["current_task"] = None
                _device_state["last_error"] = "Error 2: 电量过低，已自动返回基站。"
                return

@tool(description="获取扫地机器人当前的整体运行状态、电量、水箱、尘盒情况及当前清扫任务进度，以 JSON 字符串形式返回。当下发清扫指令前，或用户询问机器状态时必须调用此工具。")
def get_device_status() -> str:
    """获取设备实时动态状态"""
    logger.info("[DeviceTool] 查询设备状态")
    _simulate_tick() # 触发状态演进
    
    status_desc = {
        "idle": "空闲/在基站充电中",
        "cleaning": "正在清扫中",
        "paused": "已暂停",
        "self_cleaning": "正在基站洗拖布/自清洁",
        "error": "设备发生故障"
    }
    
    current_status = _device_state.copy()
    current_status["status_description"] = status_desc.get(current_status["status"], "未知状态")
    current_status.pop("consumables", None)
    
    # 格式化任务信息以便于阅读
    if current_status["current_task"]:
        task = current_status["current_task"]
        elapsed = int((time.time() - task["start_time"]) / 60)
        current_status["task_progress"] = f"正在清扫 {task['region']}，已清扫 {elapsed} 分钟，完成约 {int(task['cleaned_area'])} 平方米。"
    
    return json.dumps(current_status, ensure_ascii=False)


@tool(description="获取扫地机器人各项耗材（主刷、边刷、HEPA滤网）的剩余寿命百分比。")
def get_consumables_life() -> str:
    """获取耗材寿命"""
    logger.info("[DeviceTool] 查询耗材寿命")
    return json.dumps(_device_state["consumables"], ensure_ascii=False)


@tool(description="向扫地机器人下发指令以改变其运行状态。command 支持: 'start_clean'(开始清扫), 'pause'(暂停), 'return_to_dock'(返回基站回充), 'self_clean'(基站自清洁/洗拖布)。当 command 为 'start_clean' 时，可通过 region 参数指定清扫区域。若设备正在执行其他任务，默认会被拒绝；可设置 force=True 强制打断当前任务并执行新指令。")
def control_device(command: str, region: str = "全局", force: bool = False) -> str:
    """控制设备运行状态（支持区域清扫、自清洁、强制打断）"""
    logger.info(f"[DeviceTool] 下发控制指令: {command}, 区域: {region}, 强制执行: {force}")
    _simulate_tick()
    
    if not _device_state["is_online"]:
        return "指令下发失败：设备当前离线，请检查设备网络连接。"
        
    # 状态冲突与强制打断逻辑
    current_status = _device_state["status"]
    if current_status in ["cleaning", "self_cleaning"] and command != "pause" and command != "return_to_dock":
        if not force:
            return f"⚠️ 冲突拦截：设备当前正在【{current_status}】。为了保护设备和任务连续性，系统拒绝了新指令。如果确实需要立即执行新任务，请询问用户是否确认打断当前任务（使用 force=True 重新调用）。"
        else:
            logger.warning("[DeviceTool] 强制打断当前任务！")
            
    if command == "start_clean":
        if _device_state["battery_level"] < 15:
            return f"指令下发失败：设备电量过低（{_device_state['battery_level']}%），请等待充电完成。"
        
        # 检查耗材前置条件 (模拟逻辑：如果边刷寿命极低且未强制，建议先更换)
        if _device_state["consumables"]["side_brush"] <= 5 and not force:
             return "⚠️ 前置条件拦截：边刷寿命已严重不足（≤5%），强行清扫可能划伤地板或清扫不净。请询问用户是否确认强行清扫（force=True），或者先购买更换边刷。"
             
        if _device_state["status"] == "error" and _device_state["last_error"] and "Error 2" not in _device_state["last_error"]:
            return f"指令下发失败：设备处于故障状态（{_device_state['last_error']}），请先排除故障。"
            
        _device_state["status"] = "cleaning"
        _device_state["last_error"] = None
        _device_state["current_task"] = {
            "region": region,
            "start_time": time.time(),
            "cleaned_area": 0.0
        }
        return f"✅ 指令下发成功：扫地机器人已开始对【{region}】进行清扫。"
        
    elif command == "pause":
        if _device_state["status"] in ["cleaning", "self_cleaning"]:
            _device_state["status"] = "paused"
            return "✅ 指令下发成功：设备已暂停当前操作。"
        return "指令下发忽略：设备当前不在运行中。"
            
    elif command == "return_to_dock":
        _device_state["status"] = "idle"
        _device_state["current_task"] = None
        _device_state["battery_level"] = min(100, _device_state["battery_level"] + 10) 
        return "✅ 指令下发成功：扫地机器人正在返回基站。"
        
    elif command == "self_clean":
        if _device_state["status"] != "idle" and not force:
             return "⚠️ 冲突拦截：设备不在基站，无法进行自清洁。请先让其回充或使用 force=True 强制结束任务并洗拖布。"
        _device_state["status"] = "self_cleaning"
        _device_state["current_task"] = None
        return "✅ 指令下发成功：基站已开始自清洁和洗拖布，预计需要 3 分钟。"
        
    return f"指令下发失败：不支持的指令 '{command}'。"


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

@tool(description="模拟为扫地机器人购买耗材。当用户同意更换某项耗材（如边刷、主刷、滤网）时调用。参数 item 为要购买的耗材名称（如 '边刷'、'主刷'）。")
def purchase_consumables(item: str) -> str:
    """模拟一键购买耗材"""
    logger.info(f"[DeviceTool] 模拟购买耗材: {item}")
    order_id = f"ORDER-{random.randint(10000, 99999)}"
    
    # 模拟购买后重置寿命
    if "边刷" in item:
        _device_state["consumables"]["side_brush"] = 100
    elif "主刷" in item:
        _device_state["consumables"]["main_brush"] = 100
    elif "滤网" in item or "hepa" in item.lower():
        _device_state["consumables"]["hepa_filter"] = 100
        
    return f"下单成功！已为您在官方商城购买原装【{item}】，订单号：{order_id}。预计明天送达。同时我已在系统中将该耗材的预期寿命重置为 100%。"

@tool(description="获取扫地机器人过去 7 天的清扫历史统计数据，包括总清扫次数、总时长和常扫区域分析。当用户询问机器最近的工作表现时调用。")
def get_cleaning_history() -> str:
    """获取清扫日志与分析"""
    logger.info("[DeviceTool] 获取历史清扫日志")
    history_data = {
        "time_range": "过去 7 天",
        "total_clean_count": 5,
        "total_clean_area_sqm": 325,
        "total_duration_minutes": 210,
        "frequent_regions": ["客厅", "主卧"],
        "infrequent_regions": ["厨房", "阳台"],
        "suggestion": "系统分析发现，过去7天内【厨房】区域仅清扫过1次。建议您可以设置每周定期对厨房进行深度扫拖，以保持油污区域的清洁。"
    }
    return json.dumps(history_data, ensure_ascii=False)

@tool(description="智能故障诊断与排查工具。当 get_device_status 返回设备处于 error 状态，或用户明确说明机器报错/卡住时，必须调用此工具获取具体的排查和修复建议。")
def diagnose_error() -> str:
    """故障诊断与修复建议"""
    logger.info("[DeviceTool] 运行故障诊断")
    error_msg = _device_state.get("last_error")
    
    if _device_state["status"] != "error" or not error_msg:
        return "诊断结果：设备目前运行正常，未检测到活跃的故障代码。"
        
    # 模拟知识库联动诊断逻辑
    diagnosis = f"【诊断报告】检测到设备当前报错：{error_msg}\n\n"
    if "激光雷达被遮挡" in error_msg:
        diagnosis += "排查建议：\n1. 请检查机器是否卡在床底或沙发底等低矮空间，将其搬出。\n2. 检查顶部凸起的激光雷达罩内是否有异物（如头发、纸屑）卡住。\n3. 用干纸巾轻轻擦拭雷达传感器窗口。"
    elif "电量过低" in error_msg:
        diagnosis += "排查建议：\n机器电量已耗尽。请手动将机器搬回基站，确保充电触点对齐。建议充电至 20% 以上再继续任务。"
    else:
        diagnosis += "排查建议：\n请重启设备或清理主刷、边刷及尘盒。如问题依旧，请联系售后客服。"
        
    return diagnosis

@tool(description="为扫地机器人添加预约清扫任务。需要提供 time_str（格式必须为 'YYYY-MM-DD HH:MM'，如 '2025-06-15 10:00'）、region（如 '全局', '客厅'）和 mode（可选，如 'standard', 'strong'）。如果预约时间与现有任务冲突，将返回失败提示。建议在添加预约前，结合 get_forecast_weather 检查未来天气情况（如是否下雨）以给出更智能的建议。")
def schedule_task(time_str: str, region: str = "全局", mode: str = "standard") -> str:
    """添加智能预约清扫任务"""
    logger.info(f"[DeviceTool] 添加预约任务 - 时间: {time_str}, 区域: {region}, 模式: {mode}")
    
    # 简单校验时间格式
    try:
        task_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "预约失败：时间格式错误。请使用 'YYYY-MM-DD HH:MM' 格式，例如 '2025-06-15 10:00'。"
        
    # 检查过去的时间
    # 这里为了演示，我们假设当前时间是 2026-03-23（基于环境上下文），如果在真实环境应该用 datetime.now()
    # 简单起见，这里不严格限制必须大于真实当前时间，只做逻辑展示
    
    # 检查时间冲突（假设每个任务至少需要 1 小时）
    for existing_task in _device_state["scheduled_tasks"]:
        existing_time = datetime.strptime(existing_task["time"], "%Y-%m-%d %H:%M")
        if abs((task_time - existing_time).total_seconds()) < 3600:
            return f"预约失败：时间冲突。在 {existing_task['time']} 已经有一个清扫【{existing_task['region']}】的预约任务。请选择相隔至少 1 小时的时间。"
            
    # 生成任务 ID 并添加
    task_id = len(_device_state["scheduled_tasks"]) + 1
    new_task = {
        "id": task_id,
        "time": time_str,
        "region": region,
        "mode": mode
    }
    _device_state["scheduled_tasks"].append(new_task)
    
    # 按照时间排序
    _device_state["scheduled_tasks"].sort(key=lambda x: x["time"])
    
    return f"预约成功！已为您安排在 {time_str} 清扫【{region}】（模式：{mode}）。任务 ID：{task_id}。"

@tool(description="获取当前所有的预约清扫任务列表。当用户询问'我预约了哪些任务'或需要检查预约冲突时调用。")
def get_scheduled_tasks() -> str:
    """获取当前预约任务列表"""
    logger.info("[DeviceTool] 获取预约任务列表")
    tasks = _device_state["scheduled_tasks"]
    if not tasks:
        return "当前没有任何预约清扫任务。"
        
    result = "【当前预约任务列表】\n"
    for t in tasks:
        result += f"- 任务 ID: {t['id']}, 时间: {t['time']}, 区域: {t['region']}, 模式: {t['mode']}\n"
    return result
