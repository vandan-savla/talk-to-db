"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/auth_context";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isInitialized } = useAuth();

  useEffect(() => {
    // Wait for context to initialize
    if (!isInitialized) return;
    
    router.replace(isAuthenticated ? "/chat" : "/login");
  }, [isAuthenticated, isInitialized, router]);


  return null;
}
