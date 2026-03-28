"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";
import TextField from "../../components/Forms/TextField";
import FormButton from "../../components/Forms/FormButton";

type WorkoutOut = { id: number; name: string; date: string };

export default function WorkoutsPage() {
  return (
    <ProtectedRoute>
      <WorkoutsContent />
    </ProtectedRoute>
  );
}

function WorkoutsContent() {
  const queryClient = useQueryClient();

  const workoutsQuery = useQuery({
    queryKey: ["workouts"],
    queryFn: async () => (await api.get("/workouts")).data as WorkoutOut[],
  });

  const [name, setName] = useState("");
  const [date, setDate] = useState("");

  const createMutation = useMutation({
    mutationFn: async () => {
      return (await api.post("/workouts", { name, date })).data as WorkoutOut;
    },
    onSuccess: () => {
      setName("");
      setDate("");
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (workoutId: number) => {
      await api.delete(`/workouts/${workoutId}`);
      return workoutId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
    },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Workouts</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Create workout</h2>

          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate();
            }}
          >
            <TextField
              label="Name"
              value={name}
              placeholder="Upper Body"
              onChange={(e) => setName(e.target.value)}
              required
            />
            <TextField
              label="Date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <FormButton
              type="submit"
              loading={createMutation.isPending}
              disabled={!name || !date}
            >
              Create
            </FormButton>
          </form>

          {createMutation.isError ? (
            <p className="mt-3 text-sm text-red-300">
              {String((createMutation.error as any)?.response?.data?.detail ?? "Failed to create")}
            </p>
          ) : null}
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Your workouts</h2>

          {workoutsQuery.isLoading ? (
            <p className="text-sm text-zinc-300">Loading...</p>
          ) : workoutsQuery.error ? (
            <p className="text-sm text-red-300">
              {String((workoutsQuery.error as any)?.response?.data?.detail ?? "Failed to load")}
            </p>
          ) : workoutsQuery.data?.length ? (
            <div className="space-y-3">
              {workoutsQuery.data.map((w) => (
                <div
                  key={w.id}
                  className="flex items-center justify-between gap-4 rounded border border-zinc-800 bg-zinc-950 p-3"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{w.name}</p>
                    <p className="text-sm text-zinc-400">{w.date}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/workouts/${w.id}`}
                      className="rounded bg-zinc-800 px-3 py-1 text-sm text-zinc-100 hover:bg-zinc-700"
                    >
                      Details
                    </Link>
                    <button
                      type="button"
                      onClick={() => deleteMutation.mutate(w.id)}
                      disabled={deleteMutation.isPending}
                      className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-500 disabled:opacity-60"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-zinc-300">No workouts yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

