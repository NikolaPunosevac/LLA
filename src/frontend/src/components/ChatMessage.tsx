interface ChatMessageProps {
  role: "user" | "ai";
  content: string;
}

const ChatMessage = ({ role, content }: ChatMessageProps) => {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] px-4 py-2.5 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-chat-user text-primary-foreground rounded-br-sm"
            : "bg-chat-ai border border-chat-ai-border text-foreground rounded-bl-sm"
        }`}
      >
        {content}
      </div>
    </div>
  );
};

export default ChatMessage;
