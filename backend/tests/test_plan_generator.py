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


def test_aesthetic_cardio_day_counts_for_high_frequency_weeks():
    plan_five = build_generated_plan(
        days=5,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="beginner",
    )
    plan_six = build_generated_plan(
        days=6,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="beginner",
    )
    plan_seven = build_generated_plan(
        days=7,
        focus=["balanced"],
        periodization="hypertrophy",
        experience_level="beginner",
    )

    assert sum(1 for day in plan_five.days if day.day_role == "cardio") == 1
    assert sum(1 for day in plan_six.days if day.day_role == "cardio") == 2
    assert sum(1 for day in plan_seven.days if day.day_role == "cardio") == 2
    assert sum(1 for day in plan_seven.days if day.day_role in {"lower", "legs"}) == 2


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
