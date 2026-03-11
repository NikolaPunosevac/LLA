import { useEffect, useState, useCallback } from "react";
import { wsService, type ConnectionStatus, type WSMessage } from "@/services/websocket";

export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionStatus>(wsService.status);

  useEffect(() => {
    wsService.connect();
    const unsub = wsService.onStatus(setStatus);
    return () => {
      unsub();
    };
  }, []);

  const sendMessage = useCallback((message: string) => {
    wsService.send({ type: "chat", message });
  }, []);

  const onMessage = useCallback((handler: (msg: WSMessage) => void) => {
    return wsService.onMessage(handler);
  }, []);

  return { status, sendMessage, onMessage };
}
