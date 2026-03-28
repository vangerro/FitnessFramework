from typing import Literal, TypedDict

ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
ProgressionStyle = Literal["none", "reverse_pyramid"]
ExerciseTag = Literal[
    "row",
    "rear_delt",
    "lateral_raise",
    "ohp",
    "dip",
    "chin_weighted",
    "lat_pulldown",
    "incline_press",
    "flat_press",
    "calf",
    "core",
    "cardio_block",
]


class CatalogExercise(TypedDict):
    name: str
    compound: bool
    level: ExperienceLevel
    progression_style: ProgressionStyle
    tags: list[ExerciseTag]
    excluded_presets: list[str]


EXERCISE_CATALOG: dict[str, list[CatalogExercise]] = {
    "chest": [
        {"name": "Barbell Bench Press", "compound": True, "level": "intermediate", "progression_style": "reverse_pyramid", "tags": ["flat_press"], "excluded_presets": []},
        {"name": "Incline Dumbbell Press", "compound": True, "level": "intermediate", "progression_style": "reverse_pyramid", "tags": ["incline_press"], "excluded_presets": []},
        {"name": "Incline Smith Press", "compound": True, "level": "beginner", "progression_style": "reverse_pyramid", "tags": ["incline_press"], "excluded_presets": []},
        {"name": "Decline Bench Press", "compound": True, "level": "intermediate", "progression_style": "none", "tags": ["flat_press"], "excluded_presets": []},
        {"name": "Weighted Dips", "compound": True, "level": "advanced", "progression_style": "none", "tags": ["dip"], "excluded_presets": []},
        {"name": "Machine Chest Press", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["flat_press"], "excluded_presets": []},
        {"name": "Cable Flyes", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Pec Deck Fly", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
    ],
    "quads": [
        {"name": "Back Squat", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": ["aesthetic"]},
        {"name": "Front Squat", "compound": True, "level": "advanced", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Leg Press", "compound": True, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Hack Squat", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Bulgarian Split Squat", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Walking Lunges", "compound": True, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Leg Extension", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Standing Calf Raise", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["calf"], "excluded_presets": []},
        {"name": "Seated Calf Raise", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["calf"], "excluded_presets": []},
    ],
    "hamstrings": [
        {"name": "Romanian Deadlift", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Conventional Deadlift", "compound": True, "level": "advanced", "progression_style": "none", "tags": [], "excluded_presets": ["aesthetic"]},
        {"name": "Good Morning", "compound": True, "level": "advanced", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Single-Leg Romanian Deadlift", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Hip Thrust", "compound": True, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Lying Leg Curl", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Seated Leg Curl", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
    ],
    "bis": [
        {"name": "Weighted Chin-Up", "compound": True, "level": "intermediate", "progression_style": "reverse_pyramid", "tags": ["chin_weighted"], "excluded_presets": []},
        {"name": "Chin-Up", "compound": True, "level": "intermediate", "progression_style": "reverse_pyramid", "tags": ["chin_weighted"], "excluded_presets": []},
        {"name": "Barbell Curl", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Hammer Curl", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Cable Curl", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
    ],
    "tris": [
        {"name": "Close-Grip Bench Press", "compound": True, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Weighted Dip", "compound": True, "level": "advanced", "progression_style": "none", "tags": ["dip"], "excluded_presets": []},
        {"name": "EZ Bar Skullcrusher", "compound": False, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Cable Triceps Pushdown", "compound": False, "level": "beginner", "progression_style": "none", "tags": [], "excluded_presets": []},
        {"name": "Overhead Triceps Extension", "compound": False, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
    ],
    "shoulder": [
        {"name": "Overhead Press", "compound": True, "level": "intermediate", "progression_style": "reverse_pyramid", "tags": ["ohp"], "excluded_presets": []},
        {"name": "Dumbbell Shoulder Press", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["ohp"], "excluded_presets": []},
        {"name": "Push Press", "compound": True, "level": "advanced", "progression_style": "none", "tags": ["ohp"], "excluded_presets": []},
        {"name": "Arnold Press", "compound": True, "level": "intermediate", "progression_style": "none", "tags": ["ohp"], "excluded_presets": []},
        {"name": "Lateral Raise", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["lateral_raise"], "excluded_presets": []},
        {"name": "Rear Delt Fly", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["rear_delt"], "excluded_presets": []},
        {"name": "Face Pull", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["rear_delt"], "excluded_presets": []},
    ],
    "back": [
        {"name": "Barbell Row", "compound": True, "level": "intermediate", "progression_style": "none", "tags": ["row"], "excluded_presets": []},
        {"name": "Pendlay Row", "compound": True, "level": "advanced", "progression_style": "none", "tags": ["row"], "excluded_presets": []},
        {"name": "Chest-Supported Row", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["row"], "excluded_presets": []},
        {"name": "Single-Arm Dumbbell Row", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["row"], "excluded_presets": []},
        {"name": "Seated Cable Row", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["row"], "excluded_presets": []},
        {"name": "Pull-Up", "compound": True, "level": "intermediate", "progression_style": "none", "tags": ["chin_weighted"], "excluded_presets": []},
        {"name": "Lat Pulldown", "compound": True, "level": "beginner", "progression_style": "none", "tags": ["lat_pulldown"], "excluded_presets": []},
        {"name": "Straight-Arm Pulldown", "compound": False, "level": "intermediate", "progression_style": "none", "tags": [], "excluded_presets": []},
    ],
}


CARDIO_LIBRARY: list[CatalogExercise] = [
    {"name": "Zone 2 Cardio (30-40 min)", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["cardio_block"], "excluded_presets": []},
    {"name": "Incline Walk (20-30 min)", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["cardio_block"], "excluded_presets": []},
    {"name": "Bike Intervals (12-20 min)", "compound": False, "level": "intermediate", "progression_style": "none", "tags": ["cardio_block"], "excluded_presets": []},
    {"name": "Core Circuit (10-15 min)", "compound": False, "level": "beginner", "progression_style": "none", "tags": ["core"], "excluded_presets": []},
]


BODY_PARTS: tuple[str, ...] = tuple(EXERCISE_CATALOG.keys())
BALANCED_KEYWORD = "balanced"

LEVEL_RANK: dict[ExperienceLevel, int] = {
    "beginner": 0,
    "intermediate": 1,
    "advanced": 2,
}


def pool_for_experience(
    pool: list[CatalogExercise], experience: ExperienceLevel
) -> list[CatalogExercise]:
    """Exercises at or below the user's experience tier; widens if empty."""
    max_rank = LEVEL_RANK[experience]
    filtered = [e for e in pool if LEVEL_RANK[e["level"]] <= max_rank]
    if filtered:
        return filtered
    if experience == "beginner":
        widened = [e for e in pool if LEVEL_RANK[e["level"]] <= LEVEL_RANK["intermediate"]]
        if widened:
            return widened
    return list(pool)


def pool_for_aesthetic(pool: list[CatalogExercise]) -> list[CatalogExercise]:
    filtered = [
        exercise
        for exercise in pool
        if "aesthetic" not in exercise["excluded_presets"]
    ]
    return filtered if filtered else list(pool)
