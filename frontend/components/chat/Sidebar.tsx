"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
    MessageSquare,
    Plus,
    Trash2,
    Database,
    LogOut,
    Menu,
    X,
    Pencil,
    Check
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/lib/contexts/auth_context";
import { useChat } from "@/lib/contexts/chat_context";
import { conversationsApi } from "@/app/conversations/conversations";
import { cn } from "@/lib/utils";

export function Sidebar() {
    const router = useRouter();
    const { user, logout } = useAuth();
    const {
        conversations,
        activeConversationId,
        setActiveConversation,
        fetchConversations,
        isFetching,
        updateConversationTitle,
        deleteConversation,
        addConversation
    } = useChat();


    const [mobileOpen, setMobileOpen] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");
    const editInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        fetchConversations();
    }, [fetchConversations]);

    async function handleNewChat() {
        try {
            const convo = await conversationsApi.create();
            addConversation(convo);
            router.push(`/chat/${convo.id}`);
            setMobileOpen(false);
        } catch (err) {
            console.error("Failed to create conversation", err);
        }
    }

    function handleSelect(id: string) {
        if (editingId) return; // Don't switch while editing
        router.push(`/chat/${id}`);
        setMobileOpen(false);
    }

    async function handleStartEdit(e: React.MouseEvent, id: string, title: string) {
        e.stopPropagation();
        setEditingId(id);
        setEditValue(title);
        // Focus input after render
        setTimeout(() => editInputRef.current?.focus(), 0);
    }

    async function handleSaveEdit(e: React.FormEvent | React.MouseEvent) {
        e.preventDefault();
        e.stopPropagation();
        if (!editingId || !editValue.trim()) return;

        try {
            await updateConversationTitle(editingId, editValue.trim());
            setEditingId(null);
        } catch (err) {
            console.error("Failed to update title", err);
        }
    }

    function handleCancelEdit(e: React.MouseEvent) {
        e.stopPropagation();
        setEditingId(null);
    }

    const sidebarContent = (
        <div className="flex flex-col h-full bg-sidebar">
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
                >
                    <Plus className="w-4 h-4" />
                    New chat
                </Button>
            </div>

            <Separator />

            {/* Conversations */}
            <ScrollArea className="flex-1 px-2 py-2">
                {isFetching && conversations.length === 0 ? (
                    <div className="space-y-2 px-2">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="h-8 rounded-md bg-muted animate-pulse" />
                        ))}
                    </div>
                ) : conversations.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-8 px-4">
                        No conversations yet. Start a new chat!
                    </p>
                ) : (
                    <div className="space-y-1">
                        {conversations.map((c) => (
                            <div
                                key={c.id}
                                className={cn(
                                    "group relative flex items-center rounded-md text-sm hover:bg-accent transition-colors",
                                    activeConversationId === c.id && "bg-accent font-medium"
                                )}
                            >
                                <button
                                    onClick={() => handleSelect(c.id)}
                                    className="flex-1 text-left px-3 py-2 flex items-center gap-2 truncate"
                                    disabled={editingId === c.id}
                                >
                                    <MessageSquare className="w-3.5 h-3.5 shrink-0 text-muted-foreground" />
                                    {editingId === c.id ? (
                                        <form onSubmit={handleSaveEdit} className="flex-1 flex items-center">
                                            <input
                                                ref={editInputRef}
                                                value={editValue}
                                                onChange={(e) => setEditValue(e.target.value)}
                                                onBlur={() => setEditingId(null)}
                                                className="bg-transparent border-none focus:ring-0 p-0 w-full text-sm outline-none"
                                                onClick={(e) => e.stopPropagation()}
                                            />
                                        </form>
                                    ) : (
                                        <span className="truncate">{c.title}</span>
                                    )}
                                </button>

                                {editingId === c.id ? (
                                    <div className="flex items-center pr-1">
                                        <button
                                            onClick={(e) => handleSaveEdit(e)}
                                            className="p-1 hover:text-primary"
                                            type="button"
                                        >
                                            <Check className="w-3.5 h-3.5" />
                                        </button>
                                        <button
                                            onClick={(e) => handleCancelEdit(e)}
                                            className="p-1 hover:text-destructive"
                                            type="button"
                                        >
                                            <X className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                ) : (
                                    <div className="absolute right-1 hidden group-hover:flex items-center bg-accent/90 pl-1 rounded-sm">
                                        <button
                                            onClick={(e) => handleStartEdit(e, c.id, c.title)}
                                            className="p-1 text-muted-foreground hover:text-foreground"
                                            title="Rename"
                                        >
                                            <Pencil className="w-3.5 h-3.5" />
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (confirm("Are you sure you want to delete this conversation?")) {
                                                    deleteConversation(c.id);
                                                }
                                            }}
                                            className="p-1 text-muted-foreground hover:text-destructive"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                    </div>

                                )}
                            </div>
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
                    <span className="text-xs text-muted-foreground truncate max-w-120px">
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
                className="md:hidden fixed top-3 left-3 z-50 text-foreground"
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
