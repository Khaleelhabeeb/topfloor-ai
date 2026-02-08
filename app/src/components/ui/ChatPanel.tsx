import { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Loader2 } from 'lucide-react';
import { useGameState } from '@/hooks/useGameState';
import { agentsApi } from '@/lib/agents';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessage {
  sender: string;
  text: string;
  time: string;
  isUser?: boolean;
}

export function ChatPanel() {
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { currentEmployee, chatMessages, addChatMessage } = useGameState();

  const messages = currentEmployee ? chatMessages[currentEmployee.id] || [] : [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || !currentEmployee || isSending) return;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });

    // Add user message
    addChatMessage(currentEmployee.id, {
      sender: 'You',
      text: inputValue,
      time: timeString,
      isUser: true,
    });

    const userMessage = inputValue;
    setInputValue('');
    setIsSending(true);

    try {
      // Call the actual API
      console.log(`Sending message to ${currentEmployee.agentType}:`, userMessage);
      const response = await agentsApi.chatWithAgent(currentEmployee.agentType, {
        message: userMessage,
      });

      // Add agent response
      const responseTime = new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });

      addChatMessage(currentEmployee.id, {
        sender: currentEmployee.name,
        text: response.response,
        time: responseTime,
      });

      console.log('Agent response received:', response);
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message. Please try again.');
      
      // Add error message
      addChatMessage(currentEmployee.id, {
        sender: 'System',
        text: 'Sorry, I\'m having trouble connecting right now. Please try again.',
        time: new Date().toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        }),
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-card border-l border-border">
      {/* Chat header */}
      <div className="p-3 border-b border-border bg-muted/50">
        <h3 className="font-semibold text-sm text-foreground">Chat</h3>
        <p className="text-xs text-muted-foreground">
          {currentEmployee?.name}
        </p>
      </div>

      {/* Messages area */}
      <ScrollArea className="flex-1 p-3" ref={scrollRef}>
        <div className="space-y-3">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex flex-col ${message.isUser ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 ${
                  message.isUser
                    ? 'bg-primary text-primary-foreground'
                    : message.sender === 'System'
                    ? 'bg-destructive/10 text-destructive border border-destructive/20'
                    : 'bg-muted text-foreground'
                }`}
              >
                {message.isUser || message.sender === 'System' ? (
                  <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                ) : (
                  <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:text-sm prose-headings:my-2 prose-headings:text-sm prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-li:text-sm prose-code:text-xs prose-pre:my-2 prose-pre:text-xs prose-table:text-xs prose-strong:font-semibold">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.text}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
              <span className="text-[10px] text-muted-foreground mt-1 px-1">
                {message.sender} • {message.time}
              </span>
            </div>
          ))}
          {isSending && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-3 w-3 animate-spin" />
              <span>{currentEmployee?.name} is typing...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input area */}
      <div className="p-3 border-t border-border">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 text-sm"
            disabled={isSending}
          />
          <Button 
            size="icon" 
            onClick={handleSend} 
            disabled={!inputValue.trim() || isSending}
          >
            {isSending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
