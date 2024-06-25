import pandas as pd
import numpy as np
import random

# 常量定義
ACTIONS = ['fold', 'call', 'raise', 'all-in']
GENES_PER_INDIVIDUAL = 40
INITIAL_POPULATION_SIZE = 280
NUM_GENERATIONS = 900
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.05
small_blind_amount = 10
big_blind_amount = 20

class StrategyOptimizer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.historical_data_by_position = self.create_historical_data()
        self.expected_values_by_position = self.calculate_expected_values()
        self.position_strategies = {}

    def create_historical_data(self):
        historical_data_by_position = {
            'Button': {'fold': [], 'call': [], 'raise': [], 'all-in': []},
            'Small Blind': {'fold': [], 'call': [], 'raise': [], 'all-in': []},
            'Big Blind': {'fold': [], 'call': [], 'raise': [], 'all-in': []},
            'UTG': {'fold': [], 'call': [], 'raise': [], 'all-in': []},
            'HighJack': {'fold': [], 'call': [], 'raise': [], 'all-in': []},
            'CutOff': {'fold': [], 'call': [], 'raise': [], 'all-in': []}
        }
        raise_sizes_by_position = {position: [] for position in historical_data_by_position.keys()}

        for index, row in self.data.iterrows():
            for position in historical_data_by_position.keys():
                hand1 = row[f'{position} Hand 1']
                hand2 = row[f'{position} Hand 2']
                for num_cards in [0, 3, 4, 5]:
                    community_cards = [row[f'Community Card {i+1}'] for i in range(num_cards)]
                    hand_value = self.calculate_hand_value([hand1, hand2] + community_cards)
                    action = random.choice(ACTIONS)
                    historical_data_by_position[position][action].append((num_cards, hand_value))

                    if action == 'raise':
                        raise_size = random.randint(1, 3) * big_blind_amount
                        raise_sizes_by_position[position].append(raise_size)

        for position in historical_data_by_position:
            for action in historical_data_by_position[position]:
                if historical_data_by_position[position][action]:
                    historical_data_by_position[position][action] = np.array(historical_data_by_position[position][action])
                else:
                    historical_data_by_position[position][action] = np.array([(0, 0)])

        self.raise_sizes_by_position = raise_sizes_by_position

        return historical_data_by_position

    def calculate_hand_value(self, cards):
        ranks = '23456789TJQKA'
        suits = 'CDHS'

        def card_value(card):
            try:
                rank, suit = card.split(' of ')
                suit = suit[0]
                if rank == '10':
                    rank = 'T'
                if rank not in ranks or suit not in suits:
                    raise ValueError(f"Invalid card format: {card}")
                return ranks.index(rank), suits.index(suit)
            except ValueError:
                raise ValueError(f"Invalid card format: {card}")

        values = sorted([card_value(card) for card in cards], reverse=True)
        hand_ranks = [value[0] for value in values]
        hand_suits = [value[1] for value in values]

        is_flush = len(set(hand_suits)) == 1
        is_straight = all(hand_ranks[i] - hand_ranks[i+1] == 1 for i in range(len(hand_ranks) - 1))
        rank_counts = {rank: hand_ranks.count(rank) for rank in set(hand_ranks)}
        if is_flush and is_straight:
            return 8
        elif 4 in rank_counts.values():
            return 7
        elif 3 in rank_counts.values() and 2 in rank_counts.values():
            return 6
        elif is_flush:
            return 5
        elif is_straight:
            return 4
        elif 3 in rank_counts.values():
            return 3
        elif list(rank_counts.values()).count(2) == 2:
            return 2
        elif 2 in rank_counts.values():
            return 1
        else:
            return 0

    def calculate_expected_values(self):
        expected_values_by_position = {}
        for position in self.historical_data_by_position:
            expected_values_by_position[position] = {}
            for action in ACTIONS:
                values_by_num_cards = {}
                for num_cards in range(3, 6):
                    values = [value for nc, value in self.historical_data_by_position[position][action] if nc == num_cards]
                    if values:
                        values_by_num_cards[num_cards] = np.mean(values)
                    else:
                        values_by_num_cards[num_cards] = 0
                expected_values_by_position[position][action] = values_by_num_cards

            if self.raise_sizes_by_position[position]:
                expected_values_by_position[position]['raise_size'] = np.mean(self.raise_sizes_by_position[position])
            else:
                expected_values_by_position[position]['raise_size'] = big_blind_amount

        return expected_values_by_position

    def generate_individual_for_position(self, position):
        individual = []
        for _ in range(GENES_PER_INDIVIDUAL):
            action = random.choice(ACTIONS)
            # 從歷史數據中選擇一個隨機的手牌價值
            hand_value = random.choice(self.historical_data_by_position[position][action])[-1]
            gene = {
                'position': position,
                'action': action,
                'hand_value': hand_value
            }
            individual.append(gene)
        return individual

    def initialize_population_for_position(self, position, size):
        population = []
        for _ in range(size):
            population.append(self.generate_individual_for_position(position))
        return population

    def evaluate_fitness_for_position(self, strategy, position, small_blind=10, big_blind=20):
        position_weights = {
            'Button': 1.8,
            'Small Blind': 1.2,
            'Big Blind': 1.0,
            'CutOff': 0.9,
            'HighJack': 0.7,
            'UTG': 0.6,
        }

        pot_size = small_blind + big_blind

        total_ev = 0
        for rule in strategy:
            action = rule['action']
            hand_value = rule['hand_value']
            action_values = self.expected_values_by_position[position][action].values()
            action_value = sum(action_values) / len(action_values)

            hand_value_weight = 1.0
            if action == 'fold':
                hand_value_weight = 0.1
            elif action == 'call':
                hand_value_weight = 0.5
            elif action == 'raise':
                hand_value_weight = 0.8
            elif action == 'all-in':
                hand_value_weight = 1.0

            if position == 'Button':
                action_value *= pot_size
            elif position == 'Small Blind':
                action_value *= (pot_size + small_blind)
            elif position == 'Big Blind':
                action_value *= (pot_size + big_blind)
            else:
                action_value *= pot_size

            action_value *= hand_value_weight * hand_value

            total_ev += action_value

        total_ev *= position_weights[position]

        return total_ev

    def select_parents(self, population, fitness_scores, num_parents):
        selected_parents = random.choices(population, weights=fitness_scores, k=num_parents)
        return selected_parents

    def crossover(self, parent1, parent2, num_points=2):
        if random.random() > CROSSOVER_RATE:
            # 不進行交叉，直接返回原始父代
            return parent1, parent2

        # 選擇 num_points 個隨機交叉點並排序
        crossover_points = sorted(random.sample(range(GENES_PER_INDIVIDUAL), num_points))

        # 初始化子代
        child1, child2 = [], []

        last_point = 0
        # 交替交換片段
        for i, point in enumerate(crossover_points):
            if i % 2 == 0:
                child1.extend(parent1[last_point:point])
                child2.extend(parent2[last_point:point])
            else:
                child1.extend(parent2[last_point:point])
                child2.extend(parent1[last_point:point])
            last_point = point

        # 添加最後一段
        if num_points % 2 == 0:
            child1.extend(parent1[last_point:])
            child2.extend(parent2[last_point:])
        else:
            child1.extend(parent2[last_point:])
            child2.extend(parent1[last_point:])

        return child1, child2

    def mutate(self, individual, mutation_rate):
        for gene in individual:
            if random.random() < mutation_rate:
                gene['action'] = random.choice(ACTIONS)
        return individual

    def create_new_population_for_position(self, population, position, fitness_scores, mutation_rate, crossover_rate):
        new_population = []
        num_parents = len(population) // 2 * 2
        parents = self.select_parents(population, fitness_scores, num_parents)
        for i in range(0, num_parents, 2):
            parent1, parent2 = parents[i], parents[i + 1]
            if random.random() < crossover_rate:
                child1, child2 = self.crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            new_population.append(self.mutate(child1, mutation_rate))
            new_population.append(self.mutate(child2, mutation_rate))
        return new_population

    def optimize_strategy(self):
        positions = ['Button', 'Small Blind', 'Big Blind', 'UTG', 'HighJack', 'CutOff']
        for position in positions:
            print(f"Optimizing strategy for {position}")
            population = self.initialize_population_for_position(position, INITIAL_POPULATION_SIZE)
            for generation in range(NUM_GENERATIONS):
                fitness_scores = [self.evaluate_fitness_for_position(individual, position) for individual in population]
                population = self.create_new_population_for_position(population, position, fitness_scores, MUTATION_RATE, CROSSOVER_RATE)
            best_strategy = population[fitness_scores.index(max(fitness_scores))]
            self.position_strategies[position] = best_strategy

    def get_best_strategies(self):
        return self.position_strategies

    def recommend_action(self, position, hand, community_cards, initial_funds, remaining_funds, pot_size):
        if position not in self.position_strategies:
            raise ValueError(f"Position {position} not found in strategies.")

        initial_funds = float(initial_funds)
        remaining_funds = float(remaining_funds)
        pot_size = float(pot_size)

        hand = [card for card in hand if ' of ' in card and card.split(' of ')[0] in '23456789TJQKA' and card.split(' of ')[1][0] in 'CDHS']
        community_cards = [card for card in community_cards if ' of ' in card and card.split(' of ')[0] in '23456789TJQKA' and card.split(' of ')[1][0] in 'CDHS']
        hand_value = self.calculate_hand_value(hand + community_cards)

        best_strategy = self.position_strategies[position]
        action_values = {action: 0 for action in ACTIONS}
        raise_sizes = []

        for gene in best_strategy:
            if gene['hand_value'] == hand_value:
                action_values[gene['action']] += 1

                if gene['action'] == 'raise':
                    raise_size = self.expected_values_by_position[position]['raise_size']
                    raise_sizes.append(raise_size)

        if remaining_funds < big_blind_amount:
            if hand_value > 3:
                recommended_action = 'all-in'
            else:
                recommended_action = 'fold'
        elif remaining_funds <= small_blind_amount * 2:
            if hand_value > 2:
                recommended_action = 'all-in'
            else:
                recommended_action = 'fold'
        else:
            if hand_value < 5:
                action_values.pop('all-in', None)

            for action in action_values:
                action_values[action] *= (pot_size / (pot_size + remaining_funds))

            recommended_action = max(action_values, key=action_values.get)

        if recommended_action == 'raise':
            average_raise_size = sum(raise_sizes) / len(raise_sizes) if raise_sizes else big_blind_amount
            if remaining_funds < average_raise_size:
                recommended_action = 'call' if remaining_funds >= big_blind_amount else 'fold'
            return recommended_action, int(average_raise_size)

        return recommended_action
