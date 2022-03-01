from bank_reserves.model import get_num_rich_agents
import itertools
from mesa import Model
from bank_reserves.model import BankReserves
from bank_reserves.model import BankReserves
from mesa.batchrunner import BatchRunner
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np
import pandas as pd


# parameter lists for each parameter to be tested in batch run
br_params = {"init_people": [25, 100], "rich_threshold": [5, 10]}
fixed_params = {"reserve_percent": 5}

if __name__ == "__main__":
    data = BatchRunner(
        BankReserves,
        br_params,
        model_reporters={"Rich": get_num_rich_agents},
        agent_reporters={"Wealth": "wealth"},
    )
    br_df = pd.DataFrame(data)
    br_df.to_csv("BankReservesModel_Data.csv")
