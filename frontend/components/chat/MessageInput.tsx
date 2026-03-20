"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useChatStore } from "@/app/conversations/conversation_store";
import { useAppendMessages, useCreateConversation } from "@/app/conversations/use_conversation";
import { queryApi } from "@/app/query/query";
import { toast } from "sonner";

export function MessageInput() {
    const [input, setInput] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);


    const {
        activeConversationId,
        setActiveConversation,
        addPendingMessage,
        clearPending,
        setLoading,
        isLoading,
    } = useChatStore();

    const appendMessages = useAppendMessages(activeConversationId);
    const createConversation = useCreateConversation();

    async function handleSend() {
        const question = input.trim();
        if (!question || isLoading) return;

        setInput("");

        // Create conversation if none active
        let conversationId = activeConversationId;
        if (!conversationId) {
            const convo = await createConversation.mutateAsync();
            conversationId = convo.id;
            setActiveConversation(conversationId);
        }

        // Optimistic user message
        const tempUserMsg = {
            id: `temp-user-${Date.now()}`,
            role: "user" as const,
            content: { question },
            created_at: new Date().toISOString(),
        };
        addPendingMessage(tempUserMsg);
        setLoading(true);

        try {
            const res = await queryApi.ask(question, conversationId);

            // Append real messages to cache, clear pending
            const assistantMsg = {
                id: `temp-assistant-${Date.now()}`,
                role: "assistant" as const,
                content: { answer: res.answer, sql_query: res.sql_query },
                created_at: new Date().toISOString(),
            };
            appendMessages(tempUserMsg, assistantMsg);
            clearPending();
        } catch (err: any) {
            clearPending();
            toast.error("Query Failed", {
                description: err.response?.data?.detail || "An error occurred while processing your query.",
            });
        } finally {
            setLoading(false);
            textareaRef.current?.focus();
        }
    }

    function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }

    return (
        <div className="border-t bg-background px-4 py-3">
            <div className="max-w-3xl mx-auto flex gap-2 items-end">
                <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything about your data..."
                    rows={1}
                    className="resize-none min-h-44px max-h-32 overflow-y-auto"
                    disabled={isLoading}
                />
                <Button
                    size="icon"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    className="shrink-0 h-11 w-11"
                >
                    <Send className="w-4 h-4" />
                </Button>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">
                Press Enter to send, Shift+Enter for new line
            </p>
        </div>
    );
}