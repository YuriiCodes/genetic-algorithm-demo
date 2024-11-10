import random
from entities.session import Session
from utils.initialize_timetable import initialize_balanced_timetable


class GeneticScheduler:
    def __init__(self, groups, subjects, lecturers, classrooms, pop_size=10, generations=50, mutation_rate=0.2):
        # Ініціалізація основних параметрів для генетичного алгоритму
        self.groups = groups
        self.subjects = subjects
        self.lecturers = lecturers
        self.classrooms = classrooms
        self.pop_size = pop_size  # Розмір популяції
        self.generations = generations  # Кількість поколінь
        self.mutation_rate = mutation_rate  # Ймовірність мутації
        self.reset_threshold = 5  # Порог для перезапуску популяції, якщо немає покращення
        self.reset_counter = 0  # Лічильник для перевірки застрягання на локальних оптимумах

    def fitness(self, timetable):
        score = 0
        penalty = 0
        session_count = {}

        for day in timetable:
            for period in range(1, 5):
                if period not in timetable[day]:
                    continue  # Skip if period is missing

                for session in timetable[day][period]:
                    group_id = session.group.group_id
                    subject_id = session.subject.subject_id
                    session_type = session.session_type

                    # Initialize if not already in the session count dictionary
                    if group_id not in session_count:
                        session_count[group_id] = {}
                    if subject_id not in session_count[group_id]:
                        session_count[group_id][subject_id] = {"lecture": 0, "practice": 0}

                    # Increment session count based on session type
                    session_count[group_id][subject_id][session_type] += 1

        # Calculating penalties based on required weekly sessions
        for group in self.groups:
            group_id = group.group_id
            for subject in [s for s in self.subjects if s.group_id == group_id]:
                subject_id = subject.subject_id
                required_lectures = 2  # Required lectures per week
                required_practices = 1 * group.subgroups  # Practices per subgroup

                actual_lectures = session_count.get(group_id, {}).get(subject_id, {}).get("lecture", 0)
                actual_practices = session_count.get(group_id, {}).get(subject_id, {}).get("practice", 0)

                # Penalize based on the difference between actual and required sessions
                penalty += abs(actual_lectures - required_lectures)
                penalty += abs(actual_practices - required_practices)

        score -= penalty  # Higher penalty lowers the fitness score
        return score

    def initialize_population(self):
        """
        Ініціалізація початкової популяції розкладів.
        Створює задану кількість розкладів у популяції.
        """
        return [initialize_balanced_timetable(self.groups, self.subjects, self.lecturers, self.classrooms) for _ in range(self.pop_size)]

    def crossover(self, parent1, parent2):
        """
        Операція кросоверу: створення нового розкладу шляхом поєднання батьківських розкладів.
        """
        # Порожній розклад для нового покоління
        child = {day: {period: [] for period in range(1, 5)} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        for day in child:
            crossover_point = random.randint(1, 3)  # Точка кросоверу в межах 1-3 періодів
            for period in range(1, 5):
                if period <= crossover_point:
                    child[day][period] = parent1[day][period]  # Наслідування від першого батька
                else:
                    child[day][period] = parent2[day][period]  # Наслідування від другого батька
        return child

    def mutate(self, timetable):
        """
        Операція мутації: випадкова зміна розкладу для додаткового дослідження можливих рішень.
        """
        for _ in range(random.randint(1, 3)):  # Випадкова кількість мутацій (1-3)
            day = random.choice(list(timetable.keys()))  # Вибір випадкового дня
            period = random.randint(1, 4)  # Вибір випадкового періоду
            # Випадкове очищення слота або додавання нового заняття
            timetable[day][period] = [] if timetable[day][period] else [self.random_session()]
        return timetable

    def random_session(self):
        """
        Генерує випадкову сесію для додавання в розклад під час мутації.
        """
        group = random.choice(self.groups)
        subject = random.choice([s for s in self.subjects if s.group_id == group.group_id])
        lecturer = random.choice([l for l in self.lecturers if subject.subject_id in l.subject_ids])
        classroom = random.choice([c for c in self.classrooms if c.capacity >= group.students])
        day = random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        period = random.randint(1, 4)
        session_type = 'lecture' if lecturer.can_teach_lecture else 'practice'
        return Session(group, subject, lecturer, classroom, day, period, session_type)

    def tournament_selection(self, population, fitnesses, k=3):
        """
        Турнірний відбір: вибір кращої особини з k випадкових особин.
        """
        selected = random.sample(list(zip(population, fitnesses)), k)  # Вибір k випадкових особин
        best_individual = max(selected, key=lambda x: x[1])  # Вибір особини з найвищим fitness
        return best_individual[0]

    def adaptive_mutation(self, max_fitness, best_score):
        """
        Адаптивна мутація: динамічна зміна ймовірності мутації та перезапуск популяції.
        """
        if max_fitness == best_score:
            self.reset_counter += 1
            if self.reset_counter >= self.reset_threshold:
                self.reset_counter = 0
                print("Resetting population to avoid local optima...")  # Повідомлення про перезапуск популяції
                return True  # Викликає повторну ініціалізацію
            else:
                self.mutation_rate = min(1.0, self.mutation_rate + 0.05)  # Збільшення ймовірності мутації
        else:
            self.reset_counter = 0
            self.mutation_rate = max(0.1, self.mutation_rate - 0.02)  # Зменшення ймовірності мутації
        return False

    def run(self):
        population = [initialize_balanced_timetable(self.groups, self.subjects, self.lecturers, self.classrooms)
                      for _ in range(self.pop_size)]
        population = [timetable for timetable in population if timetable is not None]  # Filter out None values

        best_score = float('-inf')
        best_individual = None

        for generation in range(self.generations):
            fitnesses = [self.fitness(timetable) for timetable in population]  # Calculate fitness for each individual
            max_fitness = max(fitnesses)  # Maximum fitness in the current generation

            if max_fitness > best_score:
                best_score = max_fitness
                best_individual = population[fitnesses.index(max_fitness)]

            print(f"Generation {generation + 1}, Best fitness: {max_fitness}")

            if self.adaptive_mutation(max_fitness, best_score):
                population = [initialize_balanced_timetable(self.groups, self.subjects, self.lecturers, self.classrooms)
                              for _ in range(self.pop_size)]
                population = [timetable for timetable in population if timetable is not None]  # Filter out None values
                continue

            # Elitism: carry over the best individual
            new_population = [best_individual]

            while len(new_population) < self.pop_size:
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                child = self.crossover(parent1, parent2)

                if random.random() < self.mutation_rate:
                    child = self.mutate(child)

                new_population.append(child)

            population = new_population  # Update population for next generation

        return best_individual
