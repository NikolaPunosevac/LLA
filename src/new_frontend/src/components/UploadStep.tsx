import { useCallback, useState, useRef } from "react";
import mammoth from "mammoth";
import { Upload, FileText, AlertCircle } from "lucide-react";

interface Props {
  onDocxText: (text: string) => void;
  disabled: boolean;
  error: string | null;
}

export default function UploadStep({ onDocxText, disabled, error }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".docx")) {
        alert("Prosim naloži .docx datoteko.");
        return;
      }
      setFileName(file.name);
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      onDocxText(result.value);
    },
    [onDocxText]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-50 mb-4">
            <FileText className="w-7 h-7 text-cyan-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1.5">
            Tutorial Generator
          </h1>
          <p className="text-sm text-gray-500 leading-relaxed">
            Naloži Word predlogo z Jinja tagi in prejmi<br />
            navodila za konfiguracijo intervjuja po korakih.
          </p>
        </div>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`
            border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
            transition-all duration-200
            ${
              dragOver
                ? "border-cyan-400 bg-cyan-50 scale-[1.01]"
                : "border-gray-200 hover:border-cyan-300 hover:bg-gray-50/50"
            }
            ${disabled ? "opacity-40 pointer-events-none" : ""}
          `}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".docx"
            onChange={handleFileChange}
            className="hidden"
          />

          {fileName ? (
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-cyan-100 flex items-center justify-center">
                <FileText className="w-5 h-5 text-cyan-600" />
              </div>
              <p className="text-sm font-medium text-gray-700">{fileName}</p>
              <p className="text-xs text-gray-400">Klikni za zamenjavo</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
                <Upload className="w-5 h-5 text-gray-400" />
              </div>
              <p className="text-sm font-medium text-gray-600">
                Povleci .docx sem ali klikni za izbiro
              </p>
              <p className="text-xs text-gray-400">
                Podprte so samo .docx datoteke
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3.5 bg-red-50 border border-red-100 rounded-xl flex gap-2.5">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-600 leading-relaxed whitespace-pre-wrap">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
