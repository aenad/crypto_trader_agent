import { useEffect, useState, type ReactNode } from 'react';
import { Activity, ArrowDownRight, ArrowUpRight, BarChart3, BrainCircuit, Check, ChevronRight,
  CircleHelp, Download, FlaskConical, Gauge, Menu, Radio, RefreshCw, ShieldCheck, Wallet, X } from 'lucide-react';
import { decodeView, sections, type Metric, type Run, type Section, type View } from './types';
import './dashboard.css';

const icons = [Gauge, Activity, BrainCircuit, Wallet, BarChart3, FlaskConical, Radio, ShieldCheck];
const subheads: Record<Section, string> = {
  Overview: 'Your competition, at a glance.', 'Market Monitor': 'The approved universe. Every recorded signal.',
  'AI Analysis': 'Model evidence, with uncertainty in view.', Orders: 'Follow each order from intent to outcome.',
  Performance: 'Returns are only part of the story.', Testing: 'Evidence before confidence.',
  'System Health': 'Know what is connected. Know what is unknown.', 'Competition Report': 'A clear record for the judging panel.',
};
export const money = (v: Metric) => v === null ? 'Not available' : new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Number(v));
const pct = (v: Metric) => v === null ? 'Not available' : `${Number(v).toFixed(2)}%`;
const date = (v: string | null) => v ? new Date(v).toLocaleString('en-GB', { timeZone: 'Asia/Tehran', dateStyle: 'medium', timeStyle: 'short' }) : 'Not recorded';

