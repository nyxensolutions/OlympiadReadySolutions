import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

interface MarkdownMathProps {
  content: string;
  className?: string;
}

export function MarkdownMath({ content, className = "" }: MarkdownMathProps) {
  // Auto-wrap bare image URLs in markdown syntax if they aren't already wrapped.
  // Handles: Cloudinary, Cloudflare R2 (pub-*.r2.dev), or any URL ending in a known image extension.
  // e.g. https://pub-xxx.r2.dev/questions/abc.jpg -> ![image](https://pub-xxx.r2.dev/questions/abc.jpg)
  const processedContent = content.replace(
    /(?<!\]\()(https?:\/\/(?:res\.cloudinary\.com\/[^\s)]+|pub-[a-z0-9]+\.r2\.dev\/[^\s)]+|\S+\.(?:png|jpg|jpeg|gif|webp|svg|bmp)(?:\?\S*)?))/gi,
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
