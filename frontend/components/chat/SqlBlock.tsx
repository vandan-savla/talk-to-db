"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function SqlBlock({ sql }: { sql: string }) {
    const [open, setOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!sql) return null;

    async function copy() {
        await navigator.clipboard.writeText(sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    return (
        <div className="mt-3 rounded-lg border bg-muted/40 overflow-hidden text-xs">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-3 py-2 hover:bg-muted/60 transition-colors"
            >
                <span className="text-muted-foreground font-mono font-medium">SQL query</span>
                {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {open && (
                <div className="border-t">
                    <div className="flex justify-end px-3 pt-2">
                        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={copy}>
                            {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                        </Button>
                    </div>
                    <pre className="px-3 pb-3 overflow-x-auto font-mono text-xs leading-relaxed whitespace-pre">
                        {sql}
                    </pre>
                </div>
            )}
        </div>
    );
}