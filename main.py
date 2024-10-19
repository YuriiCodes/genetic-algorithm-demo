import pandas as pd

from entities.classroom import Classroom
from entities.group import Group
from entities.lecturer import Lecturer
from entities.subject import Subject
from genetic_scheduler import GeneticScheduler
from utils.initialize_timetable import initialize_timetable



def main():
    # Завантаження та парсинг CSV файлів
    groups_df = pd.read_csv('./inputs/group.csv')
    subjects_df = pd.read_csv('inputs/subjects.csv')
    lecturers_df = pd.read_csv('./inputs/lecturers.csv')
    classrooms_df = pd.read_csv('./inputs/classrooms.csv')

    # Створення об'єктів для кожної сутності
    groups = [Group(row['group_id'], row['students'], row['subgroups']) for _, row in groups_df.iterrows()]
    subjects = [Subject(row['group_id'], row['subject_id'], row['subject_name'], row['lecture_hours'],
                        row['practice_hours'], row['requires_subgroups']) for _, row in subjects_df.iterrows()]
    lecturers = [Lecturer(row['lecturer_id'], row['lecturer_name'], row['subject_ids'],
                          row['can_teach_lecture'], row['can_teach_practice']) for _, row in lecturers_df.iterrows()]
    classrooms = [Classroom(row['classroom_id'], row['capacity']) for _, row in classrooms_df.iterrows()]

    # Ініціалізація генетичного алгоритму
    scheduler = GeneticScheduler(groups, subjects, lecturers, classrooms, pop_size=10, generations=50,
                                 mutation_rate=0.2)

    # Виконання генетичного алгоритму
    best_timetable = scheduler.run()

    # Вивід найкращого розкладу
    for day, periods in best_timetable.items():
        print(f"\n{day}")
        for period, sessions in periods.items():
            print(f"  Period {period}: {sessions}")


if __name__ == '__main__':
    main()
