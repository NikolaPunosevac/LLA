import { type ConnectionStatus } from "@/services/websocket";
import { FileText } from "lucide-react";

interface HeaderProps {
  connectionStatus: ConnectionStatus;
}

const statusConfig: Record<ConnectionStatus, { label: string; className: string }> = {
  connected: { label: "Connected", className: "bg-status-connected" },
  connecting: { label: "Connecting", className: "bg-status-connecting animate-pulse" },
  disconnected: { label: "Disconnected", className: "bg-status-disconnected" },
};

const Header = ({ connectionStatus }: HeaderProps) => {
  const { label, className } = statusConfig[connectionStatus];

  return (
    <header className="sticky top-0 z-50 h-[60px] border-b bg-card flex items-center justify-between px-6 shadow-sm">
      <div className="flex items-center gap-2.5">
        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
          <FileText className="h-4 w-4 text-primary-foreground" />
        </div>
        <h1 className="text-lg font-semibold text-foreground tracking-tight">
          AI Document Assistant
        </h1>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <span className={`h-2.5 w-2.5 rounded-full ${className}`} />
        <span className="text-muted-foreground font-medium">{label}</span>
      </div>
    </header>
  );
};

export default Header;
