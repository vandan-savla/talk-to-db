"use client";

import { withAuth } from "@/lib/with_auth";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageList } from "@/components/chat/MessageList";
import { MessageInput } from "@/components/chat/MessageInput";

function ChatPage() {
    return (
        <div className="flex h-screen overflow-hidden bg-background">
            <Sidebar />
            <div className="flex flex-col flex-1 min-w-0">
                {/* Add top padding on mobile so hamburger button doesn't overlap */}
                <div className="md:hidden h-12 shrink-0" />
                <MessageList />
                <MessageInput />
            </div>
        </div>
    );
}

export default withAuth(ChatPage);