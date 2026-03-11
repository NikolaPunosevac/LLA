import { Upload, Save, Download } from "lucide-react";

interface DocumentToolbarProps {
  onUpload: () => void;
  onSave: () => void;
  onExport: () => void;
  hasDocument: boolean;
}

const DocumentToolbar = ({ onUpload, onSave, onExport, hasDocument }: DocumentToolbarProps) => {
  return (
    <div className="flex items-center gap-2 px-4 py-2.5 border-b bg-panel-header">
      <button
        onClick={onUpload}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary-hover transition-colors duration-150"
      >
        <Upload className="h-3.5 w-3.5" />
        Upload DOCX
      </button>
      <button
        onClick={onSave}
        disabled={!hasDocument}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md border text-foreground hover:bg-muted transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Save className="h-3.5 w-3.5" />
        Save
      </button>
      <button
        onClick={onExport}
        disabled={!hasDocument}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md border text-foreground hover:bg-muted transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Download className="h-3.5 w-3.5" />
        Export DOCX
      </button>
    </div>
  );
};

export default DocumentToolbar;
