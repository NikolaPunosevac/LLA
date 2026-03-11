import { useDocuWise } from "./hooks/useDocuWise";
import UploadStep from "./components/UploadStep";
import Processing from "./components/Processing";
import Slideshow from "./components/Slideshow";

export default function App() {
  const { status, phase, statusText, error, slides, processDocx, reset } =
    useDocuWise();

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-50">
      {/* Connection indicator */}
      <header className="flex-none flex items-center justify-between px-5 py-2.5 bg-cyan-600">
        <span className="text-sm font-semibold tracking-tight text-white">
          DocuWise Tutorial
        </span>
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`w-1.5 h-1.5 rounded-full ring-1 ring-white/30 ${
              status === "connected"
                ? "bg-emerald-300"
                : status === "connecting"
                ? "bg-amber-300 animate-pulse"
                : "bg-red-400"
            }`}
          />
          <span className="text-cyan-100">
            {status === "connected"
              ? "Povezan"
              : status === "connecting"
              ? "Povezujem ..."
              : "Ni povezave"}
          </span>
        </div>
      </header>

      {/* Main content — takes remaining height */}
      <main className="flex-1 min-h-0">
        {phase === "upload" && (
          <UploadStep
            onDocxText={processDocx}
            disabled={status !== "connected"}
            error={error}
          />
        )}
        {phase === "processing" && <Processing statusText={statusText} />}
        {phase === "slideshow" && (
          <Slideshow slides={slides} onReset={reset} />
        )}
      </main>
    </div>
  );
}
