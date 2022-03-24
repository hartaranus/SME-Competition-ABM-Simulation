"""
Competitors-SME Predation Model
 
 Ported by:
 ----------------------------
 | Willy Satrio N            |
 | found me on               |
 |---------------------------|
 | Github        : hartaranus|
 | stackoverflow : Willy SN  |
 |---------------------------|
 -----------------------------

 from :

Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from SME_L_and_P.scheduler import RandomActivationByTypeFiltered
from SME_L_and_P.agents import SME, Competitor, Profit


class CompetitorSME(Model):
    """
    Competitor-SME Predation Model
    """

    height = 20
    width = 20

    initial_sme = 100
    initial_competitors = 50

    sme_growth = 0.04
    competitor_growth= 0.05

    competitor_gain_from_customer = 20

    profit = False
    profit_regrowth_time = 30
    sme_gain_from_customer = 4

    verbose = False  # Print-monitoring

    description = (
        '''
            A model for simulating competitor and sme (predator-prey) business ecosystem modelling.
            Part of Indonesian Manufacturing SME's Industry 4.0 Adoption Study By Ishardita Pambudi Tama,Ph.D\n
            \n
            Team:\n
            Ishardita Pambudi Tama,Ph.D\n
            &
            Dr. Willy Satrio Nugroho\n
            \n
            \N{COPYRIGHT SIGN}Department of Industrial Engineering,
            Engineering Faculty,
            Brawijaya University
            2022
        '''
    )

    def __init__(
        self,
        width=20,
        height=20,
        initial_sme=100,
        initial_competitors=50,
        sme_growth=0.04,
        competitor_growth=0.05,
        competitor_gain_from_customer=20,
        profit=False,
        profit_regrowth_time=30,
        sme_gain_from_customer=4,
    ):
        """
        Create a new Competitor-SME model with the given parameters.

        Args:
            initial_sme: Number of sme to start with
            initial_competitors: Number of competitors to start with
            sme_growth: Probability of each sme reproducing each step
            competitor_growth: Probability of each competitor reproducing each step
            competitor_gain_from_customer: Energy a competitor gains from eating a sme
            profit: Whether to have the sme gain profit for opt_cost
            profit_regrowth_time: How long it takes for a profit patch to regrow
                                 once it is eaten
            sme_gain_from_customer: profit sme gain from profit, if enabled.
        """
        super().__init__()
        # Set parameters
        self.width = width
        self.height = height
        self.initial_sme = initial_sme
        self.initial_competitors = initial_competitors
        self.sme_growth = sme_growth
        self.competitor_growth = competitor_growth
        self.competitor_gain_from_customer = competitor_gain_from_customer
        self.profit = profit
        self.profit_regrowth_time = profit_regrowth_time
        self.sme_gain_from_customer = sme_gain_from_customer

        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        self.datacollector = DataCollector(
            {
                "Competitors": lambda m: m.schedule.get_type_count(Competitor),
                "SME": lambda m: m.schedule.get_type_count(SME),
                "Profits": lambda m: m.schedule.get_type_count(
                    Profit, lambda x: x.fully_grown
                ),
            }
        )

        # Create sme:
        for i in range(self.initial_sme):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            opt_cost = self.random.randrange(2 * self.sme_gain_from_customer)
            sme = SME(self.next_id(), (x, y), self, True, opt_cost)
            self.grid.place_agent(sme, (x, y))
            self.schedule.add(sme)

        # Create competitors
        for i in range(self.initial_competitors):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            opt_cost = self.random.randrange(2 * self.competitor_gain_from_customer)
            competitor = Competitor(self.next_id(), (x, y), self, True, opt_cost)
            self.grid.place_agent(competitor, (x, y))
            self.schedule.add(competitor)

        # Create profit patches
        if self.profit:
            for agent, x, y in self.grid.coord_iter():

                fully_grown = self.random.choice([True, False])

                if fully_grown:
                    countdown = self.profit_regrowth_time
                else:
                    countdown = self.random.randrange(self.profit_regrowth_time)

                patch = Profit(self.next_id(), (x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_type_count(Competitor),
                    self.schedule.get_type_count(SME),
                    self.schedule.get_type_count(Profit, lambda x: x.fully_grown),
                ]
            )

    def run_model(self, step_count=200):

        if self.verbose:
            print("Initial number competitors: ", self.schedule.get_type_count(Competitor))
            print("Initial number sme: ", self.schedule.get_type_count(SME))
            print(
                "Initial number profit: ",
                self.schedule.get_type_count(Profit, lambda x: x.fully_grown),
            )

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print("Final number competitors: ", self.schedule.get_type_count(Competitor))
            print("Final number sme: ", self.schedule.get_type_count(SME))
            print(
                "Final number profit: ",
                self.schedule.get_type_count(Profit, lambda x: x.fully_grown),
            )
