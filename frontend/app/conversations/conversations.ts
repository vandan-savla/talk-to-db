import api from "../client/client";

export interface Conversation {
    id: string;
    title: string;
    created_at: string;
}

export interface Message {
    id: string;
    role: "user" | "assistant";
    content: {
        question?: string;
        answer?: string;
        sql_query?: string;
    };
    created_at: string;
}

export const conversationsApi = {
    // Create new conversation — returns id used as thread_id
    create: async (): Promise<Conversation> => {
        const { data } = await api.post("/v1/conversations");
        return data;
    },

    // List all conversations for current user
    list: async (): Promise<Conversation[]> => {
        const { data } = await api.get("/v1/conversations");
        return data;
    },

    // Get messages for a conversation
    getMessages: async (conversationId: string): Promise<Message[]> => {
        const { data } = await api.get(`/v1/conversations/${conversationId}/messages`);
        return data;
    },
};