"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getToken } from "../lib/auth";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [status, setStatus] = useState<"checking" | "authed" | "anon">("checking");

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setStatus("anon");
      router.replace("/login");
      return;
    }
    setStatus("authed");
  }, [router]);

  if (status === "checking") {
    return (
      <div className="text-sm text-zinc-300" aria-busy="true">
        Loading...
      </div>
    );
  }

  if (status === "anon") {
    return null;
  }

  return <>{children}</>;
}
