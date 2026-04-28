"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import NumberField from "../../components/Forms/NumberField";
import FormButton from "../../components/Forms/FormButton";
import TextField from "../../components/Forms/TextField";
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

type WorkoutExercise = {
  id: number;
  name: string;
  sets: number;
  reps: number;
  weight: number;
  targets: {
    id: number;
    set_number: number;
    planned_reps: number;
    planned_weight: number;
  }[];
};

type WorkoutDetail = WorkoutOut & {
  day_number: number | null;
  exercises: WorkoutExercise[];
};

type WorkoutPlanSummary = {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  workout_count: number;
};

type SessionSetLog = {
  id: number;
  exercise_id: number;
  set_number: number;
  reps: number;
  weight: number;
};

type WorkoutSession = {
  id: number;
  workout_id: number;
  performed_at: string;
  set_logs: SessionSetLog[];
};

type WorkoutPlanDetail = {
  id: number;
  name: string;
  workouts: WorkoutDetail[];
};

type TabValue = "generator" | "tracking";

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

function setEntryKey(exerciseId: number, setNumber: number): string {
  return `${exerciseId}-${setNumber}`;
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
  const [activeTab, setActiveTab] = useState<TabValue>("generator");
  const [days, setDays] = useState<number | "">(3);
  const [focus, setFocus] = useState<FocusOption[]>(["balanced"]);
  const [periodization, setPeriodization] = useState<Periodization>("hypertrophy");
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel>("intermediate");
  const [generatedPlan, setGeneratedPlan] = useState<GeneratedPlan | null>(null);
  const [planName, setPlanName] = useState("");
  const [savedCount, setSavedCount] = useState<number>(0);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [selectedWorkoutId, setSelectedWorkoutId] = useState<number | null>(null);
  const [renamePlanName, setRenamePlanName] = useState("");
  const [actualSetEntries, setActualSetEntries] = useState<Record<string, { reps: string; weight: string }>>({});
  const [plannedSetEntries, setPlannedSetEntries] = useState<Record<string, { reps: string; weight: string }>>({});
  const [expandedSessionId, setExpandedSessionId] = useState<number | null>(null);

  const plansQuery = useQuery({
    queryKey: ["workoutPlans"],
    queryFn: async () => (await api.get("/workouts/plans")).data as WorkoutPlanSummary[],
  });

  const planDetailQuery = useQuery({
    queryKey: ["workoutPlanDetail", selectedPlanId],
    enabled: selectedPlanId !== null,
    queryFn: async () =>
      (await api.get(`/workouts/plans/${selectedPlanId}`)).data as WorkoutPlanDetail,
  });

  const workoutSessionsQuery = useQuery({
    queryKey: ["workoutSessions", selectedPlanId, selectedWorkoutId],
    enabled: selectedPlanId !== null && selectedWorkoutId !== null,
    queryFn: async () =>
      (
        await api.get(`/workouts/plans/${selectedPlanId}/workouts/${selectedWorkoutId}/sessions`)
      ).data as WorkoutSession[],
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
        return { plan_id: null as number | null, created_workout_ids: [] as number[] };
      }
      return (
        await api.post("/workouts/save-plan", {
          name: planName.trim(),
          days: generatedPlan.days,
        })
      ).data as { plan_id: number; created_workout_ids: number[] };
    },
    onSuccess: (result) => {
      setSavedCount(result.created_workout_ids.length);
      setPlanName("");
      setActiveTab("tracking");
      if (result.plan_id) {
        setSelectedPlanId(result.plan_id);
      }
      queryClient.invalidateQueries({ queryKey: ["workoutPlans"] });
    },
  });

  const renamePlanMutation = useMutation({
    mutationFn: async () => {
      if (!selectedPlanId) {
        return null;
      }
      return (
        await api.patch(`/workouts/plans/${selectedPlanId}`, {
          name: renamePlanName.trim(),
        })
      ).data as WorkoutPlanSummary;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workoutPlans"] });
      if (selectedPlanId !== null) {
        queryClient.invalidateQueries({ queryKey: ["workoutPlanDetail", selectedPlanId] });
      }
    },
  });

  const deletePlanMutation = useMutation({
    mutationFn: async (planId: number) => {
      await api.delete(`/workouts/plans/${planId}`);
      return planId;
    },
    onSuccess: (deletedPlanId) => {
      queryClient.invalidateQueries({ queryKey: ["workoutPlans"] });
      if (selectedPlanId === deletedPlanId) {
        setSelectedPlanId(null);
        setSelectedWorkoutId(null);
      }
    },
  });

  const logSessionMutation = useMutation({
    mutationFn: async () => {
      if (!selectedPlanId || !selectedWorkoutId || !selectedWorkout) {
        return null;
      }

      const logs: Array<{ exercise_id: number; set_number: number; reps: number; weight: number }> =
        [];
      for (const exercise of selectedWorkout.exercises) {
        for (let setNumber = 1; setNumber <= exercise.sets; setNumber += 1) {
          const entry = actualSetEntries[setEntryKey(exercise.id, setNumber)];
          if (!entry) {
            throw new Error("Please fill all reps and weight fields.");
          }
          const reps = Number(entry.reps);
          const weight = Number(entry.weight);
          if (!Number.isFinite(reps) || reps <= 0 || !Number.isFinite(weight) || weight < 0) {
            throw new Error("Reps must be > 0 and weight must be >= 0.");
          }
          logs.push({
            exercise_id: exercise.id,
            set_number: setNumber,
            reps,
            weight,
          });
        }
      }

      return (
        await api.post(`/workouts/plans/${selectedPlanId}/workouts/${selectedWorkoutId}/sessions`, {
          set_logs: logs,
        })
      ).data;
    },
    onSuccess: () => {
      if (selectedPlanId !== null) {
        queryClient.invalidateQueries({ queryKey: ["workoutPlanDetail", selectedPlanId] });
        queryClient.invalidateQueries({
          queryKey: ["workoutSessions", selectedPlanId, selectedWorkoutId],
        });
      }
    },
  });

  const saveTargetsMutation = useMutation({
    mutationFn: async (exerciseId: number) => {
      if (!selectedPlanId || !selectedWorkout) {
        return null;
      }
      const exercise = selectedWorkout.exercises.find((item) => item.id === exerciseId);
      if (!exercise) {
        throw new Error("Exercise not found.");
      }
      const targets: Array<{ set_number: number; planned_reps: number; planned_weight: number }> = [];
      for (let setNumber = 1; setNumber <= exercise.sets; setNumber += 1) {
        const key = setEntryKey(exercise.id, setNumber);
        const entry = plannedSetEntries[key];
        if (!entry) {
          throw new Error("Please fill all planned fields.");
        }
        const plannedReps = Number(entry.reps);
        const plannedWeight = Number(entry.weight);
        if (
          !Number.isFinite(plannedReps) ||
          plannedReps <= 0 ||
          !Number.isFinite(plannedWeight) ||
          plannedWeight < 0
        ) {
          throw new Error("Planned reps must be > 0 and planned weight must be >= 0.");
        }
        targets.push({
          set_number: setNumber,
          planned_reps: plannedReps,
          planned_weight: plannedWeight,
        });
      }
      await api.put(`/workouts/plans/${selectedPlanId}/exercises/${exerciseId}/targets`, {
        targets,
      });
      return exerciseId;
    },
    onSuccess: () => {
      if (selectedPlanId !== null) {
        queryClient.invalidateQueries({ queryKey: ["workoutPlanDetail", selectedPlanId] });
      }
    },
  });

  const isGenerateDisabled = days === "" || Number(days) < 1 || Number(days) > 5 || focus.length === 0;
  const isSaveDisabled = !generatedPlan || planName.trim().length === 0;
  const totalGeneratedExercises = useMemo(
    () =>
      generatedPlan?.days.reduce(
        (sum, workoutDay) => sum + workoutDay.exercises.length,
        0
      ) ?? 0,
    [generatedPlan]
  );
  const selectedPlanSummary = useMemo(
    () => plansQuery.data?.find((plan) => plan.id === selectedPlanId) ?? null,
    [plansQuery.data, selectedPlanId]
  );
  const selectedWorkout = useMemo(
    () => planDetailQuery.data?.workouts.find((workout) => workout.id === selectedWorkoutId) ?? null,
    [planDetailQuery.data, selectedWorkoutId]
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

  useEffect(() => {
    if (!plansQuery.data?.length || selectedPlanId !== null) {
      return;
    }
    setSelectedPlanId(plansQuery.data[0].id);
  }, [plansQuery.data, selectedPlanId]);

  useEffect(() => {
    if (!planDetailQuery.data?.workouts.length) {
      setSelectedWorkoutId(null);
      return;
    }
    if (
      selectedWorkoutId === null ||
      !planDetailQuery.data.workouts.some((workout) => workout.id === selectedWorkoutId)
    ) {
      setSelectedWorkoutId(planDetailQuery.data.workouts[0].id);
    }
  }, [planDetailQuery.data, selectedWorkoutId]);

  useEffect(() => {
    if (!selectedPlanSummary) {
      setRenamePlanName("");
      return;
    }
    setRenamePlanName(selectedPlanSummary.name);
  }, [selectedPlanSummary]);

  useEffect(() => {
    if (!selectedWorkout) {
      setPlannedSetEntries({});
      setActualSetEntries({});
      return;
    }
    const nextPlanned: Record<string, { reps: string; weight: string }> = {};
    const nextActual: Record<string, { reps: string; weight: string }> = {};
    selectedWorkout.exercises.forEach((exercise) => {
      for (let setNumber = 1; setNumber <= exercise.sets; setNumber += 1) {
        const target = exercise.targets.find((item) => item.set_number === setNumber);
        const plannedReps = target?.planned_reps ?? exercise.reps;
        const plannedWeight = target?.planned_weight ?? exercise.weight;
        const key = setEntryKey(exercise.id, setNumber);
        nextPlanned[key] = {
          reps: String(plannedReps),
          weight: String(plannedWeight),
        };
        nextActual[key] = {
          reps: String(plannedReps),
          weight: String(plannedWeight),
        };
      }
    });
    setPlannedSetEntries(nextPlanned);
    setActualSetEntries(nextActual);
  }, [selectedWorkoutId, selectedWorkout]);

  useEffect(() => {
    setExpandedSessionId(null);
  }, [selectedWorkoutId]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Workouts</h1>
      <div className="mb-6 flex gap-2">
        <button
          type="button"
          onClick={() => setActiveTab("generator")}
          className={`rounded px-4 py-2 text-sm font-medium ${
            activeTab === "generator"
              ? "bg-blue-600 text-white"
              : "bg-zinc-800 text-zinc-200 hover:bg-zinc-700"
          }`}
        >
          Workout Plan Generator
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("tracking")}
          className={`rounded px-4 py-2 text-sm font-medium ${
            activeTab === "tracking"
              ? "bg-blue-600 text-white"
              : "bg-zinc-800 text-zinc-200 hover:bg-zinc-700"
          }`}
        >
          Tracking Workouts
        </button>
      </div>

      {activeTab === "generator" ? (
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
                label="Training days (1-5)"
                min={1}
                max={5}
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
                  (generateMutation.error as { response?: { data?: { detail?: string } } })?.response
                    ?.data?.detail ?? "Failed to generate workout plan"
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

                <TextField
                  label="Plan name"
                  value={planName}
                  onChange={(e) => setPlanName(e.target.value)}
                  placeholder="e.g. Spring Strength Block"
                  maxLength={120}
                />

                <div className="flex flex-wrap gap-3">
                  <FormButton
                    type="button"
                    className="!w-auto"
                    onClick={() => generateMutation.mutate()}
                    loading={generateMutation.isPending}
                  >
                    Reshuffle
                  </FormButton>
                  <FormButton
                    type="button"
                    className="!w-auto"
                    onClick={() => saveMutation.mutate()}
                    loading={saveMutation.isPending}
                    disabled={isSaveDisabled}
                  >
                    Save Plan
                  </FormButton>
                </div>

                {saveMutation.isError ? (
                  <p className="text-sm text-red-300">
                    {String(
                      (saveMutation.error as { response?: { data?: { detail?: string } } })?.response
                        ?.data?.detail ?? "Failed to save plan"
                    )}
                  </p>
                ) : null}

                {savedCount > 0 ? (
                  <p className="text-sm text-emerald-300">
                    Saved {savedCount} workouts in the plan. Switch to Tracking Workouts to log sessions.
                  </p>
                ) : null}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded border border-zinc-800 bg-zinc-900 p-4 lg:col-span-1">
            <h2 className="mb-4 text-lg font-medium">Saved Plans</h2>
            {plansQuery.isLoading ? (
              <p className="text-sm text-zinc-300">Loading...</p>
            ) : plansQuery.data?.length ? (
              <div className="space-y-2">
                {plansQuery.data.map((plan) => (
                  <button
                    type="button"
                    key={plan.id}
                    className={`w-full rounded border px-3 py-2 text-left ${
                      selectedPlanId === plan.id
                        ? "border-blue-500 bg-zinc-800"
                        : "border-zinc-700 bg-zinc-950"
                    }`}
                    onClick={() => setSelectedPlanId(plan.id)}
                  >
                    <p className="text-sm font-semibold text-zinc-100">{plan.name}</p>
                    <p className="text-xs text-zinc-400">{plan.workout_count} workouts</p>
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-zinc-300">No saved plans yet.</p>
            )}
          </div>

          <div className="space-y-6 lg:col-span-2">
            {!selectedPlanId ? (
              <div className="rounded border border-zinc-800 bg-zinc-900 p-4 text-sm text-zinc-300">
                Select a plan to start tracking.
              </div>
            ) : (
              <>
                <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
                  <h2 className="mb-4 text-lg font-medium">Plan Actions</h2>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <div className="flex-1">
                      <TextField
                        label="Rename plan"
                        value={renamePlanName}
                        onChange={(e) => setRenamePlanName(e.target.value)}
                        maxLength={120}
                      />
                    </div>
                    <FormButton
                      type="button"
                      className="!w-auto"
                      loading={renamePlanMutation.isPending}
                      disabled={renamePlanName.trim().length === 0}
                      onClick={() => renamePlanMutation.mutate()}
                    >
                      Rename
                    </FormButton>
                    <FormButton
                      type="button"
                      className="!w-auto !bg-red-700 hover:!bg-red-600"
                      loading={deletePlanMutation.isPending}
                      onClick={() => {
                        if (!selectedPlanId) return;
                        if (!window.confirm("Delete this plan and all tracking history?")) return;
                        deletePlanMutation.mutate(selectedPlanId);
                      }}
                    >
                      Delete
                    </FormButton>
                  </div>
                  {renamePlanMutation.isError ? (
                    <p className="mt-3 text-sm text-red-300">Failed to rename plan.</p>
                  ) : null}
                  {deletePlanMutation.isError ? (
                    <p className="mt-3 text-sm text-red-300">Failed to delete plan.</p>
                  ) : null}
                </div>

                <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
                  <h2 className="mb-4 text-lg font-medium">Track Workout</h2>
                  {planDetailQuery.isLoading ? (
                    <p className="text-sm text-zinc-300">Loading plan details...</p>
                  ) : planDetailQuery.data?.workouts.length ? (
                    <div className="space-y-4">
                      <div className="flex flex-wrap gap-2">
                        {planDetailQuery.data.workouts.map((workout) => (
                          <button
                            key={workout.id}
                            type="button"
                            onClick={() => setSelectedWorkoutId(workout.id)}
                            className={`rounded px-3 py-1.5 text-xs font-medium ${
                              selectedWorkoutId === workout.id
                                ? "bg-blue-600 text-white"
                                : "bg-zinc-800 text-zinc-200"
                            }`}
                          >
                            Day {workout.day_number ?? "-"}: {workout.name}
                          </button>
                        ))}
                      </div>

                      {selectedWorkout ? (
                        <div className="space-y-4">
                          {selectedWorkout.exercises.map((exercise) => (
                            <div
                              key={exercise.id}
                              className="rounded border border-zinc-700 bg-zinc-950 p-3"
                            >
                              <p className="mb-2 text-sm font-semibold text-zinc-100">{exercise.name}</p>
                              <div className="space-y-2">
                                <div className="grid grid-cols-5 gap-2 text-xs uppercase tracking-wide text-zinc-500">
                                  <p>Set</p>
                                  <p>Target reps</p>
                                  <p>Target weight</p>
                                  <p>Performed reps</p>
                                  <p>Performed weight</p>
                                </div>
                                {Array.from({ length: exercise.sets }).map((_, setIndex) => {
                                  const setNumber = setIndex + 1;
                                  const key = setEntryKey(exercise.id, setNumber);
                                  const plannedEntry = plannedSetEntries[key] ?? { reps: "", weight: "" };
                                  const actualEntry = actualSetEntries[key] ?? { reps: "", weight: "" };
                                  return (
                                    <div key={key} className="grid grid-cols-5 gap-2 text-sm">
                                      <p className="self-center text-zinc-300">Set {setNumber}</p>
                                      <input
                                        type="number"
                                        min={1}
                                        value={plannedEntry.reps}
                                        onChange={(e) =>
                                          setPlannedSetEntries((current) => ({
                                            ...current,
                                            [key]: {
                                              ...plannedEntry,
                                              reps: e.target.value,
                                            },
                                          }))
                                        }
                                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-zinc-100"
                                        placeholder="Planned reps"
                                      />
                                      <input
                                        type="number"
                                        min={0}
                                        step="0.5"
                                        value={plannedEntry.weight}
                                        onChange={(e) =>
                                          setPlannedSetEntries((current) => ({
                                            ...current,
                                            [key]: {
                                              ...plannedEntry,
                                              weight: e.target.value,
                                            },
                                          }))
                                        }
                                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-zinc-100"
                                        placeholder="Target weight"
                                      />
                                      <input
                                        type="number"
                                        min={1}
                                        value={actualEntry.reps}
                                        onChange={(e) =>
                                          setActualSetEntries((current) => ({
                                            ...current,
                                            [key]: {
                                              ...actualEntry,
                                              reps: e.target.value,
                                            },
                                          }))
                                        }
                                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-zinc-100"
                                        placeholder="Actual reps"
                                      />
                                      <input
                                        type="number"
                                        min={0}
                                        step="0.5"
                                        value={actualEntry.weight}
                                        onChange={(e) =>
                                          setActualSetEntries((current) => ({
                                            ...current,
                                            [key]: {
                                              ...actualEntry,
                                              weight: e.target.value,
                                            },
                                          }))
                                        }
                                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-zinc-100"
                                        placeholder="Performed weight"
                                      />
                                    </div>
                                  );
                                })}
                              </div>
                              <div className="mt-3">
                                <FormButton
                                  type="button"
                                  className="!w-auto"
                                  loading={saveTargetsMutation.isPending}
                                  onClick={() => saveTargetsMutation.mutate(exercise.id)}
                                >
                                  Save Planned Targets
                                </FormButton>
                              </div>
                            </div>
                          ))}

                          <FormButton
                            type="button"
                            className="!w-auto"
                            loading={logSessionMutation.isPending}
                            onClick={() => logSessionMutation.mutate()}
                          >
                            Save Session
                          </FormButton>
                          {logSessionMutation.isError ? (
                            <p className="text-sm text-red-300">
                              {String((logSessionMutation.error as Error)?.message ?? "Failed to save session")}
                            </p>
                          ) : null}
                          {saveTargetsMutation.isError ? (
                            <p className="text-sm text-red-300">
                              {String((saveTargetsMutation.error as Error)?.message ?? "Failed to save planned targets")}
                            </p>
                          ) : null}
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <p className="text-sm text-zinc-300">This plan has no workouts.</p>
                  )}
                </div>

                <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
                  <h2 className="mb-4 text-lg font-medium">Tracked Workouts</h2>
                  {workoutSessionsQuery.isLoading ? (
                    <p className="text-sm text-zinc-300">Loading tracked sessions...</p>
                  ) : workoutSessionsQuery.data?.length ? (
                    <div className="space-y-2">
                      {workoutSessionsQuery.data.map((session) => (
                        <div
                          key={session.id}
                          className="rounded border border-zinc-700 bg-zinc-950 px-3 py-2"
                        >
                          <button
                            type="button"
                            className="w-full text-left"
                            onClick={() =>
                              setExpandedSessionId((current) =>
                                current === session.id ? null : session.id
                              )
                            }
                          >
                            <p className="text-sm text-zinc-100">
                              {new Date(session.performed_at).toLocaleString()}
                            </p>
                            <p className="text-xs text-zinc-400">{session.set_logs.length} sets logged</p>
                          </button>
                          {expandedSessionId === session.id ? (
                            <div className="mt-2 space-y-1 border-t border-zinc-800 pt-2">
                              {(() => {
                                const exerciseOrder =
                                  selectedWorkout?.exercises.reduce<Record<number, number>>(
                                    (acc, exercise, index) => {
                                      acc[exercise.id] = index;
                                      return acc;
                                    },
                                    {}
                                  ) ?? {};
                                return session.set_logs
                                  .slice()
                                  .sort((a, b) => {
                                    const aOrder = exerciseOrder[a.exercise_id] ?? Number.MAX_SAFE_INTEGER;
                                    const bOrder = exerciseOrder[b.exercise_id] ?? Number.MAX_SAFE_INTEGER;
                                    if (aOrder !== bOrder) {
                                      return aOrder - bOrder;
                                    }
                                    return a.set_number - b.set_number;
                                  })
                                  .map((setLog) => {
                                    const exerciseName =
                                      selectedWorkout?.exercises.find(
                                        (exercise) => exercise.id === setLog.exercise_id
                                      )?.name ?? `Exercise #${setLog.exercise_id}`;
                                    return (
                                      <p key={setLog.id} className="text-xs text-zinc-300">
                                        {exerciseName} - Set {setLog.set_number}: {setLog.reps} reps @{" "}
                                        {setLog.weight}
                                      </p>
                                    );
                                  });
                              })()}
                            </div>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-zinc-300">No sessions logged yet for this workout day.</p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
