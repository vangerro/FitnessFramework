"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import NumberField from "../../components/Forms/NumberField";
import FormButton from "../../components/Forms/FormButton";
import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";

type FocusOption =
  | "balanced"
  | "chest"
  | "quads"
  | "hamstrings"
  | "bis"
  | "tris"
  | "shoulder"
  | "back";

type Periodization = "strength" | "hypertrophy";

type ExperienceLevel = "beginner" | "intermediate" | "advanced";

type GeneratedExercise = {
  name: string;
  sets: number;
  reps: number | null;
  rep_ranges: string[];
  body_part: Exclude<FocusOption, "balanced">;
  level: ExperienceLevel;
  tags: string[];
  is_progression: boolean;
};

type GeneratedWorkoutDay = {
  day_number: number;
  name: string;
  day_role:
    | "full_body"
    | "upper"
    | "lower"
    | "push"
    | "pull"
    | "legs"
    | "aesthetic"
    | "cardio";
  date?: string | null;
  exercises: GeneratedExercise[];
};

type GeneratedPlan = {
  days: GeneratedWorkoutDay[];
};

type WorkoutOut = {
  id: number;
  name: string;
  date: string;
};

const FOCUS_OPTIONS: Array<{ value: FocusOption; label: string }> = [
  { value: "chest", label: "Chest" },
  { value: "quads", label: "Quads" },
  { value: "hamstrings", label: "Hamstrings" },
  { value: "bis", label: "Biceps" },
  { value: "tris", label: "Triceps" },
  { value: "shoulder", label: "Shoulder" },
  { value: "back", label: "Back" },
  { value: "balanced", label: "Balanced" },
];

function formatExperienceLabel(level: ExperienceLevel): string {
  if (level === "beginner") return "Beginner";
  if (level === "intermediate") return "Intermediate";
  return "Advanced";
}

function formatReps(exercise: GeneratedExercise): string {
  if (exercise.rep_ranges.length > 0) {
    return exercise.rep_ranges.join(" / ");
  }
  if (exercise.reps === null) {
    return "-";
  }
  return String(exercise.reps);
}

export default function WorkoutsPage() {
  return (
    <ProtectedRoute>
      <WorkoutsContent />
    </ProtectedRoute>
  );
}

