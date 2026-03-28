"use client";

import { InputHTMLAttributes } from "react";

export default function NumberField(
  props: InputHTMLAttributes<HTMLInputElement> & {
    label: string;
  }
) {
  const { label, className, ...rest } = props;
  return (
    <label className="block">
      <span className="mb-1 block text-sm text-zinc-200">{label}</span>
      <input
        type="number"
        step={(rest as any).step ?? "any"}
        className={[
          "w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-600",
          className ?? "",
        ].join(" ")}
        {...rest}
      />
    </label>
  );
}

