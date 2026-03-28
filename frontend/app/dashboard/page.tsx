"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";

type WeightOut = { id: number; weight: string | number; date: string };
type WorkoutOut = { id: number; name: string; date: string };

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const weightsQuery = useQuery({
    queryKey: ["weight"],
    queryFn: async () => {
      const res = await api.get("/weight");
      return res.data as WeightOut[];
    },
  });

  const workoutsQuery = useQuery({
    queryKey: ["workouts"],
    queryFn: async () => {
      const res = await api.get("/workouts");
      return res.data as WorkoutOut[];
    },
  });

  const latestWeight = useMemo(() => {
    const items = weightsQuery.data ?? [];
    return items.length ? items[items.length - 1] : null;
  }, [weightsQuery.data]);

  const latestWorkout = useMemo(() => {
    const items = workoutsQuery.data ?? [];
    return items.length ? items[items.length - 1] : null;
  }, [workoutsQuery.data]);

  const isLoading = weightsQuery.isLoading || workoutsQuery.isLoading;
  const error = weightsQuery.error ?? workoutsQuery.error;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Dashboard</h1>

      {isLoading ? (
        <p className="text-sm text-zinc-300">Loading...</p>
      ) : error ? (
        <p className="text-sm text-red-300">
          {String((error as any)?.response?.data?.detail ?? "Failed to load")}
        </p>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Latest weight</p>
          <p className="mt-2 text-3xl font-semibold">
            {latestWeight ? latestWeight.weight : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            {latestWeight ? latestWeight.date : ""}
          </p>
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Workouts</p>
          <p className="mt-2 text-3xl font-semibold">
            {workoutsQuery.data?.length ?? 0}
          </p>
          <p className="mt-1 text-sm text-zinc-400">Total entries</p>
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Latest workout</p>
          <p className="mt-2 text-3xl font-semibold">
            {latestWorkout ? latestWorkout.name : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            {latestWorkout ? latestWorkout.date : ""}
          </p>
        </div>
      </div>
    </div>
  );
}

