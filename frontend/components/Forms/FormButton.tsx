"use client";

import { ButtonHTMLAttributes } from "react";

export default function FormButton(
  props: ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }
) {
  const { loading, disabled, className, ...rest } = props;
  return (
    <button
      disabled={disabled || loading}
      className={[
        "w-full rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60",
        className ?? "",
      ].join(" ")}
      {...rest}
    >
      {loading ? "Saving..." : props.children}
    </button>
  );
}

