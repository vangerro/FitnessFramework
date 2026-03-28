"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import ProtectedRoute from "../../../components/ProtectedRoute";
import { api } from "../../../lib/api";
import TextField from "../../../components/Forms/TextField";
import NumberField from "../../../components/Forms/NumberField";
import FormButton from "../../../components/Forms/FormButton";

type ExerciseOut = {
  id: number;
  name: string;
  sets: number;
  reps: number;
  weight: string | number;
};

type WorkoutDetailOut = {
  id: number;
  name: string;
  date: string;
  exercises: ExerciseOut[];
};

export default function WorkoutDetailPage() {
  return (
    <ProtectedRoute>
      <WorkoutDetailContent />
    </ProtectedRoute>
  );
}

function WorkoutDetailContent() {
  const queryClient = useQueryClient();
  const params = useParams<{ id: string }>();
  const workoutId = Number(params.id);

  const workoutQuery = useQuery({
    queryKey: ["workout-detail", workoutId],
    queryFn: async () => {
      return (await api.get(`/workouts/${workoutId}`)).data as WorkoutDetailOut;
    },
    enabled: Number.isFinite(workoutId),
  });

  const [exName, setExName] = useState("");
  const [sets, setSets] = useState<number | "">("");
  const [reps, setReps] = useState<number | "">("");
  const [weight, setWeight] = useState<number | "">("");

  const addExerciseMutation = useMutation({
    mutationFn: async () => {
      return (
        await api.post(`/workouts/${workoutId}/exercises`, {
          name: exName,
          sets,
          reps,
          weight,
        })
      ).data as ExerciseOut;
    },
    onSuccess: () => {
      setExName("");
      setSets("");
      setReps("");
      setWeight("");
      queryClient.invalidateQueries({ queryKey: ["workout-detail", workoutId] });
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
    },
  });

  const exercises = useMemo(() => workoutQuery.data?.exercises ?? [], [workoutQuery.data]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Workout details</h1>

      {workoutQuery.isLoading ? (
        <p className="text-sm text-zinc-300">Loading...</p>
      ) : workoutQuery.error ? (
        <p className="text-sm text-red-300">
          {String((workoutQuery.error as any)?.response?.data?.detail ?? "Failed to load")}
        </p>
      ) : workoutQuery.data ? (
        <>
          <div className="mb-6 rounded border border-zinc-800 bg-zinc-900 p-4">
            <p className="text-lg font-medium">{workoutQuery.data.name}</p>
            <p className="text-sm text-zinc-400">{workoutQuery.data.date}</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
              <h2 className="mb-4 text-lg font-medium">Add exercise</h2>
              <form
                className="space-y-4"
                onSubmit={(e) => {
                  e.preventDefault();
                  addExerciseMutation.mutate();
                }}
              >
                <TextField
                  label="Name"
                  value={exName}
                  placeholder="Bench Press"
                  onChange={(e) => setExName(e.target.value)}
                  required
                />
                <NumberField
                  label="Sets"
                  step={1}
                  value={sets}
                  onChange={(e) =>
                    setSets(e.target.value === "" ? "" : Number(e.target.value))
                  }
                  required
                />
                <NumberField
                  label="Reps"
                  step={1}
                  value={reps}
                  onChange={(e) =>
                    setReps(e.target.value === "" ? "" : Number(e.target.value))
                  }
                  required
                />
                <NumberField
                  label="Weight"
                  value={weight}
                  onChange={(e) =>
                    setWeight(e.target.value === "" ? "" : Number(e.target.value))
                  }
                  required
                />
                <FormButton
                  type="submit"
                  loading={addExerciseMutation.isPending}
                  disabled={!exName || sets === "" || reps === "" || weight === ""}
                >
                  Add
                </FormButton>
              </form>

              {addExerciseMutation.isError ? (
                <p className="mt-3 text-sm text-red-300">
                  {String(
                    (addExerciseMutation.error as any)?.response?.data?.detail ??
                      "Failed to add exercise"
                  )}
                </p>
              ) : null}
            </div>

            <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
              <h2 className="mb-4 text-lg font-medium">Exercises</h2>

              {exercises.length ? (
                <div className="space-y-3">
                  {exercises.map((ex) => (
                    <div
                      key={ex.id}
                      className="rounded border border-zinc-800 bg-zinc-950 p-3"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <p className="truncate font-medium">{ex.name}</p>
                          <p className="text-sm text-zinc-400">
                            {ex.sets} sets x {ex.reps} reps
                          </p>
                        </div>
                        <p className="whitespace-nowrap text-sm text-zinc-200">
                          {ex.weight} kg
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-zinc-300">No exercises yet.</p>
              )}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}

