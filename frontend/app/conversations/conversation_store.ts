import { create } from "zustand";
import { Message } from "./conversations";

interface ChatState {
    activeConversationId: string | null;
    // Optimistic messages appended immediately, before DB confirms
    pendingMessages: Message[];
    isLoading: boolean;

    setActiveConversation: (id: string | null) => void;
    addPendingMessage: (msg: Message) => void;
    clearPending: () => void;
    setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
    activeConversationId: null,
    pendingMessages: [],
    isLoading: false,

    setActiveConversation: (id) =>
        set({ activeConversationId: id, pendingMessages: [] }),

    addPendingMessage: (msg) =>
        set((state) => ({ pendingMessages: [...state.pendingMessages, msg] })),

    clearPending: () => set({ pendingMessages: [] }),

    setLoading: (loading) => set({ isLoading: loading }),
}));