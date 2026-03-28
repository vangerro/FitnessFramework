import { AxiosError, isAxiosError } from "axios";

type FastApiDetail =
  | string
  | { msg?: string; loc?: unknown[] }
  | Array<{ msg?: string; loc?: unknown[] }>;

export function getApiErrorMessage(err: unknown): string {
  if (!isAxiosError(err)) {
    if (err instanceof Error) return err.message;
    return "Something went wrong";
  }

  const ax = err as AxiosError<{ detail?: FastApiDetail }>;
  const detail = ax.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          const loc = Array.isArray(item.loc) ? item.loc.join(".") : "";
          return loc ? `${loc}: ${item.msg}` : String(item.msg);
        }
        return JSON.stringify(item);
      })
      .join(" ");
  }

  if (detail && typeof detail === "object" && "msg" in detail) {
    return String(detail.msg);
  }

  if (!ax.response && ax.code === "ERR_NETWORK") {
    return "Cannot reach API. Start the backend (e.g. uvicorn on port 8000) or set BACKEND_URL in frontend/.env.local.";
  }

  if (ax.response?.status && ax.response.status >= 500) {
    return "Server error. Check backend logs and that the database is running.";
  }

  if (ax.message) return ax.message;
  return "Request failed";
}
