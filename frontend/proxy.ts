import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
    const token = request.cookies.get("token")?.value;
    const { pathname } = request.nextUrl;

    // Proxy API requests
    if (pathname.startsWith("/api")) {
        const url = request.nextUrl.clone();
        url.href = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${pathname.replace("/api", "/v1")}`;
        return NextResponse.rewrite(url);
    }

    // Protected routes...
    const isProtectedRoute = pathname.startsWith("/chat") || pathname.startsWith("/explorer");
    // Auth routes: /login, /register
    const isAuthRoute = pathname.startsWith("/login") || pathname.startsWith("/register");

    if (isProtectedRoute && !token) {
        return NextResponse.redirect(new URL("/login", request.url));
    }

    if (isAuthRoute && token) {
        return NextResponse.redirect(new URL("/chat", request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/chat/:path*", "/explorer/:path*", "/login", "/register", "/api/:path*"],
};
