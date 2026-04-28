import random
import pytest

from app.services.plan_generator import build_generated_plan

def test_one_day_plan_has_max_six_exercises():
    plan = build_generated_plan(
        days=1,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="intermediate",
    )
    assert len(plan.days) == 1
    assert len(plan.days[0].exercises) <= 6


def test_aesthetic_preset_excludes_back_squat_and_conventional_deadlift():
    plan = build_generated_plan(
        days=4,
        focus=["balanced"],
        periodization="strength",
        experience_level="advanced",
    )
    names = {exercise.name for day in plan.days for exercise in day.exercises}
    assert "Back Squat" not in names
    assert "Conventional Deadlift" not in names


def test_five_day_plan_has_no_cardio_days():
    plan_five = build_generated_plan(
        days=5,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="beginner",
    )
    assert all(day.day_role != "cardio" for day in plan_five.days)
    assert [day.day_role for day in plan_five.days] == [
        "upper",
        "lower",
        "push",
        "pull",
        "legs",
    ]


def test_four_day_plan_uses_two_lower_body_days():
    plan_four = build_generated_plan(
        days=4,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="beginner",
    )
    assert [day.day_role for day in plan_four.days] == [
        "upper",
        "lower",
        "upper",
        "lower",
    ]


def test_plan_generator_rejects_more_than_five_days():
    with pytest.raises(ValueError):
        build_generated_plan(
            days=6,
            focus=["balanced"],
            periodization="hypertrophy",
            experience_level="beginner",
        )


def test_reverse_pyramid_uses_rep_ranges():
    plan = build_generated_plan(
        days=3,
        focus=["chest"],
        periodization="hypertrophy",
        experience_level="intermediate",
    )
    progression_exercises = [
        exercise
        for day in plan.days
        for exercise in day.exercises
        if exercise.is_progression
    ]
    assert progression_exercises
    assert all(exercise.rep_ranges for exercise in progression_exercises)


def test_seeded_rng_produces_stable_plan():
    base_kwargs = {
        "days": 4,
        "focus": ["balanced"],
        "periodization": "hypertrophy",
        "experience_level": "intermediate",
    }
    plan_a = build_generated_plan(**base_kwargs, rng=random.Random(99))
    plan_b = build_generated_plan(**base_kwargs, rng=random.Random(99))

    signature_a = [
        (
            day.day_role,
            tuple(exercise.name for exercise in day.exercises),
        )
        for day in plan_a.days
    ]
    signature_b = [
        (
            day.day_role,
            tuple(exercise.name for exercise in day.exercises),
        )
        for day in plan_b.days
    ]

    assert signature_a == signature_b
