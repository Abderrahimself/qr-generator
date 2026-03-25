import { useState } from "react";

interface URLInputProps {
  onSubmit: (url: string, format?: string) => void;
  isLoading: boolean;
}

export function URLInput({ onSubmit, isLoading }: URLInputProps) {
  const [url, setUrl] = useState("");
  const [format, setFormat] = useState("png");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    onSubmit(url.trim(), format);
  };

  return (
    <form onSubmit={handleSubmit} className="url-input">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter a URL (e.g. https://example.com)"
        required
        disabled={isLoading}
      />
      <select value={format} onChange={(e) => setFormat(e.target.value)} disabled={isLoading}>
        <option value="png">PNG</option>
        <option value="svg">SVG</option>
      </select>
      <button type="submit" disabled={isLoading || !url.trim()}>
        {isLoading ? "Generating..." : "Generate"}
      </button>
    </form>
  );
}
