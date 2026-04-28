from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import random
from typing import Literal

from app.data.exercise_catalog import (
    BALANCED_KEYWORD,
    CARDIO_LIBRARY,
    CatalogExercise,
    ExperienceLevel,
    pool_for_experience,
    pool_for_aesthetic,
    EXERCISE_CATALOG,
)
from app.schemas.plan import DayRole, GeneratedExercise, GeneratedPlan, GeneratedWorkoutDay

BodyPart = Literal["chest", "quads", "hamstrings", "bis", "tris", "shoulder", "back"]
Periodization = Literal["strength", "hypertrophy"]

AESTHETIC_MANDATORY_TAGS = {"ohp", "lateral_raise", "rear_delt", "row", "chin_weighted"}
AESTHETIC_PREFERRED_TAGS = {"dip", "incline_press"}


@dataclass(frozen=True)
class DayTemplate:
    name: str
    day_role: DayRole
    parts: list[BodyPart]
    max_exercises: int
    max_sets: int
    compound_bias: float = 0.6


def build_generated_plan(
    *,
    days: int,
    focus: list[str],
    periodization: Periodization,
    experience_level: ExperienceLevel,
    start_date: date | None = None,
    rng: random.Random | None = None,
) -> GeneratedPlan:
    focused_parts = _resolve_focus_parts(focus)
    legs_focus = "quads" in focused_parts or "hamstrings" in focused_parts
    templates = _aesthetic_templates(days=days, legs_focus=legs_focus)
    rng = rng or random.Random()
    remaining_mandatory = set(AESTHETIC_MANDATORY_TAGS)
    generated_days: list[GeneratedWorkoutDay] = []
    plan_start = start_date or date.today()

    for day_index, template in enumerate(templates, start=1):
        if template.day_role == "cardio":
            exercises = _build_cardio_exercises(
                experience_level=experience_level,
                rng=rng,
            )
        else:
            exercises = _build_strength_day(
                template=template,
                focused_parts=focused_parts,
                periodization=periodization,
                experience_level=experience_level,
                remaining_mandatory=remaining_mandatory,
                rng=rng,
            )
            _enforce_set_budget(exercises, template.max_sets)
            _sort_day_exercises(exercises)

        for exercise in exercises:
            for tag in exercise.tags:
                if tag in remaining_mandatory:
                    remaining_mandatory.remove(tag)

        generated_days.append(
            GeneratedWorkoutDay(
                day_number=day_index,
                name=template.name,
                day_role=template.day_role,
                date=plan_start + timedelta(days=day_index - 1),
                exercises=exercises,
            )
        )

    if remaining_mandatory:
        _inject_missing_mandatory_tags(
            generated_days=generated_days,
            missing_tags=remaining_mandatory,
            periodization=periodization,
            experience_level=experience_level,
            rng=rng,
        )

    return GeneratedPlan(days=generated_days)


