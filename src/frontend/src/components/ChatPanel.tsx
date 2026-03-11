import { useState, useEffect, useRef, useCallback } from "react";
import { flushSync } from "react-dom";
import { Trash2, FileUp } from "lucide-react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import type { WSMessage } from "@/services/websocket";
import { htmlToMarkdown } from "@/lib/htmlToMarkdown";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
}

interface ChatPanelProps {
  sendMessage: (msg: string, documentMarkdown?: string) => void;
  sendGenerateTutorial: (json: string) => void;
  onMessage: (handler: (msg: WSMessage) => void) => () => void;
  documentContent?: string;
}

const ChatPanel = ({ sendMessage, sendGenerateTutorial, onMessage, documentContent }: ChatPanelProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const streamingMessageIdRef = useRef<string | null>(null);
  const streamingContentRef = useRef<string>("");

  const scrollToBottom = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    const unsub = onMessage((msg) => {
      console.log("Received message:", msg.type, msg.message?.substring(0, 50));
      
      if (msg.type === "response_start") {
        // Create a new AI message when streaming starts
        setIsTyping(false);
        const newMessageId = crypto.randomUUID();
        streamingMessageIdRef.current = newMessageId;
        streamingContentRef.current = "";
        console.log("Starting new stream, message ID:", newMessageId);
        setMessages((prev) => [
          ...prev,
          { id: newMessageId, role: "ai", content: "" },
        ]);
      } else if (msg.type === "response_chunk") {
        // Append chunk to the current streaming message
        if (streamingMessageIdRef.current && msg.message) {
          streamingContentRef.current += msg.message;
          console.log("Chunk received, total length:", streamingContentRef.current.length, "chunk:", msg.message.substring(0, 30));
          // Use flushSync to force immediate update and prevent batching
          flushSync(() => {
            setMessages((prev) => {
              const updated = prev.map((m) =>
                m.id === streamingMessageIdRef.current
                  ? { ...m, content: streamingContentRef.current }
                  : m
              );
              console.log("Updated message content length:", updated.find(m => m.id === streamingMessageIdRef.current)?.content.length);
              return updated;
            });
          });
        } else {
          console.warn("Received chunk but no streaming message ID or empty message", {
            hasId: !!streamingMessageIdRef.current,
            hasMessage: !!msg.message
          });
        }
      } else if (msg.type === "response_end") {
        // Finalize the streaming message
        console.log("Stream ended, final content length:", streamingContentRef.current.length);
        streamingMessageIdRef.current = null;
        streamingContentRef.current = "";
      } else if (msg.type === "tutorial_error") {
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          { id: crypto.randomUUID(), role: "ai", content: `**Napaka:** ${msg.message}` },
        ]);
      } else if (msg.type === "response") {
        // Fallback for non-streaming responses (backward compatibility)
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
      
      // Convert document HTML to markdown if document content exists
      const documentMarkdown = documentContent ? htmlToMarkdown(documentContent) : undefined;
      sendMessage(text, documentMarkdown);
    },
    [sendMessage, documentContent]
  );

  const handleUploadJson = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      const text = await file.text();
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", content: `Generiraj tutorial iz **${file.name}**` },
      ]);
      setIsTyping(true);
      sendGenerateTutorial(text);
    };
    input.click();
  }, [sendGenerateTutorial]);

  const clearChat = () => {
    setMessages([]);
    setIsTyping(false);
    streamingMessageIdRef.current = null;
    streamingContentRef.current = "";
  };

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <h2 className="text-sm font-semibold text-foreground">AI Assistant</h2>
        <div className="flex items-center gap-1">
          <button
            onClick={handleUploadJson}
            className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors duration-150"
            title="Generate tutorial from JSON"
          >
            <FileUp className="h-4 w-4" />
          </button>
          <button
            onClick={clearChat}
            className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors duration-150"
            title="Clear chat"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
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