function Badge({ value }: { value: string }) {
  const tone = /^(BUY|FILLED|ACCEPT|HEALTHY|RECORDED_FRESH)$/.test(value) ? 'good' : /SELL|REJECT|VETO|UNKNOWN|STALE|DIVERGED|LATCHED/.test(value) ? 'warn' : 'neutral';
  return <span className={`badge ${tone}`}>{value.replaceAll('_', ' ')}</span>;
}
function Empty({ children = 'No evidence recorded for this run.' }: { children?: ReactNode }) {
  return <div className="empty"><CircleHelp size={22} /><p>{children}</p></div>;
}
function Panel({ title, eyebrow, right, children, className = '' }: { title: string; eyebrow?: string; right?: ReactNode; children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><header className="panel-head"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h2>{title}</h2></div>{right}</header>{children}</section>;
}
function Table({ columns, rows }: { columns: string[]; rows: ReactNode[][] }) {
  if (!rows.length) return <Empty />;
  return <div className="table-scroll"><table><thead><tr>{columns.map(c => <th key={c}>{c}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>;
}

function Chart({ points, drawdown = false }: { points: View['equity']; drawdown?: boolean }) {
  const [hover, setHover] = useState<number | null>(null);
  if (!points.length) return <Empty>No recorded equity curve.</Empty>;
  const values = points.map(p => Number(drawdown ? p.drawdown_pct : p.equity_tmn));
  const low = Math.min(...values), high = Math.max(...values), spread = high - low || Math.max(Math.abs(high) * .01, 1);
  const min = drawdown ? 0 : low - spread * .18, max = high + spread * .2;
  const y = (n: number) => 175 - (n - min) / (max - min || 1) * 140;
  const xy = values.map((n, i) => `${40 + i / Math.max(values.length - 1, 1) * 690},${y(n)}`);
  const index = hover === null ? values.length - 1 : Math.min(hover, values.length - 1);
  return <div className="chart-wrap"><div className="chart-readout"><strong>{drawdown ? `${values[index].toFixed(2)}%` : money(String(values[index]))}</strong><span>{drawdown ? 'drawdown' : 'TMN'} · {date(points[index].at)}</span></div>
    <svg viewBox="0 0 760 230" role="img" aria-label={drawdown ? 'Recorded drawdown chart' : 'Recorded equity curve'} onMouseMove={e => {
      const rect = e.currentTarget.getBoundingClientRect();
      setHover(Math.max(0, Math.round(((e.clientX - rect.left) / rect.width * 760 - 40) / 690 * (values.length - 1))));
    }} onMouseLeave={() => setHover(null)}>
      <defs><linearGradient id={drawdown ? 'ddFill' : 'eqFill'} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={drawdown ? '#c98252' : '#16836c'} stopOpacity=".18" /><stop offset="100%" stopColor="#fff" stopOpacity="0" /></linearGradient></defs>
      {[0, 1, 2, 3].map(i => <g key={i}><line x1="40" x2="730" y1={35 + i * 47} y2={35 + i * 47} stroke="#e9ece8" strokeDasharray="3 4" /><text x="40" y={28 + i * 47} fill="#8a9390" fontSize="9">{drawdown ? `${(max - i / 3 * (max - min)).toFixed(1)}%` : money(String(max - i / 3 * (max - min)))}</text></g>)}
      <path d={`M40,180 L${xy.join(' L')} L730,180 Z`} fill={`url(#${drawdown ? 'ddFill' : 'eqFill'})`} />
      <polyline points={xy.join(' ')} fill="none" stroke={drawdown ? '#bc794c' : '#16836c'} strokeWidth="2.5" strokeLinejoin="round" />
      <circle cx={40 + index / Math.max(values.length - 1, 1) * 690} cy={y(values[index])} r="4" fill={drawdown ? '#bc794c' : '#16836c'} stroke="white" strokeWidth="2" />
      {[0, Math.floor((points.length - 1) / 2), points.length - 1].map((i, n) => <text key={n} x={40 + n * 345} y="215" textAnchor={n === 2 ? 'end' : 'start'} fill="#8a9390" fontSize="10">{new Date(points[i].at).toLocaleDateString('en-GB', { timeZone: 'Asia/Tehran', month: 'short', day: 'numeric' })}</text>)}
    </svg><div className="chart-caption"><span className={`dot ${drawdown ? 'orange' : ''}`} />{drawdown ? 'Peak-to-trough decline' : 'Account equity'}<span>Display rounded · exports retain decimal precision</span></div></div>;
}

function Metrics({ view }: { view: View }) {
  const m = view.metrics;
  const cards = [
    { label: 'Initial capital', value: money(m.initial_capital_tmn), unit: 'TMN', note: 'Toman · not IRR' },
    { label: view.source.simulated ? 'Simulated / virtual equity' : 'Recorded account equity', value: money(m.equity_tmn), unit: 'TMN', note: 'Marked account value' },
    { label: 'Realized PnL', value: money(m.realized_pnl_tmn), unit: 'TMN', note: 'After recorded trading costs' },
    { label: 'Competition net return', value: pct(m.net_return_pct), unit: '', note: 'Provisional · selected run only' },
    { label: 'Maximum drawdown', value: pct(m.max_drawdown_pct), unit: '', note: 'Observed equity samples' },
  ];
  return <div className="metrics-grid">{cards.map((c, i) => <section className={`metric ${i === 1 ? 'metric-featured' : ''}`} key={c.label}><div className="metric-label">{c.label}{i === 1 ? <Wallet size={15} /> : i === 4 ? <ArrowDownRight size={15} /> : <ArrowUpRight size={15} />}</div><div className="metric-value">{c.value}<small>{c.unit}</small></div><p>{c.note}</p></section>)}</div>;
}
function Comparison({ view }: { view: View }) {
  return <Panel title="Does AI add value?" eyebrow="STRATEGY COMPARISON"><p className="panel-note">{view.ai_contribution}</p><Table columns={['Variant', 'Net return', 'Max drawdown', 'Trades', 'Fees · TMN']} rows={view.comparison.map(c => [c.variant, pct(c.net_return_pct), pct(c.max_drawdown_pct), c.trades, money(c.fees_tmn)])} /></Panel>;
}
function Health({ view }: { view: View }) {
  return <div className="health-list">{view.health.map((h, i) => <div className="health-row" key={i}><span className="health-icon"><Radio size={16} /></span><div><strong>{h.name}</strong><p>{h.detail}</p></div><Badge value={h.status} /></div>)}</div>;
}
function Markets({ view }: { view: View }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  return <Panel title="Approved market universe" eyebrow="SPOT ONLY · NO LEVERAGE" right={<input aria-label="Search approved markets" placeholder="Search symbol…" value={search} onChange={e => setSearch(e.target.value)} />}><div className="pills" role="group" aria-label="Signal filter">{['ALL', 'BUY', 'SELL', 'HOLD'].map(f => <button key={f} className={filter === f ? 'selected' : ''} onClick={() => setFilter(f)}>{f}</button>)}</div>
    <Table columns={['Market', 'Status', 'Signal', 'Observed · Tehran', 'Reason']} rows={view.markets.filter(m => (filter === 'ALL' || m.action === filter) && m.symbol.toLowerCase().includes(search.toLowerCase())).map(m => [<strong>{m.symbol}</strong>, <Badge value={m.status} />, <Badge value={m.action} />, date(m.as_of), m.reasons.join(' · ') || 'Not recorded'])} /></Panel>;
}
function Orders({ view }: { view: View }) {
  const [tab, setTab] = useState('Orders');
  return <Panel title="Execution ledger" eyebrow="READ ONLY" right={<span className="muted">No trading actions available</span>}><div className="pills">{['Orders', 'Fills', 'Rejections'].map(t => <button key={t} onClick={() => setTab(t)} className={t === tab ? 'selected' : ''}>{t}</button>)}</div>
    {tab === 'Orders' && <Table columns={['Order', 'Market', 'Side', 'Status', 'Quantity / filled', 'API latency']} rows={view.orders.map(o => [<code title={o.id}>{o.id.slice(0, 19)}</code>, o.symbol, <Badge value={o.side} />, <Badge value={o.state} />, `${o.quantity} / ${o.filled_quantity ?? 'Not recorded'}`, o.latency_ms === null ? 'Not recorded' : `${o.latency_ms} ms`])} />}
    {tab === 'Fills' && <Table columns={['Fill', 'Market', 'Side', 'Quantity', 'Price', 'Fee', 'Executed · Tehran']} rows={view.fills.map(f => [<code title={f.id}>{f.id.slice(0, 14)}</code>, f.symbol, <Badge value={f.side} />, f.quantity, money(f.price), `${f.fee} ${f.fee_currency}`, date(f.at)])} />}
    {tab === 'Rejections' && <Table columns={['Market', 'Observed · Tehran', 'Rejection reasons']} rows={view.rejections.map(r => [r.symbol, date(r.at), r.reasons.join(' · ')])} />}
  </Panel>;
}
function Evidence({ view }: { view: View }) {
  return <Table columns={['Evidence', 'Status', 'Recorded detail']} rows={view.evidence.map(e => [e.name, <Badge value={e.status} />, e.detail])} />;
}
function Daily({ view }: { view: View }) {
  return <Panel title="Activity across trading days" eyebrow="TEHRAN CALENDAR"><Table columns={['Day', 'Equity change · TMN', 'Decisions', 'Fills']} rows={view.daily.map(d => [d.day, money(d.pnl_tmn), d.decisions, d.fills])} /><p className="panel-note">Observed days: {view.daily.length}. Calendar coverage does not certify three complete competition days. Daily PnL is the change in sampled equity.</p></Panel>;
}
function Downloads({ id }: { id: string }) {
  return <div className="downloads">{['md', 'json', 'csv'].map(format => <a className="button" key={format} href={`/api/dashboard/reports/${id}.${format}`} download><Download size={14} />{format === 'md' ? 'Judge report' : format.toUpperCase()}</a>)}</div>;
}

export default function App() {
  const [section, setSection] = useState<Section>('Overview');
  const [runs, setRuns] = useState<Run[]>([{ id: 'demo', title: 'Competition rehearsal', kind: 'DEMO' }]);
  const [run, setRun] = useState('demo');
  const [view, setView] = useState<View | null>(null);
  const [error, setError] = useState('');
  const [catalogError, setCatalogError] = useState('');
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    const abort = new AbortController();
    fetch('/api/dashboard/runs', { signal: abort.signal }).then(async r => {
      if (!r.ok) throw Error();
      const list = await r.json() as Run[];
      if (!Array.isArray(list) || !list.every(x => /^[a-z0-9-]+$/.test(x.id))) throw Error();
      setRuns(list); setCatalogError('');
    }).catch(() => { if (!abort.signal.aborted) setCatalogError('Recorded-run catalog unavailable. Demo remains explicitly simulated.'); });
    return () => abort.abort();
  }, [revision]);
  useEffect(() => {
    const abort = new AbortController();
    setView(null); setError(''); setLoading(true);
    let busy = false;
    const load = async () => {
      if (busy) return;
      busy = true;
      const requestAbort = new AbortController();
      const relay = () => requestAbort.abort();
      abort.signal.addEventListener('abort', relay, { once: true });
      const timeout = setTimeout(relay, 15000);
      try {
        const response = await fetch(`/api/dashboard/runs/${run}`, { signal: requestAbort.signal, cache: 'no-store' });
        if (!response.ok) throw Error();
        const result = decodeView(await response.json(), run);
        if (!abort.signal.aborted) { setView(result); setError(''); setLoading(false); }
      } catch {
        if (!abort.signal.aborted) { setView(null); setError('This report is unavailable. No simulated fallback has been substituted.'); setLoading(false); }
      } finally { busy = false; clearTimeout(timeout); abort.signal.removeEventListener('abort', relay); }
    };
    void load();
    const interval = setInterval(() => void load(), 10000);
    return () => { abort.abort(); clearInterval(interval); };
  }, [run, revision]);
  return <div className="app-shell"><aside className={mobile ? 'sidebar mobile-open' : 'sidebar'}><a className="brand" href="#" aria-label="QuantPilot home" onClick={() => setSection('Overview')}><span className="brand-mark"><Activity size={22} /></span><span>QuantPilot<small>WALLEX TRADING LAB</small></span></a><div className="nav-caption">COMPETITION WORKSPACE</div><nav aria-label="Main navigation">{sections.map((item, i) => {
    const Icon = icons[i]; return <button key={item} className={section === item ? 'nav-item active' : 'nav-item'} aria-current={section === item ? 'page' : undefined} onClick={() => { setSection(item); setMobile(false); }}><Icon size={18} />{item}{section === item && <ChevronRight size={15} className="nav-chevron" />}</button>;
  })}</nav><div className="sidebar-bottom"><div className="core-badge"><ShieldCheck size={20} /><div>One deterministic core<small>Risk authorizes. AI advises.</small></div></div><p>SPOT ONLY <span>·</span> NO LEVERAGE</p><div className="profile"><span>QP</span><div>Competition workspace<small>Read-only dashboard</small></div></div></div></aside>
    <div className="main-shell"><header className="topbar"><button className="icon-button mobile-toggle" aria-label="Toggle navigation" aria-expanded={mobile} onClick={() => setMobile(!mobile)}>{mobile ? <X size={20} /> : <Menu size={20} />}</button><div className="breadcrumb">Workspace <ChevronRight size={13} /><strong>{section}</strong></div><div className="top-actions"><span className="read-only"><span className="dot" /> READ ONLY</span><label className="run-label">Data source<select aria-label="Data source" value={run} onChange={e => { setView(null); setRun(e.target.value); }}>
      {runs.map(r => <option value={r.id} key={r.id}>{r.kind} · {r.title}</option>)}</select></label><button className="icon-button" aria-label="Refresh report" onClick={() => setRevision(x => x + 1)}><RefreshCw size={17} className={loading ? 'spin' : ''} /></button></div></header>
      <main><div className="page-heading"><div><div className="eyebrow">WALLEX QUANTPILOT <span>/</span> COMPETITION INTELLIGENCE</div><h1>{section}</h1><p>{subheads[section]}</p></div><span className="competition-chip"><FlaskConical size={15} /> 3-day trading challenge</span></div>
        {catalogError && <div className="notice" role="status">{catalogError}</div>}
        {loading && <div role="status" className="loading-state"><RefreshCw className="spin" size={22} /> Loading selected report…</div>}
        {error && <div className="error-state" role="alert"><h2>Report unavailable</h2><p>{error}</p><button className="button" onClick={() => setRevision(x => x + 1)}>Retry</button></div>}
        {view && <><div className={`source-banner ${view.source.simulated ? 'simulation' : 'recorded-live'}`} role="status"><FlaskConical size={19} /><div><strong>{view.source.label}</strong><span>{view.source.simulated ? 'Performance shown here is not real trading performance.' : 'Operator-provided account evidence; this dashboard does not verify exchange state.'}</span></div><span className="source-date">Data as of {date(view.source.as_of)}{view.source.stale && <b> · STALE EXPORT</b>}</span></div>
          {(section === 'Overview' || section === 'Performance' || section === 'Competition Report') && <Metrics view={view} />}
          {section === 'Overview' && <><div className="overview-grid"><Panel title="Equity over the competition" eyebrow="PORTFOLIO PERFORMANCE" right={<Badge value={view.source.kind} />}><Chart points={view.equity} /></Panel><Panel title="System snapshot" eyebrow="OBSERVED STATUS"><Health view={view} /></Panel></div><div className="overview-grid lower-grid"><Panel title="Latest strategy signals" eyebrow="APPROVED MARKETS" right={<button className="text-button" onClick={() => setSection('Market Monitor')}>View markets <ChevronRight size={14} /></button>}><Table columns={['Market', 'Signal', 'Market status', 'Observed · Tehran']} rows={view.markets.slice(0, 5).map(m => [<strong>{m.symbol}</strong>, <Badge value={m.action} />, <Badge value={m.status} />, date(m.as_of)])} /></Panel><Panel title="Built for explainability" eyebrow="THE DECISION PATH"><div className="decision-path">{['Market data', 'Quant strategy', 'AI evaluation', 'Risk authorization'].map((step, i) => <div key={step}><span>{String(i + 1).padStart(2, '0')}</span>{step}{i === 3 && <Check size={15} />}</div>)}</div></Panel></div></>}
          {section === 'Market Monitor' && <Markets view={view} />}
          {section === 'AI Analysis' && <><Panel title="Hybrid signal assessment" eyebrow="AI ADVISES · NEVER SUBMITS ORDERS"><p className="panel-note">Trade-quality probabilities are model estimates, not guaranteed profits. Missing model/prompt evidence stays unavailable.</p><Table columns={['Market', 'Quality score', 'LLM assessment', 'Fusion', 'Model version', 'Prompt version']} rows={view.ai.map(a => [a.symbol, a.score === null ? 'Not recorded' : <div className="score"><span style={{ width: `${Number(a.score) * 100}%` }} /><b>{(Number(a.score) * 100).toFixed(1)}%</b></div>, <Badge value={a.assessment} />, <Badge value={a.fusion} />, <div><code>{a.model_version ?? 'Not recorded'}</code><small style={{display:'block'}}>LLM: {a.analyst_model_version ?? 'Not recorded'}</small></div>, <code>{a.prompt_version ?? 'Not recorded'}</code>])} /></Panel><Comparison view={view} /></>}
          {section === 'Orders' && <Orders view={view} />}
          {section === 'Performance' && <><div className="two-columns"><Panel title="Equity curve"><Chart points={view.equity} /></Panel><Panel title="Drawdown"><Chart points={view.equity} drawdown /></Panel></div><div className="performance-strip"><div>Win rate<strong>{pct(view.metrics.win_rate_pct)}</strong></div><div>Closed trades<strong>{view.metrics.trade_count ?? "Not available"}</strong></div><div>Total fees · TMN<strong>{money(view.metrics.fees_tmn)}</strong></div></div><Daily view={view} /><Comparison view={view} /></>}
          {section === 'Testing' && <><Panel title="Evidence registry" eyebrow="RECORDED, NOT ASSUMED" right={<Downloads id={run} />}><Evidence view={view} /></Panel><Comparison view={view} /></>}
          {section === 'System Health' && <><Panel title="Connections & circuit breakers" eyebrow="NO ASSUMED UPTIME"><Health view={view} /></Panel><Panel title="Operating boundary"><p className="panel-note">The dashboard polls recorded artifacts every 10 seconds. It does not connect to MCP, stream WebSocket data, start a runner, clear a circuit breaker or enable LIVE. API service health is separate from trading-system health.</p><div className="content-id">Report identity <code>{view.source.content_id}</code></div></Panel></>}
          {section === 'Competition Report' && <><Panel title="Competition evaluation" eyebrow="JUDGE'S VIEW" right={<Downloads id={run} />}><p className="panel-note">Provisional report · no certified final liquidation imported. Every download preserves source, mode and simulation labels.</p><div className="report-copy"><h3>Strategy explanation</h3><p>{view.strategy}</p><h3>AI contribution</h3><p>{view.ai_contribution}</p><h3>Risk management</h3><p>{view.risk_policy}</p><h3>Execution reliability</h3><p>{view.orders.length} displayed orders · {view.orders.filter(o => o.state === 'UNKNOWN').length} unknown outcomes · {view.rejections.length} displayed rejections. Missing latency and exchange telemetry are not reported as success.</p></div></Panel><Daily view={view} /><Panel title="Reproducibility & testing"><Evidence view={view} /></Panel></>}
          <details className="limitations"><summary>Evidence & remaining limitations <span>{view.limitations.length}</span></summary><ul>{view.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul></details><footer><span>QuantPilot <b>·</b> Deterministic by design.</span><span>Amounts in TMN (Toman) · Timestamps in Tehran</span></footer></>}
      </main></div></div>;
}
