"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/contexts/auth_context";
import { authApi } from "@/app/auth/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

export default function LoginPage() {
    const router = useRouter();
    const { setAuth } = useAuth();
    // const { toast } = useToast();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await authApi.login(email, password);
            setAuth(res.access_token, res.user);
            router.replace("/chat");
        } catch (err: any) {
            toast.error("Login Failed", {
                description: err.response?.data?.detail || "An error occurred during login.",
            });
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4">
            <Card className="w-full max-w-sm">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl">Sign in</CardTitle>
                    <CardDescription>Enter your email and password</CardDescription>
                </CardHeader>

                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                autoComplete="email"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                autoComplete="current-password"
                            />
                        </div>
                    </CardContent>

                    <CardFooter className="flex flex-col gap-3">
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? "Signing in..." : "Sign in"}
                        </Button>
                        <p className="text-sm text-muted-foreground text-center">
                            Don&apos;t have an account?{" "}
                            <Link href="/register" className="underline underline-offset-4 hover:text-primary">
                                Register
                            </Link>
                        </p>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}