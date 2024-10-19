import random

from entities.session import Session
from utils.initialize_timetable import initialize_timetable


class GeneticScheduler:
    def __init__(self, groups, subjects, lecturers, classrooms, pop_size=10, generations=50, mutation_rate=0.2):
        self.groups = groups
        self.subjects = subjects
        self.lecturers = lecturers
        self.classrooms = classrooms
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.reset_threshold = 5  # Порог зупинки
        self.reset_counter = 0

    def fitness(self, timetable):
        score = 0
        for day in timetable:
            sessions = [timetable[day][period] for period in range(1, 5) if timetable[day][period]]
            num_sessions = len(sessions)
            num_windows = sum(1 for i in range(len(sessions) - 1) if not sessions[i+1])
            score += num_sessions - num_windows
        return score

    def initialize_population(self):
        return [initialize_timetable(self.groups, self.subjects, self.lecturers, self.classrooms) for _ in range(self.pop_size)]

    def crossover(self, parent1, parent2):
        child = {day: {period: [] for period in range(1, 5)} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        for day in child:
            crossover_point = random.randint(1, 3)
            for period in range(1, 5):
                if period <= crossover_point:
                    child[day][period] = parent1[day][period]
                else:
                    child[day][period] = parent2[day][period]
        return child

    def mutate(self, timetable):
        for _ in range(random.randint(1, 3)):
            day = random.choice(list(timetable.keys()))
            period = random.randint(1, 4)
            timetable[day][period] = [] if timetable[day][period] else [self.random_session()]
        return timetable

    def random_session(self):
        group = random.choice(self.groups)
        subject = random.choice([s for s in self.subjects if s.group_id == group.group_id])
        lecturer = random.choice([l for l in self.lecturers if subject.subject_id in l.subject_ids])
        classroom = random.choice([c for c in self.classrooms if c.capacity >= group.students])
        day = random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        period = random.randint(1, 4)
        session_type = 'lecture' if lecturer.can_teach_lecture else 'practice'
        return Session(group, subject, lecturer, classroom, day, period, session_type)

    def tournament_selection(self, population, fitnesses, k=3):
        selected = random.sample(list(zip(population, fitnesses)), k)
        best_individual = max(selected, key=lambda x: x[1])
        return best_individual[0]

    def adaptive_mutation(self, max_fitness, best_score):
        if max_fitness == best_score:
            self.reset_counter += 1
            if self.reset_counter >= self.reset_threshold:
                self.reset_counter = 0
                print("Resetting population to avoid local optima...")
                return True  # Викликає повторну ініціалізацію
            else:
                self.mutation_rate = min(1.0, self.mutation_rate + 0.05)
        else:
            self.reset_counter = 0
            self.mutation_rate = max(0.1, self.mutation_rate - 0.02)
        return False

    def run(self):
        population = self.initialize_population()
        best_score = 0
        best_individual = None

        for generation in range(self.generations):
            fitnesses = [self.fitness(timetable) for timetable in population]
            max_fitness = max(fitnesses)

            if max_fitness > best_score:
                best_score = max_fitness
                best_individual = population[fitnesses.index(max_fitness)]

            print(f"Generation {generation + 1}, Best fitness: {max_fitness}")

            # Повторна ініціалізація популяції
            if self.adaptive_mutation(max_fitness, best_score):
                population = self.initialize_population()
                continue

            # Елітарний відбір
            new_population = [best_individual]

            # Генерація нового покоління
            while len(new_population) < self.pop_size:
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                child = self.crossover(parent1, parent2)

                if random.random() < self.mutation_rate:
                    child = self.mutate(child)

                new_population.append(child)

            population = new_population

        return best_individual
