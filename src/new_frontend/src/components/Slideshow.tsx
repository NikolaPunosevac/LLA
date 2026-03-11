import { useState, useCallback, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

interface Props {
  slides: string[];
  onReset: () => void;
}

export default function Slideshow({ slides, onReset }: Props) {
  const [current, setCurrent] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const prev = useCallback(
    () => setCurrent((c) => Math.max(0, c - 1)),
    []
  );
  const next = useCallback(
    () => setCurrent((c) => Math.min(slides.length - 1, c + 1)),
    [slides.length]
  );

  // Scroll content to top on slide change
  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  }, [current]);

  // Global keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") prev();
      else if (e.key === "ArrowRight") next();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [prev, next]);

  if (slides.length === 0) return null;

  const progress = ((current + 1) / slides.length) * 100;

  return (
    <div ref={containerRef} className="flex flex-col h-full">
      {/* Toolbar with integrated progress bar */}
      <div className="flex-none bg-cyan-600">
        <div className="flex items-center justify-between px-6 py-2.5">
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 text-xs text-cyan-200 hover:text-white transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Nov dokument
          </button>
          <span className="text-xs tabular-nums text-cyan-200">
            {current + 1} / {slides.length}
          </span>
        </div>
        <div className="h-1 bg-cyan-700/50">
          <div
            className="h-full bg-cyan-300 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Scrollable slide content */}
      <div
        ref={contentRef}
        className="flex-1 min-h-0 overflow-y-auto px-6 py-8 md:px-10 lg:px-14"
      >
        <div className="max-w-5xl mx-auto prose">
          <ReactMarkdown>{slides[current]}</ReactMarkdown>
        </div>
      </div>

      {/* Fixed bottom navigation */}
      <div className="flex-none flex items-center justify-between px-6 py-3 bg-cyan-600">
        <button
          onClick={prev}
          disabled={current === 0}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
            border border-cyan-400/40 text-white hover:bg-cyan-500 active:bg-cyan-700
            disabled:opacity-25 disabled:pointer-events-none
            transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Nazaj
        </button>

        {/* Progress dots */}
        <div className="hidden md:flex items-center gap-1 max-w-[40%] flex-wrap justify-center">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className={`rounded-full transition-all duration-200 ${
                i === current
                  ? "w-5 h-2 bg-white"
                  : "w-2 h-2 bg-cyan-400/50 hover:bg-cyan-300"
              }`}
            />
          ))}
        </div>

        <button
          onClick={next}
          disabled={current === slides.length - 1}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium
            bg-white text-cyan-700 hover:bg-cyan-50 active:bg-cyan-100
            disabled:opacity-25 disabled:pointer-events-none
            transition-colors shadow-sm"
        >
          Naprej
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
