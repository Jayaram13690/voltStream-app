import { Input } from "../ui/Input"
import { Button } from "../ui/Button"
import { Spinner } from "../ui/Spinner"
import { useState } from "react"

export function ChatInput({ onSubmit, isLoading, compact = false, activeTab = "chat" }) {
  const [value, setValue] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (value.trim() && !isLoading) {
      onSubmit(e, value)
      setValue('')
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className={compact ? "flex gap-2 items-center" : "p-4 border-t border-vs-border bg-vs-bg/50"}>
      <Input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={activeTab === "chat"
          ? "Ask anything about energy, sustainability, or VoltStream..."
          : "Ask questions from the uploaded knowledge base..."}
        className="flex-1"
        disabled={isLoading}
        onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
      />
      <Button 
        type="submit"
        disabled={isLoading || !value.trim()}
        className={compact ? "px-3 py-2 bg-vs-primary text-white rounded-lg hover:bg-vs-primary/90 transition-colors min-w-[80px]" : "px-4 py-2 bg-vs-primary text-white rounded-xl hover:bg-vs-primary/90 transition-colors min-w-[100px]"}
      >
        {isLoading ? <Spinner className="w-4 h-4" /> : compact ? '▶' : '▶ Send'}
      </Button>
    </form>
  )
}