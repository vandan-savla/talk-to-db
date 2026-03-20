"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/auth_context";

export function withAuth<T extends object>(Component: React.ComponentType<T>) {
    return function ProtectedRoute(props: T) {
        const router = useRouter();
        const { isAuthenticated } = useAuth();

        useEffect(() => {
            if (!isAuthenticated) {
                router.replace("/login");
            }
        }, [isAuthenticated, router]);

        if (!isAuthenticated) return null;

        return <Component {...props} />;
    };
}