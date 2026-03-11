/**
 * Converts HTML content to Markdown format
 * Handles common HTML elements: headings, paragraphs, bold, italic, lists, etc.
 */
export function htmlToMarkdown(html: string): string {
  // Create a temporary DOM element to parse HTML
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  
  function processNode(node: Node): string {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.textContent || '';
    }
    
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return '';
    }
    
    const element = node as HTMLElement;
    const tagName = element.tagName.toLowerCase();
    const children = Array.from(node.childNodes)
      .map(processNode)
      .join('');
    
    switch (tagName) {
      case 'h1':
        return `# ${children.trim()}\n\n`;
      case 'h2':
        return `## ${children.trim()}\n\n`;
      case 'h3':
        return `### ${children.trim()}\n\n`;
      case 'h4':
        return `#### ${children.trim()}\n\n`;
      case 'h5':
        return `##### ${children.trim()}\n\n`;
      case 'h6':
        return `###### ${children.trim()}\n\n`;
      case 'p':
        return `${children.trim()}\n\n`;
      case 'strong':
      case 'b':
        return `**${children.trim()}**`;
      case 'em':
      case 'i':
        return `*${children.trim()}*`;
      case 'u':
        return `<u>${children.trim()}</u>`;
      case 'ul':
        return `${children}\n`;
      case 'ol':
        return `${children}\n`;
      case 'li':
        const parent = element.parentElement;
        if (parent?.tagName.toLowerCase() === 'ol') {
          const index = Array.from(parent.children).indexOf(element) + 1;
          return `${index}. ${children.trim()}\n`;
        } else {
          return `- ${children.trim()}\n`;
        }
      case 'br':
        return '\n';
      case 'hr':
        return '---\n\n';
      case 'blockquote':
        return `> ${children.trim()}\n\n`;
      case 'code':
        return `\`${children.trim()}\``;
      case 'pre':
        return `\`\`\`\n${children.trim()}\n\`\`\`\n\n`;
      case 'a':
        const href = element.getAttribute('href') || '';
        return `[${children.trim()}](${href})`;
      case 'img':
        const src = element.getAttribute('src') || '';
        const alt = element.getAttribute('alt') || '';
        return `![${alt}](${src})`;
      case 'div':
        return `${children}\n`;
      case 'span':
        return children;
      default:
        return children;
    }
  }
  
  const markdown = Array.from(tempDiv.childNodes)
    .map(processNode)
    .join('');
  
  // Clean up extra newlines
  return markdown
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}
