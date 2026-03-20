import api from "../client/client";

export interface QueryResponse {
    answer: string;
    sql_query: string;
}

export const queryApi = {
    ask: async (question: string, conversation_id: string): Promise<QueryResponse> => {
        const { data } = await api.post("/v1/query", { question, conversation_id });
        return data;
    },
};