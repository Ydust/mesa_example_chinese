from mesa import Agent
from bank_reserves.random_walk import RandomWalker


class Bank(Agent):
    def __init__(self, unique_id, model, reserve_percent=50):
        super().__init__(unique_id, model)
        # 未偿还贷款的总值
        self.bank_loans = 0
        # 存款中百分之多少拿来做银行准备金，单位：%
        self.reserve_percent = reserve_percent
        # 存款总值
        self.deposits = 0
        # 准备金
        self.reserves = (self.reserve_percent / 100) * self.deposits
        # 银行目前能够贷款的金额
        self.bank_to_loan = 0
        # 更新银行的准备金和可以贷款的金额；
        # 每当一个人平衡他们的账目时都会调用这个
        # Person.balance_books() 见下文

    def bank_balance(self):
        self.reserves = (self.reserve_percent / 100) * self.deposits
        # 能够贷款的金额 = 存款 - （准备金 + 未偿还贷款总值）
        self.bank_to_loan = self.deposits - (self.reserves + self.bank_loans)


# RandomWalker 的子类，它是 Mesa Agent 的子类
class Person(RandomWalker):
    def __init__(self, unique_id, pos, model, moore, bank, rich_threshold):
        # 使用需要的参数初始化父类
        super().__init__(unique_id, pos, model, moore=moore)
        # 每人的储蓄金
        self.savings = 0
        # 每人的未偿还贷款
        self.loans = 0
        """每人的钱包里有 1~a 这个范围的随机金额，也可以自定义范围"""
        # random.ranint(a, b) 随机产生[a, b]之间的整数
        self.wallet = self.random.randint(1, rich_threshold + 1)
        # 存款 - 贷款 参考 balance_books()
        self.wealth = 0
        # 交易的对象 参考 do_business()
        self.customer = 0
        # 个人银行，在 __inint__ 处设置，模型中所有人的个人银行是相相同的
        self.bank = bank

    def do_business(self):
        """检查个体是否有存款，钱包里有多少钱，银行可以贷款给他多少钱"""
        if self.savings > 0 or self.wallet > 0 or self.bank.bank_to_loan > 0:
            # 在我的位置创建人员列表
            my_cell = self.model.grid.get_cell_list_contents([self.pos])
            # 检查是否有其他人在我的位置
            if len(my_cell) > 1:
                # 在 while 循环中，把用户设置为 self
                customer = self
                while customer == self:
                    """从我所在位置的人中随机选择一个人进行交易"""
                    customer = self.random.choice(my_cell)
                # 50%的概率与附近的客户交易
                if self.random.randint(0, 1) == 0:
                    # 50% 的概率交易金额为5美元
                    if self.random.randint(0, 1) == 0:
                        # 从我的钱包里给客户 5美元 （可能导致负钱包）
                        customer.wallet += 5
                        self.wallet -= 5
                    # 50% 的机会交易 2美元
                    else:
                        # 从我的钱包里给客户 2美元（可能导致负钱包）
                        customer.wallet += 2
                        self.wallet -= 2

    def balance_books(self):
        # 检查钱包是否因与客户交易后为负
        if self.wallet < 0:
            # 如果钱包里的钱是负数，检查存款是否可以支付余额
            if self.savings >= (self.wallet * -1):
                """如果我的存款可以支付余额，就从我的存款中提取足够的钱，使我的钱包余额为 0"""
                self.withdraw_from_savings(self.wallet * -1)
            # 如果我的存款无法支付我钱包的负余额
            else:
                # 检查我是否有存款
                if self.savings > 0:
                    # 如果我有存款，就全部取出以减少我钱包的负余额
                    self.withdraw_from_savings(self.savings)
                    # 记录银行现在可以贷出多少钱
                    temp_loan = self.bank.bank_to_loan
                    """检查银行是否可以贷出足够的钱来支付我钱包里剩余的负余额"""
                    if temp_loan >= (self.wallet * -1):
                        """如果银行可以贷出足够的钱来支付我钱包的负余额，就为剩余的负余额贷款"""
                        self.take_out_loan(self.wallet * -1)
                    else:
                        """如果银行不能贷出支付我钱包负余额的钱，那么就贷出银行现在可以贷款的总金额"""
                        self.take_out_loan(temp_loan)
        else:
            # 如果我的钱包里有与客户交易的钱，请将其存到银行存款
            self.deposit_to_savings(self.wallet)
            # 检查我是否有未偿还的贷款，我是否有存款
            if self.loans > 0 and self.savings > 0:
                # 检查我的存款是否可以偿还我的贷款
                if self.savings >= self.loans:
                    self.withdraw_from_savings(self.loans)
                    self.repay_a_loan(self.loans)
                # 如果我的存款不能偿还我的贷款
                else:
                    # 用我的存款还清部分贷款
                    self.withdraw_from_savings(self.wallet)
                    self.repay_a_loan(self.loans)
        # 计算 我的财富 = 存款 - 贷款
        self.wealth = self.savings - self.loans

    # 存入银行
    def deposit_to_savings(self, amount):
        # 从我的钱包中取钱存入银行
        self.wallet -= amount
        self.savings += amount
        # 增加银行的存款
        self.bank.deposits += amount

    # 从银行取钱
    def withdraw_from_savings(self, amount):
        # 从银行取钱放入我的钱包
        self.wallet += amount
        self.savings -= amount
        # 减少银行存款
        self.bank.deposits -= amount

    # 偿还贷款
    def repay_a_loan(self, amount):
        # 从我的钱包里偿还部分或全部贷款
        self.loans -= amount
        self.wallet -= amount
        # 增加银行现在可以贷款的金额
        self.bank.bank_to_loan += amount
        # 减少未偿还银行的贷款金额
        self.bank_loans -= amount

    # 从银行贷款
    def take_out_loan(self, amount):
        # 从银行贷出的钱放到钱包里，增加我的未偿还贷款金额
        self.loans += amount
        self.wallet += amount
        # 减少从银行可以贷款的金额
        self.bank.bank_to_loan -= amount
        # 增加银行的未偿还贷款
        self.bank.bank_loans += amount

    # 为 model.BankReservesModel.schedule.step() 中的每个 Agent 调用 step()
    def step(self):
        self.random_move()
        self.do_business()
        self.balance_books()
        self.bank.bank_balance()




































