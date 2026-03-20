"use client";

import { useEffect, useRef } from "react";

// Hardcode your master DB schema here
// Update this whenever your schema changes
const ERD = `
erDiagram
  products {
    integer product_id PK
    varchar product_name
    numeric price
    integer stock_quantity
  }
`;

export default function MermaidERD() {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        async function render() {
            const mermaid = (await import("mermaid")).default;
            mermaid.initialize({
                startOnLoad: false,
                theme: document.documentElement.classList.contains("dark") ? "dark" : "default",
                fontFamily: "inherit",
            });
            if (ref.current) {
                ref.current.innerHTML = "";
                const { svg } = await mermaid.render("erd-diagram", ERD.trim());
                ref.current.innerHTML = svg;
            }
        }
        render();
    }, []);

    return (
        <div
            ref={ref}
            className="overflow-x-auto flex justify-center py-2 min-h-120px"
        />
    );
}