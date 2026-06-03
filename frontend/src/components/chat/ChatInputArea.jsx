import { ChatInput } from "./ChatInput";

export function ChatInputArea({ onSubmit, isLoading, activeTab = "chat" }) {
  return (
    <div className="p-3 border-t border-vs-border bg-vs-bg">
      <ChatInput 
        onSubmit={onSubmit}
        isLoading={isLoading}
        compact={true}
        activeTab={activeTab}
      />
    </div>
  );
}