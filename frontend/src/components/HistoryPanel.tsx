import type { QRCodeResponse } from "../types";

interface HistoryPanelProps {
  history: QRCodeResponse[];
  isLoading: boolean;
  onDelete: (id: string) => void;
}

export function HistoryPanel({ history, isLoading, onDelete }: HistoryPanelProps) {
  if (isLoading) {
    return <div className="history-panel"><p>Loading history...</p></div>;
  }

  if (history.length === 0) {
    return <div className="history-panel"><p>No QR codes generated yet.</p></div>;
  }

  return (
    <div className="history-panel">
      <h2>History</h2>
      <ul className="history-panel__list">
        {history.map((qr) => (
          <li key={qr.id} className="history-panel__item">
            <img src={qr.image_url} alt={`QR for ${qr.url}`} width={64} height={64} />
            <div className="history-panel__info">
              <a href={qr.url} target="_blank" rel="noopener noreferrer">
                {qr.url}
              </a>
              <span className="history-panel__meta">
                {qr.format.toUpperCase()} &middot;{" "}
                {new Date(qr.created_at).toLocaleDateString()}
              </span>
            </div>
            <button
              className="history-panel__delete"
              onClick={() => onDelete(qr.id)}
              title="Delete"
            >
              &times;
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
