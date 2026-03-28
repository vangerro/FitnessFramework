import type { Metadata } from "next";

import "./globals.css";
import Providers from "./providers";
import Navbar from "../components/Navbar";

export const metadata: Metadata = {
  title: "FitnessFramework",
  description: "Fitness tracking web app",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-dvh bg-zinc-950 text-zinc-100">
        <Providers>
          <Navbar />
          <main className="mx-auto w-full max-w-5xl px-4 py-6">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}

