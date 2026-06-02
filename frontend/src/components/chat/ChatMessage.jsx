import clsx from "clsx";

export function ChatMessage({ role, content, timestamp, compact = false }) {
  const isUser = role === 'user'
  
  // Format content with enhanced markdown support
  const formatContent = (text) => {
    if (!text) return text
    
    // Replace headers (including ####)
    let formatted = text
      .replace(/^####\s+(.*$)/gm, '<h4 class="font-medium mt-2 mb-1 text-vs-primary">$1</h4>')
      .replace(/^###\s+(.*$)/gm, '<h3 class="font-semibold mt-2 mb-1">$1</h3>')
      .replace(/^##\s+(.*$)/gm, '<h2 class="font-bold mt-3 mb-2">$1</h2>')
      .replace(/^#\s+(.*$)/gm, '<h1 class="font-bold text-xl mt-4 mb-3">$1</h1>')
      
    // Replace lists with proper wrapping
    formatted = formatted
      .replace(/^\*\s+(.*$)/gm, '<li>$1</li>')
      .replace(/^•\s+(.*$)/gm, '<li>$1</li>')
      .replace(/^-\s+(.*$)/gm, '<li>$1</li>')
      
    // Wrap consecutive list items in ul tags with tighter spacing
    formatted = formatted.replace(/((?:<li>.*<\/li>\n)+)/g, '<ul class="list-disc pl-4 mt-1 mb-2">$1</ul>')
    
    // Replace horizontal rules
    formatted = formatted.replace(/^---\s*$/gm, '<hr class="my-3 border-vs-border" />')
    
    // Replace code blocks
    formatted = formatted.replace(/```(.*?)```/gs, '<pre class="bg-gray-100 p-2 rounded mt-2 mb-2 overflow-x-auto text-sm">$1</pre>')
    
    // Replace bold and italic
    formatted = formatted
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
    
    // Replace checkmarks and other symbols
    formatted = formatted
      .replace(/^✅\s+(.*$)/gm, '<div class="flex items-start gap-2 mt-2"><span class="text-green-600 mt-0.5">✅</span><span>$1</span></div>')
      .replace(/^❌\s+(.*$)/gm, '<div class="flex items-start gap-2 mt-2"><span class="text-red-600 mt-0.5">❌</span><span>$1</span></div>')
      .replace(/^•\s+(.*$)/gm, '<div class="flex items-start gap-2 mt-1"><span class="text-gray-400 mt-1">•</span><span>$1</span></div>')
    
    // Replace links
    formatted = formatted.replace(
      /\[(.*?)\]\((.*?)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-vs-primary hover:underline">$1</a>'
    )
    
    // Add paragraph tags for better spacing, but be more selective
    formatted = formatted.replace(/^(?!<[a-z]|\s*$|\*|•|-|#|##|###|####|✅|❌)(.*$)/gim, '<p class="mb-2">$1</p>')
    
    // Clean up multiple newlines and empty paragraphs
    formatted = formatted
      .replace(/<p class="mb-2">\s*<\/p>/g, '')
      .replace(/\n\n+/g, '\n')
      .replace(/<\/p>\n<p class="mb-2">/g, '</p><p class="mb-2">')
    
    return formatted
  }
  
  const formattedContent = formatContent(content)
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[90%] ${isUser ? 'mr-2' : 'ml-2'}`}>
        <div className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : ''}`}>
          {!compact && (isUser ? (
            <div className="w-8 h-8 rounded-full bg-vs-primary flex items-center justify-center text-white text-sm font-bold">
              👤
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-vs-primary flex items-center justify-center text-white text-sm font-bold">
              🤖
            </div>
          ))}
          
          <div className={clsx(
            compact ? "rounded-xl px-3 py-2 text-sm" : "rounded-2xl px-4 py-3",
            isUser ? (compact ? 'rounded-br-sm bg-vs-primary text-white' : 'rounded-br-none bg-vs-primary text-white') : (compact ? 'rounded-bl-sm bg-vs-card' : 'rounded-bl-none bg-vs-card')
          )}>
            <div 
              className={clsx("whitespace-pre-wrap break-words chat-message-content overflow-hidden", 
                isUser ? "text-white" : "text-vs-text"
              )}
              dangerouslySetInnerHTML={{ __html: formattedContent }}
            />
            {!compact && (
              <div className={clsx("text-xs mt-1", 
                isUser ? 'text-white/70' : 'text-vs-muted'
              )}>
                {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}