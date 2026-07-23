import { useState } from "react";

const API_BASE = "http://localhost:8000";

const CATEGORY_OPTIONS = [
  { value: "cafe", label: "카페" },
  { value: "restaurant", label: "음식점" },
  { value: "fast_food", label: "패스트푸드" },
  { value: "convenience", label: "편의점" },
  { value: "supermarket", label: "마트/슈퍼마켓" },
];

const TOP_N_SOURCES = 7;

function StatTile({ label, value }) {
  return (
    <div className="whatif-stat">
      <div className="whatif-stat__label">{label}</div>
      <div className="whatif-stat__value">{value}</div>
    </div>
  );
}

function SourceBreakdownChart({ sourceBreakdown }) {
  const [hovered, setHovered] = useState(null);
  const [showTable, setShowTable] = useState(false);

  const entries = Object.entries(sourceBreakdown || {}).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    return (
      <div className="whatif-chart">
        <h4>이탈 출처 (전환 시민이 이전에 다니던 매장)</h4>
        <p className="whatif-chart__empty">전환한 시민이 없습니다.</p>
      </div>
    );
  }

  const top = entries.slice(0, TOP_N_SOURCES);
  const rest = entries.slice(TOP_N_SOURCES);
  const restSum = rest.reduce((sum, [, v]) => sum + v, 0);
  const bars = restSum > 0 ? [...top, ["기타", restSum]] : top;
  const max = Math.max(...bars.map(([, v]) => v));

  return (
    <div className="whatif-chart">
      <div className="whatif-chart__head">
        <h4>이탈 출처 (전환 시민이 이전에 다니던 매장)</h4>
        {entries.length > TOP_N_SOURCES && (
          <button type="button" className="whatif-chart__table-toggle" onClick={() => setShowTable((s) => !s)}>
            {showTable ? "차트로 보기" : "표로 보기 (전체)"}
          </button>
        )}
      </div>
      {!showTable ? (
        <div className="whatif-hbar">
          {bars.map(([label, value]) => (
            <div
              key={label}
              className="whatif-hbar__row"
              onMouseEnter={() => setHovered(label)}
              onMouseLeave={() => setHovered(null)}
            >
              <span className="whatif-hbar__label" title={label}>{label}</span>
              <div className="whatif-hbar__track">
                <div className="whatif-hbar__fill" style={{ width: `${(value / max) * 100}%` }} />
              </div>
              <span className="whatif-hbar__value">{value}</span>
              {hovered === label && (
                <div className="whatif-hbar__tooltip">{label}: {value}명</div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <table className="whatif-table">
          <thead>
            <tr><th>매장</th><th>전환 수</th></tr>
          </thead>
          <tbody>
            {entries.map(([label, value]) => (
              <tr key={label}><td>{label}</td><td>{value}</td></tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function HourlyBarChart({ hourlyDistribution }) {
  const [hovered, setHovered] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const hours = Array.from({ length: 24 }, (_, h) => h);
  const values = hours.map((h) => Number(hourlyDistribution?.[h] ?? hourlyDistribution?.[String(h)] ?? 0));
  const max = Math.max(1, ...values);

  return (
    <div className="whatif-chart">
      <div className="whatif-chart__head">
        <h4>시간대별 방문 분포 (7일 누적)</h4>
        <button type="button" className="whatif-chart__table-toggle" onClick={() => setShowTable((s) => !s)}>
          {showTable ? "차트로 보기" : "표로 보기"}
        </button>
      </div>
      {!showTable ? (
        <div className="whatif-vbar">
          {hours.map((h) => (
            <div
              key={h}
              className="whatif-vbar__col"
              onMouseEnter={() => setHovered(h)}
              onMouseLeave={() => setHovered(null)}
            >
              {hovered === h && (
                <div className="whatif-vbar__tooltip">{h}시: {values[h]}회</div>
              )}
              <div className="whatif-vbar__bar" style={{ height: `${(values[h] / max) * 100}%` }} />
              {h % 3 === 0 && <span className="whatif-vbar__tick">{h}</span>}
            </div>
          ))}
        </div>
      ) : (
        <table className="whatif-table">
          <thead>
            <tr><th>시간대</th><th>방문 수</th></tr>
          </thead>
          <tbody>
            {hours.map((h) => (
              <tr key={h}><td>{h}시</td><td>{values[h]}</td></tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function WhatIfPanel({ location, onClose }) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState(CATEGORY_OPTIONS[0].value);
  const [status, setStatus] = useState("form"); // form | loading | done | error
  const [report, setReport] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setStatus("loading");
    setErrorMsg("");
    try {
      const res = await fetch(`${API_BASE}/api/whatif`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lon: location.lon,
          lat: location.lat,
          name: name.trim(),
          category,
        }),
      });
      if (!res.ok) throw new Error(`서버 오류 (${res.status})`);
      const data = await res.json();
      setReport(data);
      setStatus("done");
    } catch (err) {
      setErrorMsg(err.message || "요청 실패 — api 서버가 실행 중인지 확인하세요");
      setStatus("error");
    }
  }

  return (
    <div className="whatif-panel">
      <style>{`
        .whatif-panel {
          --surface-1: #fcfcfb;
          --text-primary: #0b0b0b;
          --text-secondary: #52514e;
          --text-muted: #898781;
          --series-1: #2a78d6;
          --gridline: #e1e0d9;
          --border: rgba(11,11,11,0.10);
          --danger: #d03b3b;
        }
        @media (prefers-color-scheme: dark) {
          .whatif-panel {
            --surface-1: #1a1a19;
            --text-primary: #ffffff;
            --text-secondary: #c3c2b7;
            --text-muted: #898781;
            --series-1: #3987e5;
            --gridline: #2c2c2a;
            --border: rgba(255,255,255,0.10);
          }
        }
        .whatif-panel {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 340px;
          max-height: calc(100vh - 16px);
          overflow-y: auto;
          background: var(--surface-1);
          color: var(--text-primary);
          border-radius: 8px;
          border: 1px solid var(--border);
          box-shadow: 0 2px 12px rgba(0,0,0,0.18);
          padding: 14px 16px;
          font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
          font-size: 13px;
          box-sizing: border-box;
        }
        .whatif-panel__header { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }
        .whatif-panel__header strong { font-size: 14px; }
        .whatif-panel__close { background:none;border:none;font-size:18px;line-height:1;cursor:pointer;color:var(--text-secondary); padding: 0 2px; }
        .whatif-panel__coord { color: var(--text-secondary); font-size:12px; margin-bottom:10px; }
        .whatif-panel__form { display:flex; flex-direction:column; gap:10px; }
        .whatif-panel__form label { display:flex; flex-direction:column; gap:4px; font-size:12px; color:var(--text-secondary); }
        .whatif-panel__form input, .whatif-panel__form select {
          font: inherit; padding:6px 8px; border-radius:4px; border:1px solid var(--gridline);
          background: var(--surface-1); color: var(--text-primary);
        }
        .whatif-panel__submit {
          background: var(--series-1); color:#fff; border:none; border-radius:4px;
          padding:8px 12px; font-weight:600; cursor:pointer;
        }
        .whatif-panel__error { color: var(--danger); font-size:12px; }
        .whatif-panel__loading { display:flex; align-items:center; gap:8px; padding:12px 0; color:var(--text-secondary); }
        .whatif-panel__spinner {
          width:16px;height:16px;border-radius:50%; flex-shrink:0;
          border:2px solid var(--gridline); border-top-color: var(--series-1);
          animation: whatif-spin 0.8s linear infinite;
        }
        @keyframes whatif-spin { to { transform: rotate(360deg); } }
        .whatif-panel__stats { display:flex; gap:10px; margin-bottom:16px; }
        .whatif-stat { flex:1; }
        .whatif-stat__label { font-size:11px; color:var(--text-secondary); }
        .whatif-stat__value { font-size:22px; font-weight:600; color: var(--text-primary); }
        .whatif-chart { margin-bottom:18px; }
        .whatif-chart h4 { font-size:12px; font-weight:600; color:var(--text-secondary); margin:0 0 8px; }
        .whatif-chart__head { display:flex; justify-content:space-between; align-items:baseline; gap:8px; }
        .whatif-chart__table-toggle { background:none;border:none;color:var(--series-1);font-size:11px;cursor:pointer;padding:0; }
        .whatif-chart__empty { color: var(--text-muted); font-size:12px; }
        .whatif-hbar { display:flex; flex-direction:column; gap:6px; }
        .whatif-hbar__row { position:relative; display:grid; grid-template-columns: 84px 1fr 30px; align-items:center; gap:6px; }
        .whatif-hbar__label { font-size:11px; color:var(--text-secondary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .whatif-hbar__track { height:16px; background:var(--gridline); border-radius:4px; overflow:hidden; }
        .whatif-hbar__fill { height:100%; background:var(--series-1); border-radius:0 4px 4px 0; min-width:2px; }
        .whatif-hbar__value { font-size:11px; color:var(--text-secondary); text-align:right; }
        .whatif-hbar__tooltip {
          position:absolute; left:84px; top:-20px; background:var(--text-primary); color:var(--surface-1);
          font-size:11px; padding:2px 6px; border-radius:4px; white-space:nowrap; pointer-events:none; z-index:2;
        }
        .whatif-vbar { display:flex; align-items:flex-end; gap:2px; height:110px; border-bottom:1px solid var(--gridline); padding-top:18px; }
        .whatif-vbar__col { position:relative; flex:1; height:100%; display:flex; align-items:flex-end; justify-content:center; }
        .whatif-vbar__bar { width:100%; background:var(--series-1); border-radius:4px 4px 0 0; min-height:1px; }
        .whatif-vbar__tick { position:absolute; bottom:-16px; font-size:9px; color:var(--text-muted); }
        .whatif-vbar__tooltip {
          position:absolute; top:-20px; left:50%; transform:translateX(-50%); background:var(--text-primary); color:var(--surface-1);
          font-size:11px; padding:2px 6px; border-radius:4px; white-space:nowrap; pointer-events:none; z-index:2;
        }
        .whatif-table { width:100%; border-collapse:collapse; font-size:11px; }
        .whatif-table th, .whatif-table td { text-align:left; padding:4px 6px; border-bottom:1px solid var(--gridline); }
        .whatif-table td:last-child, .whatif-table th:last-child { text-align:right; }
        .whatif-panel__retry {
          width:100%; margin-top:4px; background:none; border:1px solid var(--gridline); border-radius:4px;
          padding:6px; font-size:12px; color:var(--text-secondary); cursor:pointer;
        }
      `}</style>

      <div className="whatif-panel__header">
        <strong>신규 매장 시뮬레이션</strong>
        <button type="button" className="whatif-panel__close" onClick={onClose} aria-label="닫기">×</button>
      </div>
      <div className="whatif-panel__coord">
        위치: {location.lat.toFixed(5)}, {location.lon.toFixed(5)}
      </div>

      {(status === "form" || status === "error") && (
        <form onSubmit={handleSubmit} className="whatif-panel__form">
          <label>
            매장명
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="예: 성수 신규 카페"
              required
            />
          </label>
          <label>
            업종
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </label>
          {status === "error" && <div className="whatif-panel__error">{errorMsg}</div>}
          <button type="submit" className="whatif-panel__submit">리포트 생성</button>
        </form>
      )}

      {status === "loading" && (
        <div className="whatif-panel__loading">
          <div className="whatif-panel__spinner" />
          <span>시뮬레이션 실행 중... (최대 몇 분 소요될 수 있어요)</span>
        </div>
      )}

      {status === "done" && report && (
        <div className="whatif-panel__report">
          <div className="whatif-panel__stats">
            <StatTile label="예상 일평균 방문자 수" value={report.daily_average_visits.toFixed(1)} />
            <StatTile label="전환 시민 수 (7일 누적)" value={report.switched_citizens.toLocaleString()} />
          </div>
          <SourceBreakdownChart sourceBreakdown={report.source_breakdown} />
          <HourlyBarChart hourlyDistribution={report.hourly_distribution} />
          <button type="button" className="whatif-panel__retry" onClick={() => setStatus("form")}>
            다시 입력
          </button>
        </div>
      )}
    </div>
  );
}

export default WhatIfPanel;
