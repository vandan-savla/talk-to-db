"use client";

import { useEffect, useRef } from "react";
import { SqlBlock } from "./SqlBlock";
import { useChat } from "@/lib/contexts/chat_context";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MessageList() {

    const bottomRef = useRef<HTMLDivElement>(null);
    const {
        activeConversationId,
        messagesByConvo,
        pendingMessages,
        isLoading,
        fetchMessages
    } = useChat();

    const messages = activeConversationId ? messagesByConvo[activeConversationId] || [] : [];

    useEffect(() => {
        if (activeConversationId) {
            fetchMessages(activeConversationId);
        }
    }, [activeConversationId, fetchMessages]);

    // Auto scroll to bottom on new message
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, pendingMessages, isLoading]);

    if (!activeConversationId) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center px-6">
                <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                    <span className="text-2xl">🗄️</span>
                </div>
                <h2 className="font-semibold text-lg">Ask your database anything</h2>
                <p className="text-sm text-muted-foreground max-w-sm">
                    Start a new chat and ask questions in plain English. The AI will write and run the SQL for you.
                </p>
            </div>
        );
    }

    const allMessages = [...messages, ...pendingMessages];

    if (allMessages.length === 0 && !isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <p className="text-sm text-muted-foreground">Send a message to get started</p>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {allMessages.map((msg) => {
                const isUser = msg.role === "user";
                const text = isUser ? msg.content.question : msg.content.answer;
                const sql = !isUser ? msg.content.sql_query : undefined;

                return (
                    <div key={msg.id} className={cn("flex", isUser ? "justify-end" : "justify-start")}>
                        <div className={cn(
                            "max-w-[85%] md:max-w-[70%] rounded-2xl px-4 py-3 text-sm",
                            isUser
                                ? "bg-primary text-primary-foreground rounded-br-sm"
                                : "bg-muted rounded-bl-sm"
                        )}>
                            {isUser ? (
                                <p>{text}</p>
                            ) : (
                                <div className="prose prose-sm dark:prose-invert max-w-none">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            table: ({ node, ...props }) => (
                                                <div className="my-2 border rounded-md overflow-hidden bg-background shadow-sm">
                                                    <div className="overflow-auto max-h-[250px]">
                                                        <table className="min-w-full divide-y bg-background relative border-collapse" {...props} />
                                                    </div>
                                                </div>
                                            ),
                                            thead: ({ node, ...props }) => <thead className="bg-muted/80 backdrop-blur-sm sticky top-0 z-10" {...props} />,
                                            th: ({ node, ...props }) => <th className="px-3 py-2 text-left font-semibold text-[12px] border-b whitespace-nowrap" {...props} />,
                                            td: ({ node, ...props }) => <td className="px-3 py-1.5 text-[12px] border-b whitespace-nowrap text-muted-foreground" {...props} />
                                        }}

                                    >
                                        {text || ""}
                                    </ReactMarkdown>
                                    {sql && <SqlBlock sql={sql} />}
                                </div>

                            )}
                        </div>
                    </div>
                );
            })}

            {/* Loading bubble */}
            {isLoading && (
                <div className="flex justify-start">
                    <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3">
                        <div className="flex gap-1 items-center h-4">
                            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
                            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:150ms]" />
                            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:300ms]" />
                        </div>
                    </div>
                </div>
            )}

            <div ref={bottomRef} />
        </div>
    );
}
