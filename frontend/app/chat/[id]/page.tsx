"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { withAuth } from "@/lib/with_auth";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageList } from "@/components/chat/MessageList";
import { MessageInput } from "@/components/chat/MessageInput";
import { useChat } from "@/lib/contexts/chat_context";

function SelectedChatPage() {
    const { id } = useParams();
    const { setActiveConversation, conversations } = useChat();
    const activeConvo = conversations.find(c => c.id === id);


    useEffect(() => {
        if (id) {
            setActiveConversation(id as string);
        }
    }, [id, setActiveConversation]);

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar />
            <div className="flex flex-col flex-1 min-w-0">
                <div className="md:hidden h-12 shrink-0" />
                
                {/* Chat Header */}
                <header className="border-b px-4 py-3 flex items-center justify-between bg-background/80 backdrop-blur-sm sticky top-0 z-10">
                    <div className="flex items-center gap-2 truncate">
                        <h2 className="font-semibold truncate text-sm">
                            {activeConvo?.title || "Loading..."}
                        </h2>
                    </div>
                </header>

                <MessageList />
                <MessageInput />
            </div>
        </div>
    );

}

export default withAuth(SelectedChatPage);
