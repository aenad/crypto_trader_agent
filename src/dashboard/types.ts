export type Mode = 'DEMO' | 'BACKTEST' | 'SHADOW' | 'LIVE';
export type Run = { id: string; title: string; kind: Mode };
export type Metric = string | null;
export type View = {
  schema_version: 'dashboard-v1';
  source: Run & { simulated: boolean; label: string; as_of: string | null; content_id: string; stale: boolean };
  generated_at: string;
  metrics: { initial_capital_tmn: Metric; equity_tmn: Metric; realized_pnl_tmn: Metric;
    net_return_pct: Metric; max_drawdown_pct: Metric; win_rate_pct: Metric; fees_tmn: Metric; trade_count: number | null };
  equity: { at: string; equity_tmn: string; drawdown_pct: string }[];
  markets: { symbol: string; status: string; action: string; as_of: string | null; reasons: string[] }[];
  ai: { symbol: string; as_of: string | null; score: Metric; assessment: string; fusion: string;
    model_version: string | null; prompt_version: string | null; analyst_model_version: string | null }[];
  orders: { id: string; symbol: string; side: string; state: string; quantity: string;
    filled_quantity: Metric; at: string | null; latency_ms: Metric }[];
  fills: { id: string; order_id: string; symbol: string; side: string; quantity: string; price: string;
    fee: string; fee_currency: string; at: string }[];
  rejections: { symbol: string; at: string | null; reasons: string[] }[];
  daily: { day: string; pnl_tmn: string; decisions: number; fills: number }[];
  comparison: { variant: string; net_return_pct: Metric; max_drawdown_pct: Metric; trades: number; fees_tmn: Metric }[];
  evidence: { name: string; status: string; detail: string }[];
  health: { name: string; status: string; detail: string }[];
  limitations: string[]; strategy: string; risk_policy: string; ai_contribution: string;
};

export const sections = ['Overview', 'Market Monitor', 'AI Analysis', 'Orders', 'Performance',
  'Testing', 'System Health', 'Competition Report'] as const;
export type Section = typeof sections[number];

export function decodeView(raw: unknown, id: string): View {
  if (!raw || typeof raw !== 'object') throw Error('Invalid report');
  const v = raw as View;
  if (v.schema_version !== 'dashboard-v1' || v.source?.id !== id ||
      !['DEMO', 'BACKTEST', 'SHADOW', 'LIVE'].includes(v.source?.kind) ||
      v.source.simulated !== (v.source.kind !== 'LIVE') || !v.metrics ||
      !['equity', 'markets', 'ai', 'orders', 'fills', 'rejections', 'daily', 'comparison',
        'evidence', 'health', 'limitations'].every(k => Array.isArray((v as unknown as Record<string, unknown>)[k]))) {
    throw Error('Invalid report provenance');
  }
  for (const [key, value] of Object.entries(v.metrics)) {
    if (key !== 'trade_count' && value !== null &&
        (typeof value !== 'string' || !Number.isFinite(Number(value)))) throw Error('Invalid numeric report');
  }
  return v;
}
