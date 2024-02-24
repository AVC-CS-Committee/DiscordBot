import random
import random

def deal_card():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return random.choice(cards)

def calculate_score(hand):
    if sum(hand) == 21 and len(hand) == 2:
        return 0
    if 11 in hand and sum(hand) > 21:
        hand.remove(11)
        hand.append(1)
    return sum(hand)

def blackjack():
    player_hand = []
    computer_hand = []

    for _ in range(2):
        player_hand.append(deal_card())
        computer_hand.append(deal_card())

    game_over = False

    while not game_over:
        player_score = calculate_score(player_hand)
        computer_score = calculate_score(computer_hand)

        return {'game_over': game_over, 'player_hand': player_hand, 'computer_hand': computer_hand, 'player_score': player_score, 'computer_score': computer_score}



def roulette():
    # Your roulette game logic here
    pass


def coinflip():
    return random.choice(['heads', 'tails'])