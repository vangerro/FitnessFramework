"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { api } from "../../lib/api";
import { getApiErrorMessage } from "../../lib/api-error";
import { setToken, getToken } from "../../lib/auth";
import TextField from "../../components/Forms/TextField";
import FormButton from "../../components/Forms/FormButton";

type LoginPayload = {
  email: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const token = getToken();
    if (token) router.replace("/dashboard");
  }, [router]);

  const mutation = useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const res = await api.post("/auth/login", payload);
      return res.data as { access_token: string };
    },
    onSuccess: (data) => {
      setToken(data.access_token);
      router.replace("/dashboard");
    },
  });

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Login</h1>

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
          placeholder="••••••••"
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
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
          Login
        </FormButton>

        <p className="text-center text-sm text-zinc-400">
          No account?{" "}
          <Link href="/register" className="text-zinc-100 underline">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}

