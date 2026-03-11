import { useState } from "react";
import { FolderOpen, Search } from "lucide-react";
import FileItem from "./FileItem";

export interface DocFile {
  name: string;
  lastModified: number;
  handle: FileSystemFileHandle;
}

interface FileBrowserProps {
  files: DocFile[];
  activeFile: string | null;
  onOpenFolder: () => void;
  onSelectFile: (file: DocFile) => void;
}

const FileBrowser = ({ files, activeFile, onOpenFolder, onSelectFile }: FileBrowserProps) => {
  const [search, setSearch] = useState("");

  const filtered = files.filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="p-3 border-b">
        <button
          onClick={onOpenFolder}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary-hover transition-colors duration-150"
        >
          <FolderOpen className="h-4 w-4" />
          Open Folder
        </button>
      </div>
      <div className="px-3 py-2 border-b">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search documents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-2 text-sm rounded-lg border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin p-2 space-y-0.5">
        {filtered.length === 0 && files.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8 px-4">
            Open a folder to browse your Word documents
          </p>
        )}
        {filtered.length === 0 && files.length > 0 && (
          <p className="text-sm text-muted-foreground text-center py-8 px-4">
            No documents match your search
          </p>
        )}
        {filtered.map((file) => (
          <FileItem
            key={file.name}
            name={file.name}
            lastModified={file.lastModified}
            isActive={activeFile === file.name}
            onClick={() => onSelectFile(file)}
          />
        ))}
      </div>
    </div>
  );
};

export default FileBrowser;
