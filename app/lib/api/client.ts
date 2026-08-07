import type { FieldErrors } from "./types";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001"
).replace(/\/$/, "");

type FastApiValidationError = {
  loc?: Array<string | number>;
  msg?: string;
};

type FastApiErrorBody = {
  detail?: string | FastApiValidationError[];
  code?: string;
  message?: string;
  field_errors?: FieldErrors;
};

export class ApiError extends Error {
  status: number;
  code?: string;
  fieldErrors: FieldErrors;

  constructor(
    message: string,
    options: { status: number; code?: string; fieldErrors?: FieldErrors }
  ) {
    super(message);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code;
    this.fieldErrors = options.fieldErrors ?? {};
  }
}

function validationErrors(details: FastApiValidationError[]): FieldErrors {
  return details.reduce<FieldErrors>((errors, item) => {
    const path = item.loc?.filter((part) => part !== "body").join(".");
    if (path && item.msg && !errors[path]) errors[path] = item.msg;
    return errors;
  }, {});
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Cannot reach the competition server. Check your connection and try again.",
      { status: 0, code: "NETWORK_ERROR" }
    );
  }

  if (response.ok) {
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  }

  let body: FastApiErrorBody = {};
  try {
    body = (await response.json()) as FastApiErrorBody;
  } catch {
    // Preserve the generic status message when the server returns no JSON.
  }

  const detailFields = Array.isArray(body.detail)
    ? validationErrors(body.detail)
    : {};
  const fieldErrors = { ...detailFields, ...(body.field_errors ?? {}) };
  const message =
    body.message ??
    (typeof body.detail === "string" ? body.detail : undefined) ??
    "The server could not complete this request.";

  throw new ApiError(message, {
    status: response.status,
    code: body.code,
    fieldErrors,
  });
}

