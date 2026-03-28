"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import ProtectedRoute from "../../components/ProtectedRoute";
import { api } from "../../lib/api";
import NumberField from "../../components/Forms/NumberField";
import FormButton from "../../components/Forms/FormButton";

type UserMe = {
  id: number;
  email: string;
  height_cm: number | null;
  age: number | null;
};

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}

function SettingsContent() {
  const queryClient = useQueryClient();
  const [heightCm, setHeightCm] = useState<number | "">("");
  const [age, setAge] = useState<number | "">("");

  const meQuery = useQuery({
    queryKey: ["users", "me"],
    queryFn: async () => (await api.get("/users/me")).data as UserMe,
  });

  useEffect(() => {
    if (!meQuery.data) return;
    setHeightCm(meQuery.data.height_cm ?? "");
    setAge(meQuery.data.age ?? "");
  }, [meQuery.data]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const res = await api.patch("/users/me", {
        height_cm: heightCm === "" ? null : heightCm,
        age: age === "" ? null : age,
      });
      return res.data as UserMe;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", "me"] });
    },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Settings</h1>

      {meQuery.isLoading ? (
        <p className="text-sm text-zinc-300">Loading...</p>
      ) : meQuery.error ? (
        <p className="text-sm text-red-300">
          {String((meQuery.error as any)?.response?.data?.detail ?? "Failed to load profile")}
        </p>
      ) : (
        <div className="max-w-md rounded border border-zinc-800 bg-zinc-900 p-4">
          <p className="mb-4 text-sm text-zinc-400">
            Used for BMI on the dashboard (with your latest weight). Weight is still logged on the
            Weight page.
          </p>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              saveMutation.mutate();
            }}
          >
            <NumberField
              label="Height (cm)"
              step={0.1}
              value={heightCm}
              onChange={(e) =>
                setHeightCm(e.target.value === "" ? "" : Number(e.target.value))
              }
            />
            <NumberField
              label="Age (years)"
              step={1}
              value={age}
              onChange={(e) => setAge(e.target.value === "" ? "" : Number(e.target.value))}
            />
            <FormButton type="submit" loading={saveMutation.isPending}>
              Save
            </FormButton>
          </form>

          {saveMutation.isError ? (
            <p className="mt-3 text-sm text-red-300">
              {String(
                (saveMutation.error as any)?.response?.data?.detail ?? "Failed to save settings"
              )}
            </p>
          ) : null}
          {saveMutation.isSuccess ? (
            <p className="mt-3 text-sm text-zinc-300">Saved.</p>
          ) : null}
        </div>
      )}
    </div>
  );
}
