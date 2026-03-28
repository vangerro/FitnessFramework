"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";
import TextField from "../../components/Forms/TextField";
import NumberField from "../../components/Forms/NumberField";
import FormButton from "../../components/Forms/FormButton";

type MeasurementOut = {
  id: number;
  chest: string | number;
  waist: string | number;
  arms: string | number;
  date: string;
};

export default function MeasurementsPage() {
  return (
    <ProtectedRoute>
      <MeasurementsContent />
    </ProtectedRoute>
  );
}

function MeasurementsContent() {
  const queryClient = useQueryClient();
  const measurementsQuery = useQuery({
    queryKey: ["measurements"],
    queryFn: async () =>
      (await api.get("/measurements")).data as MeasurementOut[],
  });

  const [chest, setChest] = useState<number | "">("");
  const [waist, setWaist] = useState<number | "">("");
  const [arms, setArms] = useState<number | "">("");
  const [date, setDate] = useState("");

  const addMutation = useMutation({
    mutationFn: async () => {
      return (
        await api.post("/measurements", {
          chest,
          waist,
          arms,
          date,
        })
      ).data as MeasurementOut;
    },
    onSuccess: () => {
      setChest("");
      setWaist("");
      setArms("");
      setDate("");
      queryClient.invalidateQueries({ queryKey: ["measurements"] });
    },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Body Measurements</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">Add measurement</h2>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              addMutation.mutate();
            }}
          >
            <NumberField
              label="Chest"
              value={chest}
              onChange={(e) =>
                setChest(e.target.value === "" ? "" : Number(e.target.value))
              }
              required
            />
            <NumberField
              label="Waist"
              value={waist}
              onChange={(e) =>
                setWaist(e.target.value === "" ? "" : Number(e.target.value))
              }
              required
            />
            <NumberField
              label="Arms"
              value={arms}
              onChange={(e) =>
                setArms(e.target.value === "" ? "" : Number(e.target.value))
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
              disabled={chest === "" || waist === "" || arms === "" || !date}
            >
              Add
            </FormButton>
          </form>

          {addMutation.isError ? (
            <p className="mt-3 text-sm text-red-300">
              {String((addMutation.error as any)?.response?.data?.detail ?? "Failed to add measurement")}
            </p>
          ) : null}
        </div>

        <div className="rounded border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="mb-4 text-lg font-medium">List</h2>
          {measurementsQuery.isLoading ? (
            <p className="text-sm text-zinc-300">Loading...</p>
          ) : measurementsQuery.data?.length ? (
            <div className="space-y-2">
              {measurementsQuery.data.map((m) => (
                <div
                  key={m.id}
                  className="rounded border border-zinc-800 bg-zinc-950 px-3 py-2"
                >
                  <div className="flex items-center justify-between gap-4">
                    <p className="text-sm text-zinc-200">{m.date}</p>
                    <p className="text-sm text-zinc-300">
                      Chest {m.chest} | Waist {m.waist} | Arms {m.arms}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-zinc-300">No measurements yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

