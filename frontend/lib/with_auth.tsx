"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/app/auth/auth_store";

export function withAuth<T extends object>(Component: React.ComponentType<T>) {
    return function ProtectedRoute(props: T) {
        const router = useRouter();
        const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

        useEffect(() => {
            if (!isAuthenticated) {
                router.replace("/login");
            }
        }, [isAuthenticated, router]);

        if (!isAuthenticated) return null;

        return <Component {...props} />;
    };
}