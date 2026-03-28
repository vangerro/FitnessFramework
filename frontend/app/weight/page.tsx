"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";
import TextField from "../../components/Forms/TextField";
import NumberField from "../../components/Forms/NumberField";
import FormButton from "../../components/Forms/FormButton";

type WeightOut = { id: number; weight: string | number; date: string };

export default function WeightPage() {
  return (
    <ProtectedRoute>
      <WeightContent />
    </ProtectedRoute>
  );
}

function WeightContent() {
  const queryClient = useQueryClient();
  const weightsQuery = useQuery({
    queryKey: ["weight"],
    queryFn: async () => (await api.get("/weight")).data as WeightOut[],
  });

  const [weight, setWeight] = useState<number | "">("");
  const [date, setDate] = useState("");

  const addMutation = useMutation({
    mutationFn: async () => {
      return (await api.post("/weight", { weight, date })).data as WeightOut;
    },
    onSuccess: () => {
      setWeight("");
      setDate("");
      queryClient.invalidateQueries({ queryKey: ["weight"] });
    },
  });

  const chartData = useMemo(() => {
    return (weightsQuery.data ?? []).map((w) => ({
      date: w.date,
      weight: Number(w.weight),
    }));
  }, [weightsQuery.data]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Weight</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Add entry</h2>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              addMutation.mutate();
            }}
          >
            <NumberField
              label="Weight (kg)"
              value={weight}
              onChange={(e) =>
                setWeight(e.target.value === "" ? "" : Number(e.target.value))
              }
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
              loading={addMutation.isPending}
              disabled={weight === "" || !date}
            >
              Add
            </FormButton>
          </form>

          {addMutation.isError ? (
            <p className="mt-3 text-sm text-red-300">
              {String((addMutation.error as any)?.response?.data?.detail ?? "Failed to add weight")}
            </p>
          ) : null}
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Chart</h2>
          {weightsQuery.isLoading ? (
            <p className="text-sm text-zinc-300">Loading...</p>
          ) : weightsQuery.error ? (
            <p className="text-sm text-red-300">
              {String((weightsQuery.error as any)?.response?.data?.detail ?? "Failed to load")}
            </p>
          ) : chartData.length ? (
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
                  <XAxis dataKey="date" hide />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="weight" stroke="#60a5fa" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-zinc-300">No weight entries yet.</p>
          )}
        </div>
      </div>

      <div className="mt-6 rounded border border-zinc-800 bg-zinc-900 p-4">
        <h2 className="mb-4 text-lg font-medium">Entries</h2>
        {weightsQuery.isLoading ? (
          <p className="text-sm text-zinc-300">Loading...</p>
        ) : weightsQuery.data?.length ? (
          <div className="space-y-2">
            {weightsQuery.data.map((w) => (
              <div
                key={w.id}
                className="flex items-center justify-between rounded border border-zinc-800 bg-zinc-950 px-3 py-2"
              >
                <p className="text-sm text-zinc-200">{w.date}</p>
                <p className="font-medium">{w.weight} kg</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-300">No entries yet.</p>
        )}
      </div>
    </div>
  );
}

