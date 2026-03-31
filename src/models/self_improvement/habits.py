from pydantic import BaseModel


class HabitConfig(BaseModel):
    goal: str
    active: bool = True


class HabitsConfig(BaseModel):
    reading: HabitConfig
    exercise: HabitConfig
    mental_math: HabitConfig
    learning: HabitConfig