def _aesthetic_templates(*, days: int, legs_focus: bool) -> list[DayTemplate]:
    if days == 1:
        return [DayTemplate("Full Body", "full_body", ["chest", "back", "quads", "hamstrings", "shoulder", "tris"], 6, 16, 0.85)]
    if days == 2:
        return [
            DayTemplate("Full Body A", "full_body", ["chest", "back", "quads", "hamstrings", "shoulder", "tris"], 6, 16, 0.85),
            DayTemplate("Full Body B", "full_body", ["chest", "back", "quads", "hamstrings", "shoulder", "bis"], 6, 16, 0.85),
        ]
    if days == 3:
        return [
            DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "tris"], 6, 16, 0.75),
            DayTemplate("Lower + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
            DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis"], 6, 16, 0.75),
        ]
    if days == 4:
        if legs_focus:
            return [
                DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
                DayTemplate("Lower A + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
                DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
                DayTemplate("Lower B + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
            ]
        return [
            DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Lower + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
            DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Aesthetic", "aesthetic", ["shoulder", "chest", "back", "bis", "tris"], 6, 15, 0.35),
        ]
    if days == 5:
        return [
            DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Lower + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
            DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Cardio + Core", "cardio", [], 3, 4, 0.0),
            DayTemplate("Push/Pull Mix", "upper", ["chest", "back", "shoulder", "bis", "tris"], 5, 14, 0.65),
        ]
    if days == 6:
        return [
            DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Lower + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
            DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis", "tris"], 6, 16, 0.75),
            DayTemplate("Cardio + Core", "cardio", [], 3, 4, 0.0),
            DayTemplate("Pull/Arms", "pull", ["back", "bis", "tris", "shoulder"], 5, 14, 0.6),
            DayTemplate("Cardio Recovery", "cardio", [], 2, 3, 0.0),
        ]
    return [
        DayTemplate("Upper A", "upper", ["chest", "back", "shoulder", "bis", "tris"], 5, 14, 0.75),
        DayTemplate("Lower A + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
        DayTemplate("Upper B", "upper", ["chest", "back", "shoulder", "bis", "tris"], 5, 14, 0.75),
        DayTemplate("Cardio + Core", "cardio", [], 3, 4, 0.0),
        DayTemplate("Pull/Arms", "pull", ["back", "bis", "tris", "shoulder"], 5, 14, 0.6),
        DayTemplate("Lower B + Calves", "lower", ["quads", "hamstrings"], 6, 16, 0.85),
        DayTemplate("Cardio Recovery", "cardio", [], 2, 3, 0.0),
    ]


def _resolve_focus_parts(focus: list[str]) -> set[BodyPart]:
    if BALANCED_KEYWORD in focus:
        return set()
    return {part for part in focus if part in EXERCISE_CATALOG}


def _build_strength_day(
    *,
    template: DayTemplate,
    focused_parts: set[BodyPart],
    periodization: Periodization,
    experience_level: ExperienceLevel,
    remaining_mandatory: set[str],
    rng: random.Random,
) -> list[GeneratedExercise]:
    slots = _build_part_slots(template=template, focused_parts=focused_parts)
    selected: list[GeneratedExercise] = []
    used_names: set[str] = set()

    for part in slots:
        exercise = _select_exercise(
            part=part,
            template=template,
            periodization=periodization,
            experience_level=experience_level,
            required_tags=remaining_mandatory,
            used_names=used_names,
            rng=rng,
        )
        if not exercise:
            continue
        used_names.add(exercise.name)
        selected.append(exercise)

    return selected[: template.max_exercises]


def _build_part_slots(*, template: DayTemplate, focused_parts: set[BodyPart]) -> list[BodyPart]:
    base_scores = {
        "chest": 3,
        "back": 3,
        "quads": 3,
        "hamstrings": 3,
        "shoulder": 3,
        "bis": 2,
        "tris": 2,
    }
    scored = sorted(
        list(dict.fromkeys(template.parts)),
        key=lambda part: base_scores.get(part, 1) + (4 if part in focused_parts else 0),
        reverse=True,
    )
    slots = scored[: template.max_exercises]
    while len(slots) < template.max_exercises:
        focus_candidates = [part for part in scored if part in focused_parts]
        if focus_candidates:
            slots.append(focus_candidates[len(slots) % len(focus_candidates)])
        elif scored:
            slots.append(scored[len(slots) % len(scored)])
        else:
            break
    return slots


def _select_exercise(
    *,
    part: BodyPart,
    template: DayTemplate,
    periodization: Periodization,
    experience_level: ExperienceLevel,
    required_tags: set[str],
    used_names: set[str],
    rng: random.Random,
) -> GeneratedExercise | None:
    pool = pool_for_experience(pool_for_aesthetic(EXERCISE_CATALOG[part]), experience_level)
    if not pool:
        return None

    best: CatalogExercise | None = None
    best_score = -10_000.0
    for exercise in pool:
        score = rng.random()
        if exercise["name"] in used_names:
            score -= 100
        if exercise["compound"]:
            score += template.compound_bias * 10
        elif template.day_role == "aesthetic":
            score += 4
        if required_tags.intersection(exercise["tags"]):
            score += 35
        if "incline_press" in exercise["tags"]:
            score += 14
        if "dip" in exercise["tags"]:
            score += 8
        if "chin_weighted" in exercise["tags"] and experience_level == "beginner":
            score -= 12
        if "lat_pulldown" in exercise["tags"] and experience_level == "beginner":
            score += 10
        if AESTHETIC_PREFERRED_TAGS.intersection(exercise["tags"]):
            score += 4
        if part == "quads" and exercise["name"] == "Hack Squat":
            score += 16
        if score > best_score:
            best = exercise
            best_score = score

    if not best:
        return None

    sets, reps, rep_ranges, is_progression = _rep_scheme(
        exercise=best,
        periodization=periodization,
        rng=rng,
    )
    return GeneratedExercise(
        name=best["name"],
        sets=sets,
        reps=reps,
        rep_ranges=rep_ranges,
        body_part=part,
        level=best["level"],
        tags=best["tags"],
        is_progression=is_progression,
    )


def _rep_scheme(
    *, exercise: CatalogExercise, periodization: Periodization, rng: random.Random
) -> tuple[int, int | None, list[str], bool]:
    if exercise["progression_style"] == "reverse_pyramid":
        if periodization == "strength":
            return 3, None, ["3-4", "4-5", "5-6"], True
        return 3, None, ["5-6", "6-8", "8-10"], True

    if periodization == "strength":
        sets = 4 if exercise["compound"] else 3
        rep_ranges = ["4-6"] if exercise["compound"] else ["6-10"]
        return sets, None, rep_ranges, False

    sets = 4 if exercise["compound"] else 3
    rep_ranges = ["6-10"] if exercise["compound"] else ["10-15"]
    return sets, None, rep_ranges, False


def _build_cardio_exercises(
    *,
    experience_level: ExperienceLevel,
    rng: random.Random,
) -> list[GeneratedExercise]:
    pool = pool_for_experience(pool_for_aesthetic(CARDIO_LIBRARY), experience_level)
    rng.shuffle(pool)
    selected = pool[:3]
    exercises: list[GeneratedExercise] = []
    for entry in selected:
        duration = _duration_from_name(entry["name"])
        exercises.append(
            GeneratedExercise(
                name=entry["name"],
                sets=1,
                reps=1,
                rep_ranges=[duration] if duration else ["1 block"],
                body_part="cardio",
                level=entry["level"],
                tags=entry["tags"],
                is_progression=False,
            )
        )
    return exercises


def _duration_from_name(name: str) -> str:
    if "(" in name and ")" in name:
        return name.split("(", 1)[1].split(")", 1)[0]
    return "1 block"


def _enforce_set_budget(exercises: list[GeneratedExercise], max_sets: int) -> None:
    total_sets = sum(item.sets for item in exercises)
    while total_sets > max_sets and exercises:
        adjusted = False
        for exercise in reversed(exercises):
            min_sets = 3 if exercise.is_progression else 2
            if exercise.sets > min_sets:
                exercise.sets -= 1
                total_sets -= 1
                adjusted = True
                if total_sets <= max_sets:
                    break
        if adjusted:
            continue
        exercises.pop()
        total_sets = sum(item.sets for item in exercises)


def _sort_day_exercises(exercises: list[GeneratedExercise]) -> None:
    exercises.sort(
        key=lambda exercise: (
            0 if exercise.is_progression else 1,
            0 if exercise.tags and ("ohp" in exercise.tags or "incline_press" in exercise.tags) else 1,
            0 if "row" in exercise.tags else 1,
            0 if "rear_delt" in exercise.tags else 1,
            0 if "lateral_raise" in exercise.tags else 1,
            0 if "calf" in exercise.tags else 1,
            exercise.name,
        )
    )


def _inject_missing_mandatory_tags(
    *,
    generated_days: list[GeneratedWorkoutDay],
    missing_tags: set[str],
    periodization: Periodization,
    experience_level: ExperienceLevel,
    rng: random.Random,
) -> None:
    if not missing_tags:
        return
    candidate_days = [day for day in generated_days if day.day_role != "cardio"]
    for missing_tag in list(missing_tags):
        replacement = _find_by_tag(
            tag=missing_tag,
            periodization=periodization,
            experience_level=experience_level,
            rng=rng,
        )
        if not replacement or not candidate_days:
            continue
        day = candidate_days[-1]
        if day.exercises:
            day.exercises[-1] = replacement
        else:
            day.exercises.append(replacement)


def _find_by_tag(
    *,
    tag: str,
    periodization: Periodization,
    experience_level: ExperienceLevel,
    rng: random.Random,
) -> GeneratedExercise | None:
    for part, exercises in EXERCISE_CATALOG.items():
        pool = pool_for_experience(pool_for_aesthetic(exercises), experience_level)
        matches = [exercise for exercise in pool if tag in exercise["tags"]]
        if not matches:
            continue
        chosen = matches[int(rng.random() * len(matches))]
        sets, reps, rep_ranges, is_progression = _rep_scheme(
            exercise=chosen,
            periodization=periodization,
            rng=rng,
        )
        return GeneratedExercise(
            name=chosen["name"],
            sets=sets,
            reps=reps,
            rep_ranges=rep_ranges,
            body_part=part,  # type: ignore[arg-type]
            level=chosen["level"],
            tags=chosen["tags"],
            is_progression=is_progression,
        )
    return None
