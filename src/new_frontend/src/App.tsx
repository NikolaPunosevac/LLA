import { useDocuWise } from "./hooks/useDocuWise";
import UploadStep from "./components/UploadStep";
import Processing from "./components/Processing";
import Slideshow from "./components/Slideshow";

export default function App() {
  const { status, phase, statusText, error, slides, processDocx, reset } =
    useDocuWise();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Connection indicator */}
      <div className="flex items-center justify-end px-4 py-2 text-xs gap-2">
        <span
          className={`w-2 h-2 rounded-full ${
            status === "connected"
              ? "bg-green-500"
              : status === "connecting"
              ? "bg-yellow-400 animate-pulse"
              : "bg-red-500"
          }`}
        />
        <span className="text-gray-400">
          {status === "connected"
            ? "Povezan"
            : status === "connecting"
            ? "Povezujem ..."
            : "Ni povezave"}
        </span>
      </div>

      {/* Main content */}
      <div className="flex-1">
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
      </div>
    </div>
  );
}
