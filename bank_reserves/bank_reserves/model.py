from bank_reserves.agents import Bank, Person
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np


"""
如果想实现参数扫描，可以运行 batch_run.py 
"""


def get_num_rich_agents(model):
    """返回富人的数量"""

    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threhold]
    return len(rich_agents)


def get_num_poor_agents(model):
    """返回穷人的数量"""
    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    return len(poor_agents)


def get_num_mid_agents(model):
    """返回中产阶级的数量"""
    mid_agents = [a for a in model.schedule.agents if a.loans < 10 and a.savings < model.rich_threshold]
    return len(mid_agents)


def get_total_savings(model):
    """所有 Agent存款的总额"""
    agent_savings = [a.savings for a in model.schedule.agents]
    return np.sum(agent_savings)


def get_total_wallets(model):
    """所有 Agent钱包中钱的总额"""
    agent_wallets = [a.wallet for a in model.schedule.agents]
    return np.sum(agent_wallets)


def get_total_money(model):
    """所有 Agent钱包和存款的总额"""
    awallet_money = get_total_wallets(model)
    savings_money = get_total_savings(model)
    return awallet_money + savings_money


def get_total_loans(model):
    """所有Agent贷款的总额"""
    agent_loans = [a.loans for a in model.schedule.agents]
    return np.sum(agent_loans)


class BankReserves(Model):
    """
    这个模型是来自 NetLogo 的银行储备模型的 Mesa 实现。
    它是一种高度抽象、简化的经济模型，只有一种类型的代理人和一家代表经济中所有银行的银行。
    人（由圆圈表示）在网格内随机移动。如果两个或更多人在同一个网格位置，他们有 50% 的机会相互交易。
    如果他们进行交易，则给予其他代理人 5 美元或 2 美元的机会均等。正的贸易余额将作为储蓄存入银行。
    如果交易导致负余额，代理将尝试从其储蓄中提取以弥补余额。如果它没有足够的储蓄来弥补负余额，它将从银行贷款来弥补差额。
    银行需要保留一定比例的存款作为准备金，银行在任何给定时间的贷款能力是存款金额、准备金和当前未偿还贷款总额的函数。
    """

    # 表格的高
    grid_h = 20
    # 表格的宽
    grid_w = 20

    """
    初始化参数 init_people   rich_threshold  reserve_percent 都是UserSettableParameters
    """

    def __init__(
            self,
            height=grid_h,
            width=grid_w,
            init_people=2,
            rich_threshold=10,
            reserve_percent=50
    ):
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        # rich_threshold 是 可以被视为“富人”的存款金额
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent
        # 参考 DataCollector 功能
        self.datacollector = DataCollector(
            model_reporters={
                "Rich": get_num_rich_agents,
                "Poor": get_num_poor_agents,
                "Middle class": get_num_mid_agents,
                "Savings": get_total_savings,
                "Wallets": get_total_wallets,
                "Money": get_total_money,
                "Loans": get_total_loans
            },
            agent_reporters={"Wealth": lambda x: x.wealth}
        )

        # 创建一个独立的银行
        self.bank = Bank(1, self, self.reserve_percent)

        # 根据用户设置的人数为模型创建Agents
        for i in range(self.init_people):
            # 在网格内随机设置 x, y 坐标
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            # 将 Person 对象放在坐标（x, y）的网格上
            self.grid.place_agent(p, (x, y))
            # 向 schedule 添加 Person 对象
            self.schedule.add(p)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self):
        for i in range(self.run_time):
            self.step()







