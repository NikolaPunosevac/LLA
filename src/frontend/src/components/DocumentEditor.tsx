import { useRef, useCallback } from "react";
import DOMPurify from "dompurify";
import mammoth from "mammoth";
import { saveAs } from "file-saver";
import DocumentToolbar from "./DocumentToolbar";

interface DocumentEditorProps {
  content: string;
  onContentChange: (html: string) => void;
}

const DocumentEditor = ({ content, onContentChange }: DocumentEditorProps) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const hasDocument = content.length > 0;

  const loadDocx = useCallback(
    async (arrayBuffer: ArrayBuffer) => {
      const result = await mammoth.convertToHtml({ arrayBuffer });
      const clean = DOMPurify.sanitize(result.value);
      onContentChange(clean);
    },
    [onContentChange]
  );

  const handleUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const buffer = await file.arrayBuffer();
    await loadDocx(buffer);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSave = () => {
    const html = editorRef.current?.innerHTML || "";
    onContentChange(html);
    // For now just update state; could persist later
  };

  const handleExport = async () => {
    const html = editorRef.current?.innerHTML || "";
    // Simple HTML-to-DOCX export using Blob
    const docContent = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset='utf-8'><title>Document</title></head>
      <body>${html}</body></html>`;
    const blob = new Blob([docContent], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    saveAs(blob, "document.docx");
  };

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full bg-card">
      <DocumentToolbar
        onUpload={handleUpload}
        onSave={handleSave}
        onExport={handleExport}
        hasDocument={hasDocument}
      />
      <input
        ref={fileInputRef}
        type="file"
        accept=".docx"
        onChange={handleFileChange}
        className="hidden"
      />
      {/* Formatting toolbar */}
      <div className="flex items-center gap-1 px-4 py-1.5 border-b bg-panel-header flex-wrap">
        <ToolbarButton label="B" onClick={() => execCommand("bold")} bold />
        <ToolbarButton label="I" onClick={() => execCommand("italic")} italic />
        <ToolbarButton label="U" onClick={() => execCommand("underline")} underline />
        <span className="w-px h-5 bg-border mx-1" />
        <ToolbarButton label="H1" onClick={() => execCommand("formatBlock", "h1")} />
        <ToolbarButton label="H2" onClick={() => execCommand("formatBlock", "h2")} />
        <ToolbarButton label="H3" onClick={() => execCommand("formatBlock", "h3")} />
        <span className="w-px h-5 bg-border mx-1" />
        <ToolbarButton label="UL" onClick={() => execCommand("insertUnorderedList")} />
        <ToolbarButton label="OL" onClick={() => execCommand("insertOrderedList")} />
        <span className="w-px h-5 bg-border mx-1" />
        <ToolbarButton label="↩" onClick={() => execCommand("undo")} />
        <ToolbarButton label="↪" onClick={() => execCommand("redo")} />
      </div>
      <div
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning
        className="flex-1 overflow-y-auto scrollbar-thin p-6 prose prose-sm max-w-none focus:outline-none text-foreground"
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}
        onInput={() => {
          if (editorRef.current) {
            onContentChange(editorRef.current.innerHTML);
          }
        }}
      />
    </div>
  );
};

function ToolbarButton({
  label,
  onClick,
  bold,
  italic,
  underline,
}: {
  label: string;
  onClick: () => void;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
}) {
  return (
    <button
      onMouseDown={(e) => {
        e.preventDefault();
        onClick();
      }}
      className={`h-7 min-w-[28px] px-1.5 text-xs rounded hover:bg-muted text-foreground transition-colors duration-100 ${
        bold ? "font-bold" : ""
      } ${italic ? "italic" : ""} ${underline ? "underline" : ""}`}
    >
      {label}
    </button>
  );
}

export default DocumentEditor;
