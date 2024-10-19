import random

from entities.session import Session

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
PERIODS = 4  # 4 пари на день


def find_suitable_lecturer(lecturers, subject, session_type):
    # Перевірка відповідності лекторам, які викладають потрібний предмет
    suitable_lecturers = [l for l in lecturers if subject.subject_id in l.subject_ids]
    if session_type == 'lecture':
        suitable_lecturers = [l for l in suitable_lecturers if l.can_teach_lecture]
    else:
        suitable_lecturers = [l for l in suitable_lecturers if l.can_teach_practice]

    # Додаткове відлагоджувальне повідомлення
    if not suitable_lecturers:
        print(
            f"Warning: No suitable lecturer found for subject {subject.subject_name} (ID: {subject.subject_id}) for {session_type}")
        print(f"Subject IDs that lecturers can teach: {[l.subject_ids for l in lecturers]}")
        print(f"Subject ID being matched: {subject.subject_id}")
    return random.choice(suitable_lecturers) if suitable_lecturers else None


def find_suitable_classroom(classrooms, capacity):
    suitable_classrooms = [c for c in classrooms if c.capacity >= capacity]
    if not suitable_classrooms:
        print(f"Warning: No suitable classroom found for capacity {capacity}")
    return random.choice(suitable_classrooms) if suitable_classrooms else None


def find_empty_slot(timetable):
    for day in DAYS:
        for period in range(1, PERIODS + 1):
            if not timetable[day][period]:
                return day, period
    print("Warning: No empty slot available")
    return None, None


def initialize_timetable(groups, subjects, lecturers, classrooms):
    timetable = {day: {period: [] for period in range(1, PERIODS + 1)} for day in DAYS}

    for group in groups:
        for subject in [s for s in subjects if s.group_id == group.group_id]:
            # Лекції
            lecturer = find_suitable_lecturer(lecturers, subject, session_type='lecture')
            if lecturer:
                classroom = find_suitable_classroom(classrooms, group.students)
                if classroom:
                    day, period = find_empty_slot(timetable)
                    if day and period:
                        session = Session(group, subject, lecturer, classroom, day, period, 'lecture')
                        timetable[day][period].append(session)
                        print(f"Scheduled: {session}")

            # Практичні заняття
            lecturer = find_suitable_lecturer(lecturers, subject, session_type='practice')
            if lecturer:
                classroom = find_suitable_classroom(classrooms, group.students // 2)  # для підгрупи
                if classroom:
                    day, period = find_empty_slot(timetable)
                    if day and period:
                        session = Session(group, subject, lecturer, classroom, day, period, 'practice')
                        timetable[day][period].append(session)
                        print(f"Scheduled: {session}")

    return timetable


