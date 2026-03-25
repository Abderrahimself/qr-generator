export interface QRCodeRequest {
  url: string;
  format?: string;
}

export interface QRCodeResponse {
  id: string;
  url: string;
  image_url: string;
  format: string;
  created_at: string;
}
