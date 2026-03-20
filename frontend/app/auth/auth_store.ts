import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "./auth";

interface AuthState {
    token: string | null;
    user: User | null;
    isAuthenticated: boolean;
    setAuth: (token: string, user: User) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: null,
            user: null,
            isAuthenticated: false,

            setAuth: (token, user) => {
                localStorage.setItem("token", token);
                set({ token, user, isAuthenticated: true });
            },

            logout: () => {
                localStorage.removeItem("token");
                localStorage.removeItem("user");
                set({ token: null, user: null, isAuthenticated: false });
            },
        }),
        {
            name: "auth-storage", // localStorage key
            partialize: (state) => ({
                token: state.token,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);