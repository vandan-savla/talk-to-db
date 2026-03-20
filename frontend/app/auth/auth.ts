import api from "../client/client";

export interface User {
    id: string;
    email: string;
    full_name: string | null;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export const authApi = {
    register: async (email: string, password: string, full_name?: string): Promise<AuthResponse> => {
        const { data } = await api.post("/v1/auth/register", { email, password, full_name });
        return data;
    },

    login: async (email: string, password: string): Promise<AuthResponse> => {

        const { data } = await api.post("/v1/auth/login", { email, password }, { timeout: 5000 });
        return data;
    },
};