function WorkoutsContent() {
  const queryClient = useQueryClient();
  const [days, setDays] = useState<number | "">(3);
  const [focus, setFocus] = useState<FocusOption[]>(["balanced"]);
  const [periodization, setPeriodization] = useState<Periodization>("hypertrophy");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>("intermediate");
  const [generatedPlan, setGeneratedPlan] = useState<GeneratedPlan | null>(null);
  const [savedCount, setSavedCount] = useState<number>(0);

  const workoutsQuery = useQuery({
    queryKey: ["workouts"],
    queryFn: async () => (await api.get("/workouts")).data as WorkoutOut[],
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      return (
        await api.post("/workouts/generate", {
          days: Number(days),
          focus,
          periodization,
          experience_level: experienceLevel,
        })
      ).data as GeneratedPlan;
    },
    onSuccess: (plan) => {
      setGeneratedPlan(plan);
      setSavedCount(0);
    },
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!generatedPlan) {
        return { created_workout_ids: [] as number[] };
      }
      return (
        await api.post("/workouts/save-plan", {
          days: generatedPlan.days,
        })
      ).data as { created_workout_ids: number[] };
    },
    onSuccess: (result) => {
      setSavedCount(result.created_workout_ids.length);
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
    },
  });

  const isGenerateDisabled = days === "" || Number(days) < 1 || Number(days) > 7 || focus.length === 0;
  const totalGeneratedExercises = useMemo(
    () =>
      generatedPlan?.days.reduce(
        (sum, workoutDay) => sum + workoutDay.exercises.length,
        0
      ) ?? 0,
    [generatedPlan]
  );

  const toggleFocus = (value: FocusOption) => {
    setFocus((current) => {
      if (value === "balanced") {
        return ["balanced"];
      }

      const withoutBalanced = current.filter((item) => item !== "balanced");
      if (withoutBalanced.includes(value)) {
        const next = withoutBalanced.filter((item) => item !== value);
        return next.length ? next : ["balanced"];
      }
      return [...withoutBalanced, value];
    });
  };

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Workout Plan Generator</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Configuration</h2>
          <form
            className="space-y-5"
            onSubmit={(e) => {
              e.preventDefault();
              generateMutation.mutate();
            }}
          >
            <NumberField
              label="Training days (1-7)"
              min={1}
              max={7}
              step={1}
              value={days}
              onChange={(e) => {
                const value = e.target.value;
                setDays(value === "" ? "" : Number(value));
              }}
              required
            />

            <fieldset>
              <legend className="mb-2 text-sm text-zinc-200">Focus</legend>
              <div className="grid grid-cols-2 gap-2">
                {FOCUS_OPTIONS.map((option) => {
                  const checked = focus.includes(option.value);
                  return (
                    <label
                      key={option.value}
                      className="flex items-center gap-2 rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-200"
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleFocus(option.value)}
                        className="h-4 w-4"
                      />
                      {option.label}
                    </label>
                  );
                })}
              </div>
            </fieldset>

            <fieldset>
              <legend className="mb-2 text-sm text-zinc-200">Periodization</legend>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-sm text-zinc-200">
                  <input
                    type="radio"
                    name="periodization"
                    value="strength"
                    checked={periodization === "strength"}
                    onChange={() => setPeriodization("strength")}
                  />
                  Strength
                </label>
                <label className="flex items-center gap-2 text-sm text-zinc-200">
                  <input
                    type="radio"
                    name="periodization"
                    value="hypertrophy"
                    checked={periodization === "hypertrophy"}
                    onChange={() => setPeriodization("hypertrophy")}
                  />
                  Hypertrophy
                </label>
              </div>
            </fieldset>

            <fieldset>
              <legend className="mb-2 text-sm text-zinc-200">Experience</legend>
              <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:gap-4">
                <label className="flex items-center gap-2 text-sm text-zinc-200">
                  <input
                    type="radio"
                    name="experience"
                    value="beginner"
                    checked={experienceLevel === "beginner"}
                    onChange={() => setExperienceLevel("beginner")}
                  />
                  Beginner
                </label>
                <label className="flex items-center gap-2 text-sm text-zinc-200">
                  <input
                    type="radio"
                    name="experience"
                    value="intermediate"
                    checked={experienceLevel === "intermediate"}
                    onChange={() => setExperienceLevel("intermediate")}
                  />
                  Intermediate
                </label>
                <label className="flex items-center gap-2 text-sm text-zinc-200">
                  <input
                    type="radio"
                    name="experience"
                    value="advanced"
                    checked={experienceLevel === "advanced"}
                    onChange={() => setExperienceLevel("advanced")}
                  />
                  Advanced
                </label>
              </div>
            </fieldset>

            <FormButton
              type="submit"
              loading={generateMutation.isPending}
              disabled={isGenerateDisabled}
            >
              Generate Plan
            </FormButton>
          </form>

          {generateMutation.isError ? (
            <p className="mt-3 text-sm text-red-300">
              {String(
                (generateMutation.error as any)?.response?.data?.detail ??
                  "Failed to generate workout plan"
              )}
            </p>
          ) : null}
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Plan Preview</h2>
          {!generatedPlan ? (
            <p className="text-sm text-zinc-300">
              Configure your options and generate a plan to preview workouts.
            </p>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-zinc-300">
                {generatedPlan.days.length} workout days, {totalGeneratedExercises} exercises.
              </p>

              <div className="space-y-3">
                {generatedPlan.days.map((day) => (
                  <div
                    key={`${day.day_number}-${day.name}`}
                    className="rounded border border-zinc-700 bg-zinc-950 p-3"
                  >
                    <h3 className="text-sm font-semibold text-zinc-100">
                      Day {day.day_number}: {day.name}
                    </h3>
                    <p className="mt-1 text-xs uppercase tracking-wide text-zinc-400">
                      {day.day_role.replace("_", " ")}
                    </p>
                    <div className="mt-2 overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead className="text-zinc-400">
                          <tr>
                            <th className="py-1 pr-3">Exercise</th>
                            <th className="py-1 pr-3">Level</th>
                            <th className="py-1 pr-3">Sets</th>
                            <th className="py-1 pr-3">Reps</th>
                          </tr>
                        </thead>
                        <tbody className="text-zinc-200">
                          {day.exercises.map((exercise, index) => (
                            <tr key={`${exercise.name}-${index}`}>
                              <td className="py-1 pr-3">{exercise.name}</td>
                              <td className="py-1 pr-3 text-zinc-400">
                                {formatExperienceLabel(exercise.level)}
                              </td>
                              <td className="py-1 pr-3">{exercise.sets}</td>
                              <td className="py-1 pr-3">{formatReps(exercise)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-3">
                <FormButton
                  type="button"
                  onClick={() => generateMutation.mutate()}
                  loading={generateMutation.isPending}
                >
                  Regenerate
                </FormButton>
                <FormButton
                  type="button"
                  onClick={() => saveMutation.mutate()}
                  loading={saveMutation.isPending}
                  disabled={saveMutation.isPending}
                >
                  Save Plan
                </FormButton>
              </div>

              {saveMutation.isError ? (
                <p className="text-sm text-red-300">
                  {String(
                    (saveMutation.error as any)?.response?.data?.detail ??
                      "Failed to save plan"
                  )}
                </p>
              ) : null}

              {savedCount > 0 ? (
                <p className="text-sm text-emerald-300">
                  Saved {savedCount} workouts.{" "}
                  <a href="#saved-workouts" className="underline hover:text-emerald-200">
                    View saved workouts
                  </a>
                  .
                </p>
              ) : null}
            </div>
          )}
        </div>
      </div>

      <section id="saved-workouts" className="mt-6 rounded border border-zinc-800 bg-zinc-900 p-4">
        <h2 className="mb-4 text-lg font-medium">Saved Workouts</h2>
        {workoutsQuery.isLoading ? (
          <p className="text-sm text-zinc-300">Loading...</p>
        ) : workoutsQuery.data?.length ? (
          <div className="space-y-2">
            {workoutsQuery.data.map((workout) => (
              <div
                key={workout.id}
                className="rounded border border-zinc-800 bg-zinc-950 px-3 py-2"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm text-zinc-200">{workout.name}</p>
                  <p className="text-sm text-zinc-400">{workout.date}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-300">
            No workouts saved yet. Generate and save a plan to populate this list.
          </p>
        )}
      </section>

    </div>
  );
}
