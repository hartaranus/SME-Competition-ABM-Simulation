from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from SME_L_and_P.agents import SME, Competitor, Profit
from SME_L_and_P.model import CompetitorSME

def competitor_sme_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is SME:
        portrayal["Shape"] = "SME_L_and_P/resources/sme.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    elif type(agent) is Competitor:
        portrayal["Shape"] = "SME_L_and_P/resources/competitor.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.opt_cost, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is Profit:
        if agent.fully_grown:
            portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
        else:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(competitor_sme_portrayal, 20, 20, 500, 500)
chart_element = ChartModule(
    [
        {"Label": "Competitors", "Color": "#AA0000"},
        {"Label": "SME's", "Color": "#666666"},
        {"Label": "Profits", "Color": "#00AA00"},
    ]
)

model_params = {
    "profit": UserSettableParameter("checkbox", "Profit Enabled", True),
    "profit_regrowth_time": UserSettableParameter(
        "slider", "Profit Regrowth Time", 20, 1, 50
    ),
    "initial_sme": UserSettableParameter(
        "slider", "Initial SME Population", 100, 10, 300
    ),
    "sme_growth": UserSettableParameter(
        "slider", "SME Growth Rate", 0.04, 0.01, 1.0, 0.01
    ),
    "initial_competitors": UserSettableParameter(
        "slider", "Initial Competitor Population", 50, 10, 300
    ),
    "competitor_growth": UserSettableParameter(
        "slider",
        "Competitor Growth Rate",
        0.05,
        0.01,
        1.0,
        0.01,
        description="The rate at which competitor agents growing.",
    ),
    "competitor_gain_from_customer": UserSettableParameter(
        "slider", "Competitor Gain From Customer Rate", 20, 1, 50
    ),
    "sme_gain_from_customer": UserSettableParameter(
        "slider", "SME Gain From Customer", 4, 1, 10
    ),
}

server = ModularServer(
    CompetitorSME, [canvas_element, chart_element], 
    "SME Competition Simulation",
    model_params,
)
server.port = 4200
