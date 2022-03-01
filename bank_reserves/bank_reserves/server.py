from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from bank_reserves.agents import Person
from bank_reserves.model import BankReserves


# 绿色
RICH_COLOR = "#46FF33"
# 红色
POOR_COLOR = "#FF3C33"
# 蓝色
MID_COLOR = "#3349FF"


def person_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    # 更新每个 Person 对象的描述特征
    if isinstance(agent, Person):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "True"

        color = MID_COLOR

        # 根据存款和贷款设置 agent 颜色
        if agent.savings > agent.model.rich_threshold:
            color = RICH_COLOR
        if agent.savings < 10 and agent.loans < 10:
            color = MID_COLOR
        if agent.loans > 10:
            color = POOR_COLOR

        portrayal["Color"] = color

    return portrayal


# 用户可以设置参数的字典，那些可以映射到模型__init__的参数
model_params = {
    "init_people": UserSettableParameter(
        "slider", "People", 25, 1, 200, description="初始化人数"
     ),
    "rich_threshold": UserSettableParameter(
        "slider", "Rich_threshold", 10, 1, 20, description="随机初始化钱包金额上限"
    ),
    "reserve_percent": UserSettableParameter(
        "slider", "Reserves", 50, 1, 100, description="银行必须预留百分之多少的存款"
    )
}


canvas_element = CanvasGrid(person_portrayal, 20, 20, 500, 500)


chart_element = ChartModule(
    [
        {"Label": "Rich", "Color": RICH_COLOR},
        {"Label": "Poor", "Color": POOR_COLOR},
        {"Label": "Middle Class", "Color": MID_COLOR}
    ]
)

# 创建 Mesa ModularServer 的实例
server = ModularServer(
    BankReserves,
    [canvas_element, chart_element],
    "银行储蓄模型",
    model_params=model_params
)

