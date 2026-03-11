import { htmlToMarkdown } from "./htmlToMarkdown";

/**
 * Parse an edit command in the format [start-end]['replacement text']
 * Example: [60-70]['new text'] or [1-5]['hello world']
 */
export function parseEditCommand(command: string): { start: number; end: number; text: string } | null {
  // Match pattern: [start-end]['text']
  const match = command.match(/\[(\d+)-(\d+)\]\[['"](.*?)['"]\]/);
  if (!match) {
    return null;
  }
  
  const start = parseInt(match[1], 10);
  const end = parseInt(match[2], 10);
  const text = match[3];
  
  if (isNaN(start) || isNaN(end) || start < 1 || end < start) {
    return null;
  }
  
  return { start, end, text };
}

/**
 * Convert HTML to markdown, split into lines, apply edit, convert back to HTML
 */
export function applyEditCommand(htmlContent: string, command: string): string {
  const edit = parseEditCommand(command);
  if (!edit) {
    return htmlContent; // Invalid command, return unchanged
  }
  
  // Convert HTML to markdown
  const markdown = htmlToMarkdown(htmlContent);
  
  // Split into lines (1-indexed for user convenience)
  const lines = markdown.split('\n');
  
  // Validate line numbers
  if (edit.start > lines.length || edit.end > lines.length) {
    console.warn(`Edit command references lines ${edit.start}-${edit.end} but document has only ${lines.length} lines`);
    return htmlContent;
  }
  
  // Apply the edit (convert to 0-indexed)
  const startIdx = edit.start - 1;
  const endIdx = edit.end - 1;
  
  // Split replacement text into lines if it contains newlines
  const replacementLines = edit.text.split('\n');
  
  // Replace the specified lines with the new text (split into lines)
  const newLines = [
    ...lines.slice(0, startIdx),
    ...replacementLines,
    ...lines.slice(endIdx + 1)
  ];
  
  // Join back and convert markdown to HTML
  const newMarkdown = newLines.join('\n');
  
  // Convert markdown back to HTML
  // For now, we'll use a simple approach: create a temporary element
  // In a production app, you might want to use a proper markdown-to-HTML library
  return markdownToHtml(newMarkdown);
}

/**
 * Simple markdown to HTML converter
 * Converts markdown back to HTML, preserving structure
 */
function markdownToHtml(markdown: string): string {
  if (!markdown.trim()) {
    return '';
  }
  
  const lines = markdown.split('\n');
  const htmlLines: string[] = [];
  let inList = false;
  let listType: 'ul' | 'ol' | null = null;
  let listItems: string[] = [];
  
  function closeList() {
    if (listItems.length > 0 && listType) {
      const tag = listType === 'ul' ? 'ul' : 'ol';
      htmlLines.push(`<${tag}>${listItems.join('')}</${tag}>`);
      listItems = [];
      listType = null;
      inList = false;
    }
  }
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    
    if (!trimmed) {
      closeList();
      continue;
    }
    
    // Headers
    if (trimmed.startsWith('###### ')) {
      closeList();
      htmlLines.push(`<h6>${trimmed.substring(7)}</h6>`);
      continue;
    }
    if (trimmed.startsWith('##### ')) {
      closeList();
      htmlLines.push(`<h5>${trimmed.substring(6)}</h5>`);
      continue;
    }
    if (trimmed.startsWith('#### ')) {
      closeList();
      htmlLines.push(`<h4>${trimmed.substring(5)}</h4>`);
      continue;
    }
    if (trimmed.startsWith('### ')) {
      closeList();
      htmlLines.push(`<h3>${trimmed.substring(4)}</h3>`);
      continue;
    }
    if (trimmed.startsWith('## ')) {
      closeList();
      htmlLines.push(`<h2>${trimmed.substring(3)}</h2>`);
      continue;
    }
    if (trimmed.startsWith('# ')) {
      closeList();
      htmlLines.push(`<h1>${trimmed.substring(2)}</h1>`);
      continue;
    }
    
    // Horizontal rule
    if (trimmed === '---') {
      closeList();
      htmlLines.push('<hr>');
      continue;
    }
    
    // Blockquote
    if (trimmed.startsWith('> ')) {
      closeList();
      htmlLines.push(`<blockquote>${processInlineMarkdown(trimmed.substring(2))}</blockquote>`);
      continue;
    }
    
    // Ordered list
    const olMatch = trimmed.match(/^(\d+)\. (.+)$/);
    if (olMatch) {
      if (!inList || listType !== 'ol') {
        closeList();
        listType = 'ol';
        inList = true;
      }
      listItems.push(`<li>${processInlineMarkdown(olMatch[2])}</li>`);
      continue;
    }
    
    // Unordered list
    if (trimmed.startsWith('- ')) {
      if (!inList || listType !== 'ul') {
        closeList();
        listType = 'ul';
        inList = true;
      }
      listItems.push(`<li>${processInlineMarkdown(trimmed.substring(2))}</li>`);
      continue;
    }
    
    // Regular paragraph
    closeList();
    htmlLines.push(`<p>${processInlineMarkdown(trimmed)}</p>`);
  }
  
  closeList();
  
  return htmlLines.join('\n');
}

/**
 * Process inline markdown (bold, italic, code, links, etc.)
 */
function processInlineMarkdown(text: string): string {
  // Code blocks (must be processed before inline code)
  text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  
  // Inline code
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Bold
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Italic
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Links
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  
  // Images
  text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />');
  
  return text;
}
