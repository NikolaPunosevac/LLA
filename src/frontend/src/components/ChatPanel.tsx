import { useState, useEffect, useRef, useCallback } from "react";
import { Trash2 } from "lucide-react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import type { WSMessage } from "@/services/websocket";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
}

interface ChatPanelProps {
  sendMessage: (msg: string) => void;
  onMessage: (handler: (msg: WSMessage) => void) => () => void;
}

const ChatPanel = ({ sendMessage, onMessage }: ChatPanelProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    const unsub = onMessage((msg) => {
      if (msg.type === "response") {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "ai", content: msg.message },
        ]);
      }
    });
    return unsub;
  }, [onMessage]);

  const handleSend = useCallback(
    (text: string) => {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", content: text },
      ]);
      setIsTyping(true);
      sendMessage(text);
    },
    [sendMessage]
  );

  const clearChat = () => {
    setMessages([]);
    setIsTyping(false);
  };

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <h2 className="text-sm font-semibold text-foreground">AI Assistant</h2>
        <button
          onClick={clearChat}
          className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors duration-150"
          title="Clear chat"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-muted-foreground text-center">
              Start a conversation with the AI assistant
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-chat-ai border border-chat-ai-border rounded-xl rounded-bl-sm px-4 py-3 flex gap-1">
              <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} />
    </div>
  );
};

export default ChatPanel;
