import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { conversationsApi } from "./conversations";
import { useAuthStore } from "../auth/auth_store";

// ── Conversations list ────────────────────────────────────────
export function useConversations() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return useQuery({
        queryKey: ["conversations"],
        queryFn: conversationsApi.list,
        enabled: isAuthenticated,         // only fetch when logged in
        staleTime: 5 * 60 * 1000,        // 5 min — no refetch on focus/tab switch
        gcTime: 30 * 60 * 1000,          // keep in cache 30 min
    });
}

// ── Messages for a conversation ───────────────────────────────
export function useMessages(conversationId: string | null) {
    return useQuery({
        queryKey: ["messages", conversationId],
        queryFn: () => conversationsApi.getMessages(conversationId!),
        enabled: !!conversationId,
        staleTime: Infinity,              // messages never go stale — append locally
        gcTime: 60 * 60 * 1000,          // keep 1hr in cache
    });
}

// ── Create new conversation ───────────────────────────────────
export function useCreateConversation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: conversationsApi.create,
        onSuccess: (newConvo) => {
            // Prepend to cached list immediately — no refetch needed
            queryClient.setQueryData(["conversations"], (old: any[] = []) => [
                newConvo,
                ...old,
            ]);
        },
    });
}

// ── Append a message pair to cache after query succeeds ───────
export function useAppendMessages(conversationId: string | null) {
    const queryClient = useQueryClient();

    return (userMsg: any, assistantMsg: any) => {
        queryClient.setQueryData(["messages", conversationId], (old: any[] = []) => [
            ...old,
            userMsg,
            assistantMsg,
        ]);
    };
}