from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

DECLARATIVE_BASE = declarative_base()


teacher_subject_association = Table(
    'teacher_subject', DECLARATIVE_BASE.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), nullable=True),
    Column('subject_id', Integer, ForeignKey('subject_partitions.id'), nullable=True),
)

room_types_subject_partitions_association = Table(
    'room_groups_to_subject_partitions', DECLARATIVE_BASE.metadata,
    Column('room_group_id', Integer, ForeignKey('room_groups.id'), nullable=True),
    Column('subject_id', Integer, ForeignKey('subject_partitions.id'), nullable=True),
)

class Group(DECLARATIVE_BASE):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    curriculum_id = Column(Integer, ForeignKey("curricula.id"))
    name = Column(String, default="Новая группа")

class Curriculum(DECLARATIVE_BASE):
    __tablename__ = "curricula"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="Новый учебный план")

class Term(DECLARATIVE_BASE):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True)

    curriculum_id = Column(Integer, ForeignKey('curricula.id'))
    term_number_id = Column(Integer, ForeignKey('term_numbers.id'))

class TermNumber(DECLARATIVE_BASE):
    __tablename__ = "term_numbers"

    id = Column(Integer, primary_key=True)
    value = Column(String)

class Teacher(DECLARATIVE_BASE):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    second_name = Column(String)
    last_name = Column(String)

    subject_partitions = relationship('SubjectPartition', secondary=teacher_subject_association,
                                      back_populates='teachers')

class LessonType(DECLARATIVE_BASE):
    __tablename__ = 'lesson_types'

    id = Column(Integer, primary_key=True)
    name = Column(String)

class SubjectTitle(DECLARATIVE_BASE):
    __tablename__ = "subject_titles"

    id = Column(Integer, primary_key=True)
    value = Column(String)

    partitions = relationship("SubjectPartition", back_populates="title")


class SubjectPartition(DECLARATIVE_BASE):
    __tablename__ = 'subject_partitions'

    id = Column(Integer, primary_key=True)
    lesson_type_id = Column(Integer, ForeignKey('lesson_types.id'))
    title_id = Column(Integer, ForeignKey('subject_titles.id'))

    title = relationship("SubjectTitle", back_populates="partitions")

    @property
    def name(self):
        return self.title.value

    teachers = relationship('Teacher', secondary=teacher_subject_association, back_populates='subject_partitions')
    room_groups = relationship("RoomGroup", secondary=room_types_subject_partitions_association,
                               back_populates='subject_partitions')

class ScheduledSubject(DECLARATIVE_BASE):
    __tablename__ = 'scheduled_subjects'

    id = Column(Integer, primary_key=True)
    curriculum_id = Column(Integer, ForeignKey('curricula.id'))
    term_number_id = Column(Integer, ForeignKey('term_numbers.id'))
    subject_partition_id = Column(Integer, ForeignKey('subject_partitions.id'))
    count = Column(Integer, default=1)


room_groups_association = Table(
    'rooms_to_groups', DECLARATIVE_BASE.metadata,
    Column('room_id', Integer, ForeignKey('rooms.id'), nullable=True),
    Column('group_id', Integer, ForeignKey('room_groups.id'), nullable=True),
)

class Room(DECLARATIVE_BASE):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)

    building = Column(String)
    room = Column(String)

    groups = relationship("RoomGroup", secondary=room_groups_association, back_populates='rooms')

class Time(DECLARATIVE_BASE):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True)
    value = Column(String)

class Day(DECLARATIVE_BASE):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    value = Column(String)

class RoomGroup(DECLARATIVE_BASE):
    __tablename__ = 'room_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    rooms = relationship("Room", secondary=room_groups_association, back_populates='groups')
    subject_partitions = relationship("SubjectPartition", secondary=room_types_subject_partitions_association,
                                      back_populates="room_groups")

class Lesson(DECLARATIVE_BASE):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)

    group_id = Column(Integer, ForeignKey("groups.id"))
    day_id = Column(Integer, ForeignKey("days.id"))
    time_id = Column(Integer, ForeignKey("times.id"))
    subject_partition_id = Column(Integer, ForeignKey("subject_partitions.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
