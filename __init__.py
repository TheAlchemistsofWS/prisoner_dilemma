from otree.api import *
import random


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner_tax'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 8
    PAYOFF_A = cu(5)
    PAYOFF_B = cu(3)
    PAYOFF_C = cu(1)
    PAYOFF_D = cu(0)
    PROBABILITY_0 = 0
    PROBABILITY_1 = 0.4
    SUBSIDY_1, SUBSIDY_2 = 2, 0
    TAX_1, TAX_2 = 0, 2

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    detection_roll = models.FloatField(initial=0)


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
    group.detection_roll = random.random()
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
    player.caught = False

    if player.group.detection_roll < C.PROBABILITY_1:
        if player.cooperate:
            if other.cooperate == False:
                if player.round_number <= 4:
                    player.payoff += C.SUBSIDY_1
                else:
                    player.payoff += C.SUBSIDY_2
        else:
            player.caught = True
            player.payoff = 0

    if player.round_number <= 4:
        player.payoff -= C.TAX_1
    else:
        player.payoff -= C.TAX_2


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
