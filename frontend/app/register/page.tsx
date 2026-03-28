"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { api } from "../../lib/api";
import { getApiErrorMessage } from "../../lib/api-error";
import { getToken } from "../../lib/auth";
import TextField from "../../components/Forms/TextField";
import FormButton from "../../components/Forms/FormButton";

type RegisterPayload = {
  email: string;
  password: string;
};

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const token = getToken();
    if (token) router.replace("/dashboard");
  }, [router]);

  const mutation = useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      const res = await api.post("/auth/register", payload);
      return res.data as { id: number; email: string };
    },
    onSuccess: () => {
      router.replace("/login");
    },
  });

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Register</h1>

      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate({ email: email.trim(), password });
        }}
      >
        <TextField
          label="Email"
          value={email}
          placeholder="you@example.com"
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          placeholder="123456"
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          required
        />

        {mutation.isError ? (
          <p className="text-sm text-red-300">{getApiErrorMessage(mutation.error)}</p>
        ) : null}

        <FormButton
          type="submit"
          loading={mutation.isPending}
          disabled={!email || !password}
        >
          Create account
        </FormButton>

        {mutation.isSuccess ? (
          <p className="pt-2 text-sm text-zinc-300">Redirecting to login...</p>
        ) : null}

        <p className="text-center text-sm text-zinc-400">
          Already have an account?{" "}
          <Link href="/login" className="text-zinc-100 underline">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}

