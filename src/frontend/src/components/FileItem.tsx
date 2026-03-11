import { FileText } from "lucide-react";

interface FileItemProps {
  name: string;
  lastModified: number;
  isActive: boolean;
  onClick: () => void;
}

const FileItem = ({ name, lastModified, isActive, onClick }: FileItemProps) => {
  const date = new Date(lastModified);
  const formatted = date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors duration-150 ${
        isActive
          ? "bg-accent text-accent-foreground"
          : "hover:bg-muted text-foreground"
      }`}
    >
      <FileText className="h-4 w-4 shrink-0 text-primary" />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium truncate">{name}</p>
        <p className="text-xs text-muted-foreground">{formatted}</p>
      </div>
    </button>
  );
};

export default FileItem;
