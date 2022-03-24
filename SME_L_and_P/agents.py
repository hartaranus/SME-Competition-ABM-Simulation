from mesa import Agent
from SME_L_and_P.random_walk import RandomWalker


class SME(RandomWalker):
    """
    An SME that operates, gain profit and lossess.

    Initialized By the RandomWalker.
    """
    opt_cost = None

    def __init__(self, unique_id, pos, model, moore, opt_cost=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.opt_cost = opt_cost

    def step(self):
        """
        A model step. Operates, then gain profit and grow.
        """
        self.random_move()
        isOperating = True

        if self.model.profit:
            # Reduce opt_cost
            self.opt_cost -= 1

            # If there is profit available to be gained, get it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            profit_patch = [obj for obj in this_cell if isinstance(obj, Profit)][0]
            if profit_patch.fully_grown:
                self.opt_cost += self.model.sme_gain_from_customer
                profit_patch.fully_grown = False

            # Death
            if self.opt_cost < 0:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)
                isOperating = False

        if isOperating and self.random.random() < self.model.sme_growth:
            # Create a new SME:
            if self.model.profit:
                self.opt_cost /= 2
            smes = SME(
                self.model.next_id(), self.pos, self.model, self.moore, self.opt_cost
            )
            self.model.grid.place_agent(smes, self.pos)
            self.model.schedule.add(smes)


class Competitor(RandomWalker):
    """
    A Competitor that might be encountered by each SME at any point in time (caused by competitors).
    """

    opt_cost = None

    def __init__(self, unique_id, pos, model, moore, opt_cost=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.opt_cost = opt_cost

    def step(self):
        self.random_move()
        self.opt_cost -= 1

        # If there are SME present, eat one
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        smes = [obj for obj in this_cell if isinstance(obj, SME)]
        if len(smes) > 0:
            sme_to_beat = self.random.choice(smes)
            self.opt_cost += self.model.competitor_gain_from_customer
            # Kill the SME
            self.model.grid._remove_agent(self.pos, sme_to_beat)
            self.model.schedule.remove(sme_to_beat)

        # Competitor Fall or Creation
        if self.opt_cost < 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
        else:
            if self.random.random() < self.model.competitor_growth:
                # Create a new competitor group
                self.opt_cost /= 2
                cub = Competitor(
                    self.model.next_id(), self.pos, self.model, self.moore, self.opt_cost
                )
                self.model.grid.place_agent(cub, cub.pos)
                self.model.schedule.add(cub)


class Profit(Agent):
    """
    A patch of profit that grows at a fixed rate and it is gained by the SME
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of profit

        a patch of profit = > a set of profitable operations (sales,etc)

        Args:
            grown: (boolean) Whether the patch of profit is fully grown or not
            countdown: Time for the patch of profit to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.profit_regrowth_time
            else:
                self.countdown -= 1
