import { ChatInput } from "./ChatInput";

export function ChatInputArea({ onSubmit, isLoading }) {
  return (
    <div className="p-3 border-t border-vs-border bg-vs-bg">
      <ChatInput 
        onSubmit={onSubmit}
        isLoading={isLoading}
        compact={true}
      />
    </div>
  );
}