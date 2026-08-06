import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { protectCurrency } from "@/lib/notation";

interface MarkdownMathProps {
  content: string;
  className?: string;
  /** Skip the default dark text colour and inherit from the parent instead
   *  (used by the admin panel, which renders on a dark background). */
  inheritColor?: boolean;
}

export function MarkdownMath({ content, className = "", inheritColor = false }: MarkdownMathProps) {
  // Auto-wrap bare image URLs in markdown syntax if they aren't already wrapped.
  // Handles: Cloudinary, Cloudflare R2 (pub-*.r2.dev), or any URL ending in a known image extension.
  // e.g. https://pub-xxx.r2.dev/questions/abc.jpg -> ![image](https://pub-xxx.r2.dev/questions/abc.jpg)
  const withImages = content.replace(
    /(?<!\]\()(https?:\/\/(?:res\.cloudinary\.com\/[^\s)]+|pub-[a-z0-9]+\.r2\.dev\/[^\s)]+|\S+\.(?:png|jpg|jpeg|gif|webp|svg|bmp)(?:\?\S*)?))/gi,
    "![image]($1)"
  );

  // Money is not maths. Without this, "invest $1400, $1600 and $2200 respectively"
  // pairs its dollar signs into a formula and KaTeX strips every space inside it,
  // rendering "invest 1400,1600and2200respectively". Genuine LaTeX is untouched.
  const processedContent = protectCurrency(withImages);

  return (
    <div className={`${inheritColor ? "" : "text-slate-900"} leading-relaxed ${className}`}>
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
