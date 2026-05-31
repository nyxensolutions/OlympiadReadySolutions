import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

interface MarkdownMathProps {
  content: string;
  className?: string;
}

export function MarkdownMath({ content, className = "" }: MarkdownMathProps) {
  // Auto-wrap raw cloudinary URLs in markdown syntax if they aren't already wrapped
  // e.g. https://res.cloudinary.com/xyz -> ![image](https://res.cloudinary.com/xyz)
  const processedContent = content.replace(
    /(?<!\]\()(https:\/\/res\.cloudinary\.com\/[^\s\)]+)/g,
    "![image]($1)"
  );

  return (
    <div className={`text-slate-900 leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          p: ({ node, ...props }) => <span {...props} />,
          img: ({ node, ...props }) => (
            <img {...props} className="inline-block max-h-32 object-contain rounded-md shadow-sm border border-slate-200" />
          )
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}
