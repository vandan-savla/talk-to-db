"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, Plus, Trash2, Database, LogOut, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/app/auth/auth_store";
import { useChatStore } from "@/app/conversations/conversation_store";
import { useConversations, useCreateConversation } from "@/app/conversations/use_conversation";
import { cn } from "@/lib/utils";

export function Sidebar() {
    const router = useRouter();
    const { user, logout } = useAuthStore();
    const { activeConversationId, setActiveConversation } = useChatStore();
    const { data: conversations, isLoading } = useConversations();
    const createConversation = useCreateConversation();
    const [mobileOpen, setMobileOpen] = useState(false);

    async function handleNewChat() {
        const convo = await createConversation.mutateAsync();
        setActiveConversation(convo.id);
        setMobileOpen(false);
    }

    function handleSelect(id: string) {
        setActiveConversation(id);
        setMobileOpen(false);
    }

    const sidebarContent = (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Database className="w-5 h-5 text-primary" />
                    <span className="font-semibold text-sm">Talk to DB</span>
                </div>
                <Button
                    variant="ghost"
                    size="icon"
                    className="md:hidden"
                    onClick={() => setMobileOpen(false)}
                >
                    <X className="w-4 h-4" />
                </Button>
            </div>

            <div className="px-3 pb-3">
                <Button
                    onClick={handleNewChat}
                    className="w-full justify-start gap-2"
                    variant="outline"
                    size="sm"
                    disabled={createConversation.isPending}
                >
                    <Plus className="w-4 h-4" />
                    New chat
                </Button>
            </div>

            <Separator />

            {/* Conversations */}
            <ScrollArea className="flex-1 px-2 py-2">
                {isLoading ? (
                    <div className="space-y-2 px-2">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="h-8 rounded-md bg-muted animate-pulse" />
                        ))}
                    </div>
                ) : conversations?.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-8 px-4">
                        No conversations yet. Start a new chat!
                    </p>
                ) : (
                    <div className="space-y-1">
                        {conversations?.map((c) => (
                            <button
                                key={c.id}
                                onClick={() => handleSelect(c.id)}
                                className={cn(
                                    "w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-2 hover:bg-accent transition-colors truncate",
                                    activeConversationId === c.id && "bg-accent font-medium"
                                )}
                            >
                                <MessageSquare className="w-3.5 h-3.5 shrink-0 text-muted-foreground" />
                                <span className="truncate">{c.title}</span>
                            </button>
                        ))}
                    </div>
                )}
            </ScrollArea>

            <Separator />

            {/* Footer */}
            <div className="p-3 space-y-1">
                <button
                    onClick={() => router.push("/explorer")}
                    className="w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-2 hover:bg-accent transition-colors"
                >
                    <Database className="w-3.5 h-3.5 text-muted-foreground" />
                    Explorer
                </button>
                <div className="flex items-center justify-between px-3 py-2">
                    <span className="text-xs text-muted-foreground truncate">
                        {user?.email}
                    </span>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 shrink-0"
                        onClick={() => { logout(); router.replace("/login"); }}
                    >
                        <LogOut className="w-3.5 h-3.5" />
                    </Button>
                </div>
            </div>
        </div>
    );

    return (
        <>
            {/* Mobile toggle button */}
            <Button
                variant="ghost"
                size="icon"
                className="md:hidden fixed top-3 left-3 z-50"
                onClick={() => setMobileOpen(true)}
            >
                <Menu className="w-5 h-5" />
            </Button>

            {/* Mobile overlay */}
            {mobileOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black/40 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile drawer */}
            <aside
                className={cn(
                    "md:hidden fixed inset-y-0 left-0 z-50 w-72 bg-background border-r transform transition-transform duration-200",
                    mobileOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                {sidebarContent}
            </aside>

            {/* Desktop sidebar */}
            <aside className="hidden md:flex flex-col w-64 border-r bg-background shrink-0">
                {sidebarContent}
            </aside>
        </>
    );
}