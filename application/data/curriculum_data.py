from __future__ import annotations

from typing import Any, Dict

from ..utitily import SillyDB
from .orm import (
    DECLARATIVE_BASE,
    SubjectPartition,
    Curriculum,
    Teacher,
    ScheduledSubject,
    Room,
    RoomGroup,
    TermNumber,
    Time,
    Day,
    LessonType,
    Group,
    Lesson,
    SubjectTitle,
)
from .descriptions import (
    ColumnDescription,
    ListColumnDescription,
    ForeignKeyColumnDescription,
    TableDescription,
)


def represent_subject(obj: SubjectPartition):
    annotation = ""
    match obj.lesson_type_id:
        case 1:
            annotation = " (лекц.)"
        case 2:
            annotation = " (практ.)"
        case 3:
            annotation = " (лаб.)"

    return obj.name + annotation


class Data(SillyDB):
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, name):
        self._path = name

        self.set_source()

        self.make_terms()
        self.make_lesson_types()
        self.make_times()
        self.make_days()

    _table_descriptions: Dict[Any, TableDescription] = {
        Curriculum: TableDescription(
            "Учебные планы", ColumnDescription("name", "Название")
        ),
        Teacher: TableDescription(
            "Преподаватели",
            ColumnDescription("last_name", "Фамилия"),
            ColumnDescription("first_name", "Имя"),
            ColumnDescription("second_name", "Отчество"),
            ListColumnDescription(
                SubjectPartition,
                "subject_partitions",
                "Может преподавать дисциплины",
                represent_subject,
            ),
        ),
        SubjectTitle: TableDescription(
            "Дисциплины", ColumnDescription("value", "Название")
        ),
        SubjectPartition: TableDescription(
            "Дисциплины",
            ForeignKeyColumnDescription(SubjectTitle, "title_id", "Название"),
            ForeignKeyColumnDescription(LessonType, "lesson_type_id", "Форма"),
            ListColumnDescription(
                Teacher,
                "teachers",
                "Преподаватели этой дисциплины",
                lambda obj: f"{obj.last_name} {obj.first_name[0]}. {obj.second_name[0]}.",
            ),
            ListColumnDescription(
                RoomGroup, "room_groups", "Категории аудиторий", lambda obj: obj.name
            ),
        ),
        Group: TableDescription(
            "Группы",
            ColumnDescription("name", "Название"),
            ForeignKeyColumnDescription(Curriculum, "curriculum_id", "Специальность"),
        ),
        ScheduledSubject: TableDescription(
            "Предметы",
            ForeignKeyColumnDescription(
                Curriculum, "curriculum_id", "Учебный план", as_filter=True
            ),
            ForeignKeyColumnDescription(
                TermNumber, "term_number_id", "Семестр", as_filter=True
            ),
            ForeignKeyColumnDescription(
                SubjectPartition, "subject_partition_id", "Название", represent_subject
            ),
            ColumnDescription("count", "Количество"),
        ),
        Room: TableDescription(
            "Аудитории",
            ColumnDescription("building", "Корпус"),
            ColumnDescription("room", "Аудитория"),
            ListColumnDescription(
                RoomGroup, "groups", "Категория", lambda obj: obj.name
            ),
        ),
        RoomGroup: TableDescription(
            "Категории аудиторий",
            ColumnDescription("name", "Название"),
            ListColumnDescription(
                Room,
                "rooms",
                "Аудитории",
                lambda obj: f"к. {obj.building}, а. {obj.room}",
            ),
            ListColumnDescription(
                SubjectPartition, "subject_partitions", "Дисциплины", represent_subject
            ),
        ),
        Lesson: TableDescription(
            "Расписание",
            ForeignKeyColumnDescription(Group, "group_id", "Группа", as_filter=True),
            ForeignKeyColumnDescription(Day, "day_id", "День", as_filter=True),
            ForeignKeyColumnDescription(Time, "time_id", "Время"),
            ForeignKeyColumnDescription(
                SubjectPartition,
                "subject_partition_id",
                "Предмет",
                represent=represent_subject,
            ),
            ForeignKeyColumnDescription(
                Teacher,
                "teacher_id",
                "Преподаватель",
                represent=lambda obj: f"{obj.last_name} {obj.first_name[0]}. {obj.second_name[0]}.",
            ),
            ForeignKeyColumnDescription(
                Room,
                "room_id",
                "Аудитория",
                represent=lambda obj: f"к. {obj.building}, а. {obj.room}",
            ),
        ),
    }

    @property
    def table_descriptions(self) -> Dict[Any, TableDescription]:
        return self._table_descriptions

    def make_terms(self):
        with self.get_session() as session:
            terms = session.query(TermNumber).all()
            if not terms:
                for i in range(10):
                    term_num = TermNumber(id=i, value=str(i + 1))
                    session.add(term_num)

            session.commit()

    def make_times(self):
        with self.get_session() as session:
            times = session.query(Time).all()
            if len(times) <= 0:
                for item in (
                    "8:00-9:30",
                    "9:55-11:30",
                    "11:40-13:15",
                    "13:55-15:30",
                    "15:40-17:15",
                ):
                    time = Time(value=item)
                    session.add(time)

        session.commit()

    def make_lesson_types(self):
        with self.get_session() as session:
            lesson_types = session.query(LessonType).all()
            if not lesson_types:
                session.add(LessonType(name="Лекц."))
                session.add(LessonType(name="Практ."))
                session.add(LessonType(name="Лаб."))
                session.commit()

    def make_days(self):
        with self.get_session() as session:
            days = session.query(Day).all()
            if len(days) <= 0:
                for item in (
                    "Понедельник",
                    "Вторник",
                    "Среда",
                    "Четверг",
                    "Пятница",
                    "Суббота",
                ):
                    time = Day(value=item)
                    session.add(time)

        session.commit()

    def __init__(self, db_file_name: str):
        super().__init__(DECLARATIVE_BASE)
