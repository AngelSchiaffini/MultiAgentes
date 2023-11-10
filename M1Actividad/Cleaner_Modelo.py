# cleaners_model.py

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import random

class Garbage(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.isFull = True

    def step(self):
        pass

class CleanerBot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.movements = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        new_position = self.random.choice(possible_steps)
        cellmates = self.model.grid.get_cell_list_contents([new_position])
        flag = True

        for cellmate in cellmates:
            if not isinstance(cellmate, CleanerBot):
                flag = False

        isEmpty = not flag

        self.movements += 1

        while not isEmpty:
            new_position = self.random.choice(possible_steps)
            cellmates = self.model.grid.get_cell_list_contents([new_position])
            flag = True

            for cellmate in cellmates:
                if not isinstance(cellmate, CleanerBot):
                    flag = False

            isEmpty = not flag

        self.model.grid.move_agent(self, new_position)

    def step(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for cellmate in cellmates:
            if isinstance(cellmate, Garbage):
                cellmate.isFull = False
        self.move()

class CleanersModel(Model):
    def __init__(self, width, height, num_agents, dirty_percentage):
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        num_garbage = int((dirty_percentage * width * height) / 100)

        for i in range(num_garbage):
            temp = Garbage(i, self)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            while not self.grid.is_cell_empty((x, y)):
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
            self.schedule.add(temp)
            self.grid.place_agent(temp, (x, y))

        for i in range(num_agents):
            temp = CleanerBot(i + num_garbage, self)
            self.grid.place_agent(temp, (0, 0))
            self.schedule.add(temp)

        self.datacollector = DataCollector(
            agent_reporters={"Position": "pos"},
            model_reporters={"Movements": "total_movements", "CleanPercentage": "clean_percentage"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

        if all(isinstance(cell, Garbage) and not cell.isFull for cell in self.grid.coord_iter()):
            self.running = False

    def clean_percentage(self):
        clean_cells = sum(isinstance(cell, Garbage) and not cell.isFull for cell in self.grid.coord_iter())
        total_cells = self.grid.width * self.grid.height
        return clean_cells / total_cells * 100 if total_cells > 0 else 0

    def total_movements(self):
        return sum(agent.movements for agent in self.schedule.agents)
