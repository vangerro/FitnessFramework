"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { clearToken } from "../lib/auth";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthPage = pathname === "/login" || pathname === "/register";

  const onLogout = () => {
    clearToken();
    router.replace("/login");
  };

  return (
    <header className="border-b border-zinc-800 bg-zinc-950">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-4">
          <Link href={isAuthPage ? "/" : "/dashboard"} className="font-semibold">
            FitnessFramework
          </Link>
          {isAuthPage ? (
            <div className="flex items-center gap-3">
              <Link href="/login" className="text-sm text-zinc-300 hover:text-white">
                Login
              </Link>
              <Link href="/register" className="text-sm text-zinc-300 hover:text-white">
                Register
              </Link>
            </div>
          ) : (
            <div className="hidden items-center gap-3 md:flex">
              <Link href="/dashboard" className="text-sm text-zinc-300 hover:text-white">
                Dashboard
              </Link>
              <Link href="/workouts" className="text-sm text-zinc-300 hover:text-white">
                Workouts
              </Link>
              <Link href="/weight" className="text-sm text-zinc-300 hover:text-white">
                Weight
              </Link>
              <Link
                href="/measurements"
                className="text-sm text-zinc-300 hover:text-white"
              >
                Measurements
              </Link>
            </div>
          )}
        </div>
        {!isAuthPage ? (
          <button
            type="button"
            onClick={onLogout}
            className="rounded bg-zinc-800 px-3 py-1 text-sm text-zinc-100 hover:bg-zinc-700"
          >
            Logout
          </button>
        ) : null}
      </nav>
    </header>
  );
}
