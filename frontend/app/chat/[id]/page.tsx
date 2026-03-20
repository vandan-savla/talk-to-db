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
    const { setActiveConversation } = useChat();

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
                <MessageList />
                <MessageInput />
            </div>
        </div>
    );
}

export default withAuth(SelectedChatPage);
