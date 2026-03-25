import type { QRCodeResponse } from "../types";

interface QRDisplayProps {
  qrCode: QRCodeResponse | null;
}

export function QRDisplay({ qrCode }: QRDisplayProps) {
  if (!qrCode) {
    return (
      <div className="qr-display qr-display--empty">
        <p>Enter a URL above to generate a QR code</p>
      </div>
    );
  }

  return (
    <div className="qr-display">
      <img src={qrCode.image_url} alt={`QR code for ${qrCode.url}`} />
      <p className="qr-display__url">{qrCode.url}</p>
      <a
        href={qrCode.image_url}
        download={`qr-${qrCode.id}.${qrCode.format}`}
        className="qr-display__download"
      >
        Download {qrCode.format.toUpperCase()}
      </a>
    </div>
  );
}
