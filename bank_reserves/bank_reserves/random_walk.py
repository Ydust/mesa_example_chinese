from mesa import Agent


class RandomWalker(Agent):
    """
    以通用方式实现随机游走方法的类
    不打算单独使用，而是讲该方法继承给其他 Agent
    """

    grid = None
    x = None
    y = None
    # 使用摩尔邻域
    moore = True

    def __init__(self, unique_id, pos, model, moore=True):
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def random_move(self):
        """
        在允许的任意方向上走一步
        """
        # 从相邻单元格中选择下一个移动单元
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)

        self.model.grid.move_agent(self, next_move)

