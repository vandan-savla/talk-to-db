"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useRouter } from "next/navigation";

import { Conversation, Message, conversationsApi } from "@/app/conversations/conversations";

interface ChatContextType {
    conversations: Conversation[];
    activeConversationId: string | null;
    messagesByConvo: Record<string, Message[]>;
    pendingMessages: Message[];
    isLoading: boolean;
    isFetching: boolean;
    setActiveConversation: (id: string | null) => void;
    fetchConversations: () => Promise<void>;
    fetchMessages: (id: string) => Promise<void>;
    addConversation: (convo: Conversation) => void;
    updateConversationTitle: (id: string, title: string) => Promise<void>;
    deleteConversation: (id: string) => Promise<void>;
    addPendingMessage: (msg: Message) => void;

    clearPending: () => void;
    setLoading: (loading: boolean) => void;
    appendRealMessages: (id: string, userMsg: Message, assistantMsg: Message) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
    const [messagesByConvo, setMessagesByConvo] = useState<Record<string, Message[]>>({});
    const [pendingMessages, setPendingMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFetching, setIsFetching] = useState(false);

    const router = useRouter();

    const fetchConversations = useCallback(async () => {

        setIsFetching(true);
        try {
            const data = await conversationsApi.list();
            setConversations(data);
        } finally {
            setIsFetching(false);
        }
    }, []);

    const fetchMessages = useCallback(async (id: string) => {
        if (!id) return;
        setIsFetching(true);
        try {
            const data = await conversationsApi.getMessages(id);
            setMessagesByConvo(prev => ({ ...prev, [id]: data }));
        } finally {
            setIsFetching(false);
        }
    }, []);

    // Fetch messages when active conversation changes
    useEffect(() => {
        if (activeConversationId && !messagesByConvo[activeConversationId]) {
            fetchMessages(activeConversationId);
        }
    }, [activeConversationId, fetchMessages, messagesByConvo]);

    // Initial Load from localStorage
    useEffect(() => {
        const savedConvos = localStorage.getItem("chat_conversations");
        const savedMessages = localStorage.getItem("chat_messages");
        if (savedConvos) setConversations(JSON.parse(savedConvos));
        if (savedMessages) setMessagesByConvo(JSON.parse(savedMessages));

        fetchConversations();
    }, [fetchConversations]);

    // Persist to localStorage
    useEffect(() => {
        localStorage.setItem("chat_conversations", JSON.stringify(conversations));
    }, [conversations]);

    useEffect(() => {
        localStorage.setItem("chat_messages", JSON.stringify(messagesByConvo));
    }, [messagesByConvo]);

    const addConversation = (convo: Conversation) => {
        setConversations(prev => [convo, ...prev]);
    };

    const updateConversationTitle = async (id: string, title: string) => {
        await conversationsApi.updateTitle(id, title);
        setConversations(prev => prev.map(c => c.id === id ? { ...c, title } : c));
    };

    const deleteConversation = async (id: string) => {
        await conversationsApi.delete(id);
        setConversations(prev => prev.filter(c => c.id !== id));
        setMessagesByConvo(prev => {
            const next = { ...prev };
            delete next[id];
            return next;
        });

        if (activeConversationId === id) {
            setActiveConversationId(null);
            router.push("/chat");
        }
    };


    const appendRealMessages = (id: string, userMsg: Message, assistantMsg: Message) => {

        setMessagesByConvo(prev => {
            const current = prev[id] || [];
            return { ...prev, [id]: [...current, userMsg, assistantMsg] };
        });
    };

    return (
        <ChatContext.Provider value={{
            conversations,
            activeConversationId,
            messagesByConvo,
            pendingMessages,
            isLoading,
            isFetching,
            setActiveConversation: setActiveConversationId,
            fetchConversations,
            fetchMessages,
            addConversation,
            updateConversationTitle,
            deleteConversation,
            addPendingMessage: (msg) => setPendingMessages(prev => [...prev, msg]),

            clearPending: () => setPendingMessages([]),
            setLoading: setIsLoading,
            appendRealMessages
        }}>
            {children}
        </ChatContext.Provider>
    );
}

export function useChat() {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error("useChat must be used within a ChatProvider");
    }
    return context;
}
