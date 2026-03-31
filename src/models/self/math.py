from datetime import date

from pydantic import BaseModel


class ProblemTypeConfig(BaseModel):
    enabled: bool = True
    weight: int = 1
    min_digits: int = 2
    max_digits: int = 2
    trailing_zeros_chance: float = 0.3


class DivisionConfig(ProblemTypeConfig):
    whole_numbers_only: bool = True


class MathGeneralConfig(BaseModel):
    problems_per_day: int = 5


class MathConfig(BaseModel):
    general: MathGeneralConfig = MathGeneralConfig()
    addition: ProblemTypeConfig = ProblemTypeConfig()
    subtraction: ProblemTypeConfig = ProblemTypeConfig()
    multiplication: ProblemTypeConfig = ProblemTypeConfig(weight=3)
    division: DivisionConfig = DivisionConfig()


class MathSession(BaseModel):
    date: date
    time_seconds: int
    correct: int
    total: int
    problem_types: list[str] = []


class MathLog(BaseModel):
    sessions: list[MathSession] = []
