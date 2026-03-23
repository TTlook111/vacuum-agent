from langchain.agents import create_agent
from model.factory import chat_model
from agent.tools.agent_tools import rag_summarize, get_user_location, get_user_id, \
    get_current_month, fetch_external_data, fill_context_for_report
from agent.tools.weather_tool import get_current_weather, get_history_weather, get_forecast_weather, get_air_quality, get_weather_alerts
from agent.tools.device_tool import get_device_status, get_consumables_life, control_device, set_cleaning_mode, purchase_consumables, get_cleaning_history, diagnose_error
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize,
                   get_current_weather,
                   get_history_weather,
                   get_forecast_weather,
                   get_air_quality,
                   get_weather_alerts,
                   get_device_status,
                   get_consumables_life,
                   control_device,
                   set_cleaning_mode,
                   purchase_consumables,
                   get_cleaning_history,
                   diagnose_error,
                   get_user_location,
                   get_user_id,
                   get_current_month,
                   fetch_external_data,
                   fill_context_for_report
                   ],
            middleware=[
                report_prompt_switch,
                log_before_model,
                monitor_tool
            ]
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        # 第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("扫地机器在我所在的地区的气温下如何保养？"):
        print(chunk, end="", flush=True)
