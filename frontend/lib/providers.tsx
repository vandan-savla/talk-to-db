"use client";

import { AuthProvider } from "./contexts/auth_context";
import { ChatProvider } from "./contexts/chat_context";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <ChatProvider>
                {children}
            </ChatProvider>
        </AuthProvider>
    );
}