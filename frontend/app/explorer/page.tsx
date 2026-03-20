"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Play, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { withAuth } from "@/lib/with_auth";
import api from "@/app/client/client";
import { toast } from "sonner";

// ── ERD component (mermaid) ───────────────────────────────────
import dynamic from "next/dynamic";
const MermaidERD = dynamic(() => import("@/components/explorer/MermaidERD"), { ssr: false });

// ── Results table ─────────────────────────────────────────────
function ResultsTable({ rows }: { rows: Record<string, any>[] }) {
    if (!rows.length) return <p className="text-sm text-muted-foreground p-4">No results</p>;
    const cols = Object.keys(rows[0]);

    return (
        <ScrollArea className="w-full">
            <table className="w-full text-xs">
                <thead>
                    <tr className="border-b bg-muted/50">
                        {cols.map((col) => (
                            <th key={col} className="text-left px-3 py-2 font-medium text-muted-foreground whitespace-nowrap">
                                {col}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, i) => (
                        <tr key={i} className="border-b hover:bg-muted/30 transition-colors">
                            {cols.map((col) => (
                                <td key={col} className="px-3 py-2 whitespace-nowrap font-mono">
                                    {String(row[col] ?? "null")}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </ScrollArea>
    );
}

// ── Main page ─────────────────────────────────────────────────
function ExplorerPage() {
    const router = useRouter();
    const [sql, setSql] = useState("SELECT * FROM products LIMIT 10;");
    const [results, setResults] = useState<Record<string, any>[] | null>(null);
    const [running, setRunning] = useState(false);
    const [copied, setCopied] = useState(false);

    async function runQuery() {
        if (!sql.trim()) return;
        setRunning(true);
        try {
            const { data } = await api.post("/v1/explorer/query", { sql });
            setResults(data.rows);
        } catch (err: any) {
            toast.error("Query failed", {
                description: err.response?.data?.detail || "Something went wrong",
            });
        } finally {
            setRunning(false);
        }
    }

    async function copySql() {
        await navigator.clipboard.writeText(sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b px-4 py-3 flex items-center gap-3">
                <Button variant="ghost" size="icon" onClick={() => router.push("/chat")}>
                    <ArrowLeft className="w-4 h-4" />
                </Button>
                <h1 className="font-semibold">Explorer</h1>
            </header>

            <div className="max-w-7xl mx-auto p-4 space-y-6">

                {/* ERD Section */}
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-base">Schema</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <MermaidERD />
                    </CardContent>
                </Card>

                {/* Query Editor */}
                <Card>
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-base">Query</CardTitle>
                            <div className="flex gap-2">
                                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={copySql}>
                                    {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                                </Button>
                                <Button size="sm" onClick={runQuery} disabled={running} className="gap-1.5">
                                    <Play className="w-3.5 h-3.5" />
                                    {running ? "Running..." : "Run"}
                                </Button>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Textarea
                            value={sql}
                            onChange={(e) => setSql(e.target.value)}
                            className="font-mono text-sm min-h-120px resize-y"
                            placeholder="SELECT * FROM ..."
                            spellCheck={false}
                        />
                        {results !== null && (
                            <>
                                <Separator />
                                <div>
                                    <p className="text-xs text-muted-foreground mb-2">
                                        {results.length} row{results.length !== 1 ? "s" : ""}
                                    </p>
                                    <div className="rounded-md border overflow-hidden">
                                        <ResultsTable rows={results} />
                                    </div>
                                </div>
                            </>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

export default withAuth(ExplorerPage);