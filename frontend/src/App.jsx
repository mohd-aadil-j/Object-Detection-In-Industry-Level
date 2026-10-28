import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function App() {
  const [settings, setSettings] = useState({
    component_name: '',
    expected_sequence: 'yellow, blue, black, red',
    layer_distance: 0,
    color_tolerance: 20,
  });
  const [inspection, setInspection] = useState({
    component_serial_number: '',
    operator_id: '',
    operator_name: '',
    image: null,
  });
  const [processState, setProcessState] = useState('STOPPED');
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState([]);

  async function loadHistory() {
    const response = await fetch(`${API_BASE}/inspection/history/`);
    if (!response.ok) throw new Error('Unable to load inspection history.');
    setHistory(await response.json());
  }

  async function saveSettings(event) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    try {
      const response = await fetch(`${API_BASE}/settings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...settings,
          expected_sequence: settings.expected_sequence
            .split(',')
            .map((color) => color.trim())
            .filter(Boolean),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Unable to save settings.');
      setMessage(`Settings saved for ${data.expected_wire_count} wires.`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function controlProcess(action) {
    setBusy(true);
    setMessage('');
    try {
      const response = await fetch(`${API_BASE}/process/${action}/`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Process action failed.');
      setProcessState(data.state);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function submitInspection(event) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    setResult(null);
    const formData = new FormData();
    formData.append('component_serial_number', inspection.component_serial_number);
    formData.append('operator_id', inspection.operator_id);
    formData.append('operator_name', inspection.operator_name);
    formData.append('image', inspection.image);
    try {
      const response = await fetch(`${API_BASE}/inspection/process/`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Inspection failed.');
      setResult(data);
      loadHistory().catch((error) => setMessage(error.message));
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Production station</p>
          <h1>Wire Sequence Inspection</h1>
        </div>
        <span className={`state-pill state-${processState.toLowerCase()}`}>{processState}</span>
      </header>

      <section className="control-panel">
        <h2>Process control</h2>
        <div className="button-row">
          <button onClick={() => controlProcess('start')} disabled={busy}>Start</button>
          <button onClick={() => controlProcess('pause')} disabled={busy || processState !== 'RUNNING'}>Pause</button>
          <button onClick={() => controlProcess('resume')} disabled={busy || processState !== 'PAUSED'}>Resume</button>
          <button className="button-danger" onClick={() => controlProcess('stop')} disabled={busy || processState === 'STOPPED'}>Stop</button>
        </div>
      </section>

      <div className="content-grid">
        <section className="card">
          <h2>Inspection input</h2>
          <form onSubmit={submitInspection}>
            <label>Component serial number<input required value={inspection.component_serial_number} onChange={(event) => setInspection({ ...inspection, component_serial_number: event.target.value })} /></label>
            <label>Operator ID<input required value={inspection.operator_id} onChange={(event) => setInspection({ ...inspection, operator_id: event.target.value })} /></label>
            <label>Operator name<input value={inspection.operator_name} onChange={(event) => setInspection({ ...inspection, operator_name: event.target.value })} /></label>
            <label>Wire image<input required type="file" accept="image/*" onChange={(event) => setInspection({ ...inspection, image: event.target.files[0] })} /></label>
            <button className="button-primary" disabled={busy || processState !== 'RUNNING' || !inspection.image}>Inspect component</button>
          </form>
        </section>

        <section className="card result-card">
          <h2>Inspection result</h2>
          {result ? (
            <div className={`result result-${result.result.toLowerCase()}`}>
              <strong>{result.result.replace('_', ' ')}</strong>
              <p>Detected: {result.detected_sequence.join(' - ') || 'No wires detected'}</p>
              <p>{result.error_details || 'Sequence evaluated against active settings.'}</p>
            </div>
          ) : <p className="empty-state">Submit an image while the station is running.</p>}
          {message && <p className="message">{message}</p>}
        </section>
      </div>

      <section className="card settings-card">
        <h2>Active inspection settings</h2>
        <form onSubmit={saveSettings} className="settings-form">
          <label>Component name<input required value={settings.component_name} onChange={(event) => setSettings({ ...settings, component_name: event.target.value })} /></label>
          <label>Expected sequence<input required value={settings.expected_sequence} onChange={(event) => setSettings({ ...settings, expected_sequence: event.target.value })} /><small>Use comma-separated color names.</small></label>
          <label>Layer distance (px)<input type="number" min="0" value={settings.layer_distance} onChange={(event) => setSettings({ ...settings, layer_distance: Number(event.target.value) })} /></label>
          <label>Color tolerance<input type="number" min="0" max="255" value={settings.color_tolerance} onChange={(event) => setSettings({ ...settings, color_tolerance: Number(event.target.value) })} /></label>
          <button disabled={busy}>Save settings</button>
        </form>
      </section>

      <section className="card settings-card">
        <div className="history-heading">
          <h2>Inspection history</h2>
          <div className="button-row">
            <button onClick={() => loadHistory().catch((error) => setMessage(error.message))}>Refresh history</button>
            <a className="button-link" href={`${API_BASE}/inspection/history/?export=csv`}>Export CSV</a>
          </div>
        </div>
        {history.length === 0 ? <p className="empty-state">No records loaded.</p> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Serial</th><th>Operator</th><th>Detected sequence</th><th>Result</th><th>Tested at</th></tr></thead>
              <tbody>{history.map((record) => (
                <tr key={record.id}>
                  <td>{record.component_serial_number}</td>
                  <td>{record.operator_name || record.operator_id}</td>
                  <td>{record.detected_sequence.join(' - ') || 'None'}</td>
                  <td><strong>{record.result.replace('_', ' ')}</strong></td>
                  <td>{new Date(record.tested_at).toLocaleString()}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
