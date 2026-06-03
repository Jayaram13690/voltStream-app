import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

export function RagContextViewer({ context }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!context) return null;
  
  return (
    <div className="mt-2">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm font-medium text-vs-primary hover:text-vs-primary/80 transition-colors w-full text-left"
      >
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        <span>Retrieved Context</span>
      </button>
      {isExpanded && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm text-vs-muted border border-vs-border">
          <pre className="whitespace-pre-wrap break-words overflow-x-auto max-h-64 overflow-y-auto">
            {context}
          </pre>
        </div>
      )}
    </div>
  );
}