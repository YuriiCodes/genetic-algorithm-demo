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
        """
        Функція оцінки розкладу.
        Обчислює кількість занять і зменшує кількість "вікон" у розкладі.
        """
        score = 0
        for day in timetable:
            # Створюємо список занять у кожний день
            sessions = [timetable[day][period] for period in range(1, 5) if timetable[day][period]]
            num_sessions = len(sessions)  # Кількість занять у день
            num_windows = sum(1 for i in range(len(sessions) - 1) if not sessions[i+1])  # Підрахунок "вікон"
            score += num_sessions - num_windows  # Оцінка: більше занять, менше "вікон"
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
        """
        Основний цикл генетичного алгоритму: ініціалізація популяції, відбір, кросовер, мутація, адаптивне навчання.
        """
        population = self.initialize_population()  # Початкова популяція
        best_score = 0  # Найкращий результат оцінки
        best_individual = None  # Найкращий розклад

        for generation in range(self.generations):
            fitnesses = [self.fitness(timetable) for timetable in population]  # Обчислення fitness для кожної особини
            max_fitness = max(fitnesses)  # Максимальний fitness у поточному поколінні

            if max_fitness > best_score:
                best_score = max_fitness  # Оновлення найкращого score
                best_individual = population[fitnesses.index(max_fitness)]  # Оновлення найкращого розкладу

            print(f"Generation {generation + 1}, Best fitness: {max_fitness}")  # Вивід результату

            # Повторна ініціалізація популяції при застряганні
            if self.adaptive_mutation(max_fitness, best_score):
                population = self.initialize_population()
                continue

            # Елітарний відбір: найкраща особина автоматично переходить у нове покоління
            new_population = [best_individual]

            # Генерація нового покоління
            while len(new_population) < self.pop_size:
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                child = self.crossover(parent1, parent2)

                if random.random() < self.mutation_rate:  # Перевірка на мутацію
                    child = self.mutate(child)

                new_population.append(child)

            population = new_population  # Оновлення популяції для наступного покоління

        return best_individual  # Повернення найкращого розкладу після завершення алгоритму
