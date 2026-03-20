"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import Cookies from "js-cookie";

interface User {
    id: string;
    email: string;
    full_name: string | null;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    setAuth: (token: string, user: User) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);

    // Initialize from storage
    useEffect(() => {
        const savedToken = Cookies.get("token");
        const savedUser = localStorage.getItem("user");
        if (savedToken) setToken(savedToken);
        if (savedUser) setUser(JSON.parse(savedUser));
    }, []);

    const setAuth = (newToken: string, newUser: User) => {
        setToken(newToken);
        setUser(newUser);
        Cookies.set("token", newToken, { expires: 7, path: "/" });
        localStorage.setItem("user", JSON.stringify(newUser));
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        Cookies.remove("token", { path: "/" });
        localStorage.removeItem("user");
    };

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isAuthenticated: !!token,
            setAuth,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
