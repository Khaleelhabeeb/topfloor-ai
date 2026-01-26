import { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send } from 'lucide-react';
import { useGameState } from '@/hooks/useGameState';

interface ChatMessage {
  sender: string;
  text: string;
  time: string;
  isUser?: boolean;
}

export function ChatPanel() {
  const [inputValue, setInputValue] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const { currentEmployee, chatMessages, addChatMessage } = useGameState();

  const messages = currentEmployee ? chatMessages[currentEmployee.id] || [] : [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim() || !currentEmployee) return;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });

    addChatMessage(currentEmployee.id, {
      sender: 'You',
      text: inputValue,
      time: timeString,
      isUser: true,
    });

    setInputValue('');

    // Simulate a response after a short delay
    setTimeout(() => {
      const responses = [
        "That's a great point!",
        "I'll look into that.",
        "Thanks for sharing!",
        "Let me check and get back to you.",
        "Sounds good to me!",
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      addChatMessage(currentEmployee.id, {
        sender: currentEmployee.name.split(' ')[0],
        text: randomResponse,
        time: new Date().toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        }),
      });
    }, 1000 + Math.random() * 1000);
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
                    : 'bg-muted text-foreground'
                }`}
              >
                <p className="text-sm">{message.text}</p>
              </div>
              <span className="text-[10px] text-muted-foreground mt-1 px-1">
                {message.sender} • {message.time}
              </span>
            </div>
          ))}
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
          />
          <Button size="icon" onClick={handleSend} disabled={!inputValue.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
