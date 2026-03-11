import { useEffect, useState, useCallback, useRef } from "react";
import { wsService, type ConnectionStatus, type WSMessage } from "../services/websocket";

export type AppPhase = "upload" | "processing" | "slideshow";

export function useDocuWise() {
  const [status, setStatus] = useState<ConnectionStatus>(wsService.status);
  const [phase, setPhase] = useState<AppPhase>("upload");
  const [statusText, setStatusText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [slides, setSlides] = useState<string[]>([]);
  const handlerRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    wsService.connect();
    const unsubStatus = wsService.onStatus(setStatus);

    handlerRef.current = wsService.onMessage((msg: WSMessage) => {
      switch (msg.type) {
        case "status":
          setStatusText(msg.message);
          break;
        case "tutorial_slides":
          setSlides(msg.slides ?? []);
          setPhase("slideshow");
          setStatusText("");
          break;
        case "process_error":
          setError(msg.message);
          setPhase("upload");
          setStatusText("");
          break;
      }
    });

    return () => {
      unsubStatus();
      handlerRef.current?.();
    };
  }, []);

  const processDocx = useCallback((text: string) => {
    setError(null);
    setPhase("processing");
    setStatusText("Pošiljam dokument ...");
    wsService.send({ type: "process_docx", message: text });
  }, []);

  const reset = useCallback(() => {
    setPhase("upload");
    setSlides([]);
    setError(null);
    setStatusText("");
  }, []);

  return { status, phase, statusText, error, slides, processDocx, reset };
}
