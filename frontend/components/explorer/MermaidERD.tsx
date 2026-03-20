"use client";
import { useEffect, useRef } from "react";

interface SchemaData {
    columns: any[];
    relationships: any[];
}

export default function MermaidERD({ schema }: { schema: SchemaData | null }) {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const currentSchema = schema;
        if (!currentSchema) return;

        async function render() {
            if (!currentSchema) return;
            try {

                const mermaid = (await import("mermaid")).default;
                mermaid.initialize({
                    startOnLoad: false,
                    theme: document.documentElement.classList.contains("dark") ? "dark" : "default",
                    fontFamily: "inherit",
                    securityLevel: 'loose',
                });

                // Generate Mermaid ERD notation
                let erdText = "erDiagram\n";

                // Group columns by table
                const tables: Record<string, any[]> = {};
                currentSchema.columns.forEach((col: any) => {

                    // col is [table_name, column_name, data_type, is_primary] or 
                    // {table_name, column_name, data_type, is_primary} if dict
                    const tName = Array.isArray(col) ? col[0] : col.table_name;
                    const cName = Array.isArray(col) ? col[1] : col.column_name;
                    const dType = Array.isArray(col) ? col[2] : col.data_type;
                    const isPK = Array.isArray(col) ? col[3] : col.is_primary;

                    if (!tables[tName]) tables[tName] = [];
                    tables[tName].push({ cName, dType, isPK });
                });

                for (const [tName, cols] of Object.entries(tables)) {
                    erdText += `  ${tName} {\n`;
                    cols.forEach(c => {
                        const cleanType = c.dType.replace(/\s+/g, '-');
                        erdText += `    ${cleanType} ${c.cName}${c.isPK ? " PK" : ""}\n`;
                    });
                    erdText += "  }\n";
                }

                // Add relationships
                currentSchema.relationships.forEach((rel: any) => {

                    const tName = Array.isArray(rel) ? rel[0] : rel.table_name;
                    const cName = Array.isArray(rel) ? rel[1] : rel.column_name;
                    const ftName = Array.isArray(rel) ? rel[2] : rel.foreign_table_name;
                    const fcName = Array.isArray(rel) ? rel[3] : rel.foreign_column_name;
                    
                    erdText += `  ${tName} ||--o{ ${ftName} : "${cName}"\n`;
                });

                if (ref.current) {
                    ref.current.innerHTML = "";
                    const { svg } = await mermaid.render(`erd-${Date.now()}`, erdText.trim());
                    ref.current.innerHTML = svg;
                }
            } catch (err) {
                console.error("Mermaid error", err);
                if (ref.current) ref.current.innerHTML = "Failed to render ERD";
            }
        }
        render();
    }, [schema]);

    if (!schema) {
        return <div className="py-8 text-center text-sm text-muted-foreground animate-pulse">Loading schema...</div>;
    }

    return (
        <div className="relative w-full border rounded-xl bg-muted/30 overflow-hidden">
            <div
                ref={ref}
                className="overflow-auto flex justify-center py-6 min-h-[300px] max-h-[500px] w-full cursor-grab active:cursor-grabbing"
            />
            <div className="absolute bottom-2 right-2 text-[10px] text-muted-foreground bg-background/50 px-1.5 py-0.5 rounded border">
                Schema Diagram
            </div>
        </div>
    );
}
