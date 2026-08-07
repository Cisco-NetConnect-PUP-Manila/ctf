import type { NextRequest } from "next/server";

const BACKEND_URL = (
  process.env.BACKEND_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8001"
).replace(/\/$/, "");

async function forward(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const target = new URL(`${BACKEND_URL}/${path.join("/")}`);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  const cookie = request.headers.get("cookie");
  if (contentType) headers.set("content-type", contentType);
  if (cookie) headers.set("cookie", cookie);

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body:
        request.method === "GET" || request.method === "HEAD"
          ? undefined
          : await request.arrayBuffer(),
      cache: "no-store",
    });

    const responseHeaders = new Headers();
    const upstreamContentType = upstream.headers.get("content-type");
    const setCookie = upstream.headers.get("set-cookie");
    if (upstreamContentType) responseHeaders.set("content-type", upstreamContentType);
    if (setCookie) responseHeaders.set("set-cookie", setCookie);

    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      {
        code: "BACKEND_UNAVAILABLE",
        message: "The competition server is temporarily unavailable.",
      },
      { status: 503 }
    );
  }
}

export const dynamic = "force-dynamic";
export const GET = forward;
export const POST = forward;
export const PATCH = forward;
export const DELETE = forward;

