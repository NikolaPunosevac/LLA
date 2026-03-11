import { useState, useCallback } from "react";
import mammoth from "mammoth";
import DOMPurify from "dompurify";
import Header from "@/components/Header";
import FileBrowser, { type DocFile } from "@/components/FileBrowser";
import ChatPanel from "@/components/ChatPanel";
import DocumentEditor from "@/components/DocumentEditor";
import { useWebSocket } from "@/hooks/useWebSocket";

const Home = () => {
  const { status, sendMessage, sendGenerateTutorial, onMessage } = useWebSocket();
  const [files, setFiles] = useState<DocFile[]>([]);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [docContent, setDocContent] = useState("");

  const handleOpenFolder = useCallback(async () => {
    try {
      if ("showDirectoryPicker" in window) {
        const dirHandle = await (window as any).showDirectoryPicker();
        const docFiles: DocFile[] = [];
        for await (const entry of dirHandle.values()) {
          if (entry.kind === "file" && entry.name.endsWith(".docx")) {
            const file = await entry.getFile();
            docFiles.push({
              name: entry.name,
              lastModified: file.lastModified,
              handle: entry,
            });
          }
        }
        docFiles.sort((a, b) => b.lastModified - a.lastModified);
        setFiles(docFiles);
      } else {
        // Fallback: use file input
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".docx";
        input.multiple = true;
        input.webkitdirectory = true;
        input.onchange = () => {
          if (input.files) {
            const docFiles: DocFile[] = [];
            for (const file of Array.from(input.files)) {
              if (file.name.endsWith(".docx")) {
                docFiles.push({
                  name: file.name,
                  lastModified: file.lastModified,
                  handle: file as any,
                });
              }
            }
            docFiles.sort((a, b) => b.lastModified - a.lastModified);
            setFiles(docFiles);
          }
        };
        input.click();
      }
    } catch {
      // User cancelled
    }
  }, []);

  const handleSelectFile = useCallback(async (docFile: DocFile) => {
    setActiveFile(docFile.name);
    try {
      const file = await docFile.handle.getFile();
      const buffer = await file.arrayBuffer();
      const result = await mammoth.convertToHtml({ arrayBuffer: buffer });
      setDocContent(DOMPurify.sanitize(result.value));
    } catch {
      setDocContent("<p>Failed to load document.</p>");
    }
  }, []);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header connectionStatus={status} />
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* File Browser - 20% */}
        <div className="lg:w-[20%] w-full h-[250px] lg:h-auto border-b lg:border-b-0 lg:border-r overflow-hidden">
          <FileBrowser
            files={files}
            activeFile={activeFile}
            onOpenFolder={handleOpenFolder}
            onSelectFile={handleSelectFile}
          />
        </div>
        {/* Chat Panel - 30% */}
        <div className="lg:w-[30%] w-full h-[350px] lg:h-auto border-b lg:border-b-0 lg:border-r overflow-hidden">
          <ChatPanel sendMessage={sendMessage} sendGenerateTutorial={sendGenerateTutorial} onMessage={onMessage} />
        </div>
        {/* Document Editor - 50% */}
        <div className="lg:w-[50%] w-full flex-1 lg:flex-none lg:h-auto overflow-hidden">
          <DocumentEditor content={docContent} onContentChange={setDocContent} />
        </div>
      </div>
    </div>
  );
};

export default Home;
