from otree.api import *
import random


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 8
    PAYOFF_A = cu(5)
    PAYOFF_B = cu(3)
    PAYOFF_C = cu(1)
    PAYOFF_D = cu(0)
    PROBABILITY_0 = 0
    PROBABILITY_1 = 0.4
    SUBSIDY_1, SUBSIDY_2 = 2, 1
    TAX_1, TAX_2 = 1, 2
    NUM_ROUNDS = 4

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )
    caught = models.BooleanField(initial=True)
    total_payoff = models.CurrencyField(initial=0)

# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)



def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }
    other = other_player(player)
    player.payoff = payoff_matrix[(player.cooperate, other.cooperate)]
    t = random.random()

    if player.cooperate and  other.cooperate == False and t < C.PROBABILITY_1:
        player.payoff += C.SUBSIDY_1 if player.round_number <= 4 else C.SUBSIDY_2

    if t < C.PROBABILITY_1 and player.cooperate == False:
        player.payoff = 0  # Наказание за выбор "defect"
        player.caught = True
    else:
        player.caught = False

    if player.round_number <= 4:
        player.payoff -= C.TAX_1
    else:
        player.payoff -= C.TAX_2

    player.total_payoff += player.payoff

# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        opponent = other_player(player)
        return dict(
            opponent=opponent,
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
            caught=player.caught,
            total_payoff=player.total_payoff,
        )


page_sequence = [Introduction, Decision, ResultsWaitPage, Results]
