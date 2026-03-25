import { useQRGenerator } from "./hooks/useQRGenerator";
import { URLInput } from "./components/URLInput";
import { QRDisplay } from "./components/QRDisplay";
import { HistoryPanel } from "./components/HistoryPanel";

export default function App() {
  const {
    currentQR,
    history,
    isGenerating,
    isLoadingHistory,
    error,
    generate,
    remove,
  } = useQRGenerator();

  return (
    <div className="app">
      <header className="app__header">
        <h1>QR Generator</h1>
      </header>

      <main className="app__main">
        <section className="app__generator">
          <URLInput onSubmit={generate} isLoading={isGenerating} />
          {error && <p className="app__error">{error}</p>}
          <QRDisplay qrCode={currentQR} />
        </section>

        <aside className="app__sidebar">
          <HistoryPanel
            history={history}
            isLoading={isLoadingHistory}
            onDelete={remove}
          />
        </aside>
      </main>
    </div>
  );
}
