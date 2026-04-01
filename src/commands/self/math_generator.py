import random

from src.models.self.math import MathConfig
from src.utils.self import load_math_config

SYMBOLS = {
    "addition": "+",
    "subtraction": "−",
    "multiplication": "×",
    "division": "÷",
}


def _random_number(min_digits: int, max_digits: int) -> int:
    digits = random.randint(min_digits, max_digits)
    low = 10 ** (digits - 1)
    high = 10**digits - 1
    return random.randint(low, high)


def _maybe_add_trailing_zeros(n: int, chance: float) -> int:
    if random.random() < chance:
        zeros = random.choice([1, 2])
        n *= 10**zeros
    return n


def _generate_problem(problem_type: str, config: MathConfig) -> str:
    type_config = getattr(config, problem_type)

    if problem_type == "division":
        a = _random_number(type_config.min_digits, type_config.max_digits)
        b = _random_number(type_config.min_digits, type_config.max_digits)
        b = _maybe_add_trailing_zeros(b, type_config.trailing_zeros_chance)
        dividend = a * b
        return f"{dividend} {SYMBOLS[problem_type]} {b} ="

    operand1 = _random_number(type_config.min_digits, type_config.max_digits)
    operand2 = _random_number(type_config.min_digits, type_config.max_digits)
    operand1 = _maybe_add_trailing_zeros(operand1, type_config.trailing_zeros_chance)
    operand2 = _maybe_add_trailing_zeros(operand2, type_config.trailing_zeros_chance)

    if problem_type == "subtraction" and operand1 < operand2:
        operand1, operand2 = operand2, operand1

    return f"{operand1} {SYMBOLS[problem_type]} {operand2} ="


def generate_problems(config: MathConfig | None = None) -> tuple[str, list[str]]:
    if config is None:
        config = load_math_config()

    enabled_types = []
    weights = []
    for name in ["addition", "subtraction", "multiplication", "division"]:
        type_config = getattr(config, name)
        if type_config.enabled:
            enabled_types.append(name)
            weights.append(type_config.weight)

    if not enabled_types:
        return ("No problem types enabled.", [])

    problem_types = random.choices(
        enabled_types, weights=weights, k=config.general.problems_per_day
    )

    lines = []
    for i, pt in enumerate(problem_types, 1):
        problem = _generate_problem(pt, config)
        lines.append(f"{i}. {problem}")  # type: ignore

    return ("\n".join(lines), problem_types)
