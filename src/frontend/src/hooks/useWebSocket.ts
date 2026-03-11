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

  const sendGenerateTutorial = useCallback((interviewJson: string) => {
    wsService.send({ type: "generate_tutorial", message: interviewJson });
  }, []);

  const onMessage = useCallback((handler: (msg: WSMessage) => void) => {
    return wsService.onMessage(handler);
  }, []);

  return { status, sendMessage, sendGenerateTutorial, onMessage };
}
