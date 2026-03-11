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
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div className="max-w-lg w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-900">
          DocuWise Tutorial Generator
        </h1>
        <p className="text-center text-gray-500 mb-8">
          Naloži Word predlogo z Jinja tagi in prejmi navodila za konfiguracijo
          intervjuja po korakih.
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
            transition-colors duration-200
            ${
              dragOver
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
            }
            ${disabled ? "opacity-50 pointer-events-none" : ""}
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
            <div className="flex flex-col items-center gap-3">
              <FileText className="w-12 h-12 text-blue-500" />
              <p className="text-gray-700 font-medium">{fileName}</p>
              <p className="text-sm text-gray-400">Klikni za zamenjavo</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className="w-12 h-12 text-gray-400" />
              <p className="text-gray-600 font-medium">
                Povleci .docx sem ali klikni za izbiro
              </p>
              <p className="text-sm text-gray-400">
                Podprte so samo .docx datoteke
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700 whitespace-pre-wrap">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
