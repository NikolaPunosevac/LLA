import { useState, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

interface Props {
  slides: string[];
  onReset: () => void;
}

export default function Slideshow({ slides, onReset }: Props) {
  const [current, setCurrent] = useState(0);

  const prev = useCallback(
    () => setCurrent((c) => Math.max(0, c - 1)),
    []
  );
  const next = useCallback(
    () => setCurrent((c) => Math.min(slides.length - 1, c + 1)),
    [slides.length]
  );

  // Keyboard navigation
  const handleKey = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowLeft") prev();
      else if (e.key === "ArrowRight") next();
    },
    [prev, next]
  );

  if (slides.length === 0) return null;

  return (
    <div
      className="flex flex-col h-full min-h-[80vh]"
      tabIndex={0}
      onKeyDown={handleKey}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b bg-white">
        <button
          onClick={onReset}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          Nov dokument
        </button>
        <span className="text-sm text-gray-500 font-medium">
          {current + 1} / {slides.length}
        </span>
      </div>

      {/* Slide content */}
      <div className="flex-1 overflow-auto px-6 py-8 md:px-16 lg:px-24">
        <div className="max-w-3xl mx-auto prose prose-gray prose-sm md:prose-base">
          <ReactMarkdown>{slides[current]}</ReactMarkdown>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between px-6 py-4 border-t bg-white">
        <button
          onClick={prev}
          disabled={current === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            bg-gray-100 text-gray-700 hover:bg-gray-200
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Nazaj
        </button>

        {/* Progress dots */}
        <div className="hidden md:flex items-center gap-1.5">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className={`w-2 h-2 rounded-full transition-colors ${
                i === current ? "bg-blue-500" : "bg-gray-300 hover:bg-gray-400"
              }`}
            />
          ))}
        </div>

        <button
          onClick={next}
          disabled={current === slides.length - 1}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            bg-blue-500 text-white hover:bg-blue-600
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-colors"
        >
          Naprej
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
