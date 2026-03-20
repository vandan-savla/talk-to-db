"use client";

import { useEffect } from "react";
import { withAuth } from "@/lib/with_auth";
import { useChat } from "@/lib/contexts/chat_context";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageSquare, Database, Sparkles } from "lucide-react";
import { conversationsApi } from "@/app/conversations/conversations";


function ChatPage() {
    const { addConversation } = useChat();
    const router = useRouter();

    async function handleNewChat() {
        try {
            const convo = await conversationsApi.create();
            addConversation(convo);
            router.push(`/chat/${convo.id}`);
        } catch (err) {
            console.error("Failed to create conversation", err);
        }
    }

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar />
            <div className="flex flex-col flex-1 min-w-0 bg-accent/5">
                <div className="md:hidden h-12 shrink-0" />

                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto">
                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
                        <Database className="w-8 h-8 text-primary" />
                    </div>

                    <h1 className="text-3xl font-bold mb-2 tracking-tight">Talk to your Database</h1>
                    <p className="text-muted-foreground mb-8 text-lg">
                        Ask questions in natural language and get SQL results instantly.
                        Connect your data and start exploring.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                        <div className="p-4 rounded-xl border bg-card text-left hover:border-primary/50 transition-colors cursor-pointer group"
                            onClick={() => router.push('/explorer')}>
                            <div className="flex items-center gap-2 mb-2 font-semibold">
                                <Sparkles className="w-4 h-4 text-primary" />
                                <span>DB Explorer</span>
                            </div>
                            <p className="text-xs text-muted-foreground">Browse your tables and run manual SQL queries with the interactive explorer.</p>
                        </div>

                        <div className="p-4 rounded-xl border bg-card text-left hover:border-primary/50 transition-colors cursor-pointer group"
                            onClick={handleNewChat}>
                            <div className="flex items-center gap-2 mb-2 font-semibold">
                                <MessageSquare className="w-4 h-4 text-primary" />
                                <span>Natural Language</span>
                            </div>
                            <p className="text-xs text-muted-foreground">Just type "Show me the top 5 products by stock" and let the AI do the rest.</p>
                        </div>
                    </div>


                    <div className="mt-12 text-xs text-muted-foreground uppercase tracking-widest font-medium">
                        Select a chat from the sidebar to get started
                    </div>
                </div>
            </div>
        </div>
    );
}


export default withAuth(ChatPage);