"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";

type WeightOut = { id: number; weight: string | number; date: string };
type UserMe = {
  id: number;
  email: string;
  height_cm: number | null;
  age: number | null;
};

function bmiFromKgAndCm(weightKg: number, heightCm: number): number {
  const hM = heightCm / 100;
  if (hM <= 0) return NaN;
  return weightKg / (hM * hM);
}

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

  const meQuery = useQuery({
    queryKey: ["users", "me"],
    queryFn: async () => (await api.get("/users/me")).data as UserMe,
  });

  const latestWeight = useMemo(() => {
    const items = weightsQuery.data ?? [];
    return items.length ? items[items.length - 1] : null;
  }, [weightsQuery.data]);

  const bmi = useMemo(() => {
    const h = meQuery.data?.height_cm;
    const w = latestWeight ? Number(latestWeight.weight) : NaN;
    if (h == null || h <= 0 || !Number.isFinite(w) || w <= 0) return null;
    return bmiFromKgAndCm(w, h);
  }, [meQuery.data?.height_cm, latestWeight]);

  const isLoading = weightsQuery.isLoading || meQuery.isLoading;
  const error = weightsQuery.error ?? meQuery.error;

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

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Latest weight</p>
          <p className="mt-2 text-3xl font-semibold">
            {latestWeight ? `${latestWeight.weight} kg` : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            {latestWeight ? latestWeight.date : ""}
          </p>
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Height</p>
          <p className="mt-2 text-3xl font-semibold">
            {meQuery.data?.height_cm != null ? `${meQuery.data.height_cm} cm` : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            <Link href="/settings" className="text-zinc-200 underline hover:text-white">
              Settings
            </Link>
          </p>
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">Age</p>
          <p className="mt-2 text-3xl font-semibold">
            {meQuery.data?.age != null ? meQuery.data.age : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">years</p>
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="text-sm text-zinc-300">BMI</p>
          <p className="mt-2 text-3xl font-semibold">
            {bmi != null && Number.isFinite(bmi) ? bmi.toFixed(1) : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            {bmi == null ? "Needs weight + height" : "kg / m²"}
          </p>
        </div>
      </div>
    </div>
  );
}
