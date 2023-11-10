from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from Cleaner_Modelo import CleanersModel, Garbage, CleanerBot
import time

def agent_portrayal(agent):
    if isinstance(agent, Garbage):
        if agent.isFull:
            portrayal = {"Shape": "rect",
                         "w": 1,
                         "h": 1,
                         "Filled": "true",
                         "Layer": 0,
                         "Color": "gray"}
        else:
            portrayal = {"Shape": "rect",
                         "w": 1,
                         "h": 1,
                         "Filled": "true",
                         "Layer": 0,
                         "Color": "white"}
    elif isinstance(agent, CleanerBot):
        portrayal = {"Shape": "circle",
                     "r": 1,
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "red"}
    else:
        portrayal = {}
    return portrayal

ancho = 28
alto = 28
grid = CanvasGrid(agent_portrayal, ancho, alto, 500, 500)
server = ModularServer(CleanersModel,
                       [grid],
                       "Cleaners",
                       {"width": ancho, "height": alto,
                        "num_agents": 10, "dirty_percentage": 70})
server.port = 8521

if __name__ == "__main__":
    try:
        start_time = time.time()  # Tiempo de inicio de la simulación
        server.launch()
    except KeyboardInterrupt:
        print("\nSimulation interrupted.")
    finally:
        elapsed_time = time.time() - start_time  # Tiempo transcurrido
        print(f"Elapsed time: {elapsed_time} seconds")

        if elapsed_time >= 300:  # 300 segundos = 5 minutos
            print("Simulation exceeded time limit. Exiting...")
        else:
            # Accede a los resultados de la simulación después de la interrupción
            model = server.model
            positions = model.datacollector.get_agent_vars_dataframe().xs(0, level="AgentID")["Position"]
            print("Final positions of agents:")
            print(positions)

            total_movements = model.datacollector.get_model_vars_dataframe()["Movements"].iloc[0]
            clean_percentage = model.datacollector.get_model_vars_dataframe()["CleanPercentage"].iloc[0]

            print(f"Total movements: {total_movements}")
            print(f"Clean percentage: {clean_percentage}%")
