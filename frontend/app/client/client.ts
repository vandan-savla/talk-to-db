import axios from "axios";
import Cookies from "js-cookie";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
    headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const token = Cookies.get("token") || localStorage.getItem("token");
        if (token) config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// On 401 → clear token and redirect to login
api.interceptors.response.use(
    (res) => res,
    (error) => {
        if (error.response?.status === 401 && typeof window !== "undefined") {
            Cookies.remove("token", { path: "/" });
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default api;