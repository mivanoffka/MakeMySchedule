import random
from typing import Dict, Any, List, Optional, Sequence, Tuple
from functools import reduce

from sqlalchemy.orm import Session

from application.data.orm import Lesson

from ..task import ObservableTask, ObservableTaskResult
from ...data import (
    Data,
    Teacher,
    Curriculum,
    SubjectPartition,
    ScheduledSubject,
    Time,
    Day,
    Group,
    LessonType,
    Room,
)

LECTURE_ID = 1
PRACTICE_ID = 2
LABORATORY_ID = 3


class LessonPrecursor:
    group_ids: Sequence[int]
    day_id: int
    time_id: int
    subject_partition_id: int
    teacher_id: int
    room_id: int

    def __init__(
        self,
        group_ids: Sequence[int],
        day_id: int,
        time_id: int,
        subject_partition_id: int,
        teacher_id: int,
        room_id: int,
    ):
        self.group_ids = group_ids
        self.day_id = day_id
        self.time_id = time_id
        self.subject_partition_id = subject_partition_id
        self.teacher_id = teacher_id
        self.room_id = room_id


class ComposerTask(ObservableTask):
    _curriculum_data: Data
    _session: Session
    _curriculum: Dict[str, Any]
    _population_size: int
    _generations_count: int
    _mutation_rate: float
    _schedules: List[List[LessonPrecursor]]
    _best_schedule: List[LessonPrecursor]

    def __init__(
        self,
        data: Data,
        population_size: int,
        generations_count: int,
        mutation_rate: float,
    ):  
        self._curriculum_data = data
        self._session = self._curriculum_data.get_session()
        self._population_size = int(population_size)
        self._generations_count = int(generations_count)
        self._mutation_rate = mutation_rate
        self._schedules = []

    def _initialize_progress_units(self): ...

    def create_new_schedule(self) -> List[LessonPrecursor]:
        schedule = []
        times = self._session.query(Time).all()
        days = self._session.query(Day).all()
        for curriculum in self._session.query(Curriculum).all():
            curriculum: Curriculum = curriculum
            groups_for_curriculum = (
                self._session.query(Group).filter_by(curriculum_id=curriculum.id).all()
            )
            subjects_for_term = (
                self._session.query(ScheduledSubject)
                .filter(
                    ScheduledSubject.term_number_id == 0,
                    ScheduledSubject.curriculum_id == curriculum.id,
                )
                .all()
            )

            for subject_for_term in subjects_for_term:
                subject_for_term: ScheduledSubject = subject_for_term

                subject_itself: Optional[SubjectPartition] = (
                    self._session.query(SubjectPartition)
                    .filter_by(id=subject_for_term.subject_partition_id)
                    .first()
                )

                if subject_itself is None:
                    continue

                allowed_teachers = subject_itself.teachers
                allowed_room_groups = subject_itself.room_groups

                allowed_rooms_list = []
                for room_group in allowed_room_groups:
                    lst = room_group.rooms
                    allowed_rooms_list.append(lst)

                allowed_rooms = list(
                    reduce(lambda a, b: set(a).intersection(b), allowed_rooms_list)
                )

                lesson_type_id: int = int(subject_itself.lesson_type_id)

                if lesson_type_id == PRACTICE_ID:
                    for group in groups_for_curriculum:
                        for i in range(subject_for_term.count):
                            if subject_itself is not None:
                                teacher = random.choice(allowed_teachers)
                                time = random.choice(times)
                                room = random.choice(allowed_rooms)
                                day = random.choice(days)
                                lesson = LessonPrecursor(
                                    group_ids=(group.id,),
                                    subject_partition_id=subject_itself.id,
                                    time_id=time.id,
                                    teacher_id=teacher.id,
                                    room_id=room.id,
                                    day_id=day.id,
                                )
                                schedule.append(lesson)

                elif lesson_type_id == LABORATORY_ID:
                    for group in groups_for_curriculum:
                        for i in range(subject_for_term.count * 2):
                            if subject_itself is not None:
                                teacher = random.choice(allowed_teachers)
                                time = random.choice(times)
                                room = random.choice(allowed_rooms)
                                day = random.choice(days)
                                lesson = LessonPrecursor(
                                    group_ids=(group.id,),
                                    subject_partition_id=subject_itself.id,
                                    time_id=time.id,
                                    teacher_id=teacher.id,
                                    room_id=room.id,
                                    day_id=day.id,
                                )
                                schedule.append(lesson)

                elif lesson_type_id == LECTURE_ID:
                    group_ids = []
                    for group in groups_for_curriculum:
                        group_ids.append(group.id)
                    group_ids = tuple(group_ids)

                    for i in range(subject_for_term.count):
                        teacher = random.choice(allowed_teachers)
                        time = random.choice(times)
                        room = random.choice(allowed_rooms)
                        day = random.choice(days)
                        lesson = LessonPrecursor(
                            group_ids=group_ids,
                            subject_partition_id=subject_itself.id,
                            time_id=time.id,
                            teacher_id=teacher.id,
                            room_id=room.id,
                            day_id=day.id,
                        )
                        schedule.append(lesson)
                else:
                    ...
        return schedule

    def mutate(self, schedule):
        index = random.randint(0, len(schedule) - 1)
        lesson = schedule[index]
        subject = (
            self._session.query(SubjectPartition)
            .filter_by(id=lesson.subject_partition_id)
            .first()
        )

        if subject is None:
            return

        teachers = subject.teachers

        allowed_room_groups = subject.room_groups

        allowed_rooms_list = []
        for room_group in allowed_room_groups:
            lst = room_group.rooms
            allowed_rooms_list.append(lst)

        allowed_rooms = list(
            reduce(lambda a, b: set(a).intersection(b), allowed_rooms_list)
        )

        times = self._session.query(Time).all()
        days = self._session.query(Day).all()

        lesson.day = random.choice(days)
        lesson.teacher = random.choice(teachers)
        lesson.room = random.choice(allowed_rooms)
        lesson.time = random.choice(times)

        schedule[index] = lesson

    def check(self, schedule):
        score = 0

        teacher_for_time = []
        room_for_time = []
        group_for_time = []

        for lesson in schedule:
            room_id = lesson.room_id
            teacher_id = lesson.teacher_id
            day_id = lesson.day_id
            time_id = lesson.time_id
            subject_id = lesson.subject_partition_id
            group_ids = lesson.group_ids

            if (teacher_id, day_id, time_id) in teacher_for_time:
                score -= 1
            else:
                teacher_for_time.append((teacher_id, day_id, time_id))

            if (room_id, day_id, time_id) in room_for_time:
                score -= 1
                room_for_time.append((room_id, day_id, time_id))

            tuples = tuple((group_id, day_id, time_id) for group_id in group_ids)
            
            for group_id in group_ids:
                if (group_id, day_id, time_id) in group_for_time:
                    score -= 1
                else:
                    for t in tuples:
                        group_for_time.append(t)
                    break

        return score

    def crossover(self, first, second):
        child = []
        for i in range(len(first)):
            value = first[i] if random.random() > 0.5 else second[i]
            child.append(value)
        return child

    def execute(self) -> ObservableTaskResult:
        self._schedules = [
            self.create_new_schedule() for _ in range(self._population_size)
        ]

        for generation in range(self._generations_count):
            self._schedules.sort(
                key=lambda schedule: self.check(schedule), reverse=True
            )

            self.make_message(
                f"Generation {generation + 1}: Best fitness {self.check(self._schedules[0])}"
            )

            # Если найдено хорошее решение
            if (
                self.check(self._schedules[0]) == 0
                or generation == self._generations_count - 1
            ):
                # self.print_schedule(self._schedules[0])
                self._best_schedule = self._schedules[0]
                self.save_to_db()
                schedule = self._session.query(Lesson).all()
                self.print_schedule(schedule)
                break

            # Селекция: берем 50% лучших особей
            next_generation = self._schedules[: self._population_size // 2]

            # Скрещивание: создаем новое поколение на основе лучших
            while len(next_generation) < self._population_size:
                parent1, parent2 = random.sample(
                    self._schedules[: self._population_size // 2], 2
                )
                child = self.crossover(parent1, parent2)
                if random.random() < self._mutation_rate:
                    self.mutate(child)
                next_generation.append(child)

            # Замена популяции
            self._schedules = next_generation

        return ObservableTaskResult(None, None, None, None)

    def save_to_db(self):
        if self._best_schedule:
            with self._session as session:
                session.query(Lesson).delete()
                session.commit()

                for lesson in self._best_schedule:
                    lesson: LessonPrecursor = lesson

                    for group_id in lesson.group_ids:
                        orm_lesson = Lesson(
                            group_id=group_id,
                            subject_partition_id=lesson.subject_partition_id,
                            time_id=lesson.time_id,
                            teacher_id=lesson.teacher_id,
                            room_id=lesson.room_id,
                            day_id=lesson.day_id,
                        )

                        session.add(orm_lesson)
                    session.commit()

    def print_schedule(self, schedule):

        total_curricula = self._session.query(Curriculum).all()
        days = self._session.query(Day).all()
        times = self._session.query(Time).all()

        for curriculum in total_curricula:
            print(f"{curriculum.name}")
            curriculum_groups = (
                self._session.query(Group).filter_by(curriculum_id=curriculum.id).all()
            )
            for group in curriculum_groups:
                print(f"   гр. {group.name}")
                lessons = tuple(
                    lesson for lesson in schedule if lesson.group_id == group.id
                )
                for day in days:
                    print(f"      {day.value}")
                    lessons_for_day = tuple(
                        lesson for lesson in lessons if lesson.day_id == day.id
                    )
                    for time in times:
                        lessons_for_time = tuple(
                            lesson
                            for lesson in lessons_for_day
                            if lesson.time_id == time.id
                        )
                        for lesson in lessons_for_time:
                            subject = (
                                self._session.query(SubjectPartition)
                                .filter_by(id=lesson.subject_partition_id)
                                .first()
                            )
                            if subject is None:
                                continue

                            subject_type = (
                                self._session.query(LessonType)
                                .filter_by(id=subject.lesson_type_id)
                                .first()
                            )

                            if subject_type is None:
                                continue

                            teacher = (
                                self._session.query(Teacher)
                                .filter_by(id=lesson.teacher_id)
                                .first()
                            )

                            if teacher is None:
                                continue

                            room = (
                                self._session.query(Room)
                                .filter_by(id=lesson.room_id)
                                .first()
                            )

                            if room is None:
                                continue

                            teacher_name = f"{teacher.last_name} {teacher.first_name[0]}.{teacher.second_name[0]}."
                            room_name = f"к.{room.building}, а.{room.room}"
                            print(
                                f"         {time.value}: {subject.name} ({subject_type.name.lower()}), {teacher_name}, {room_name}"
                            )
            print()
