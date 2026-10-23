import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import App, { money } from './App';
import fixture from './demo.fixture.json';
import { decodeView, sections } from './types';

const runs = [{ id: 'demo', title: 'Competition rehearsal', kind: 'DEMO' },
  { id: 'recorded', title: 'Recorded virtual session', kind: 'SHADOW' }];
function mockApi(handler?: (url: string) => Promise<unknown>) {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    const body = url.endsWith('/runs') ? runs : handler ? await handler(url) : structuredClone(fixture);
    return { ok: true, json: async () => body };
  }));
}

describe('dashboard evidence boundaries', () => {
  it('labels simulated performance and renders every requested section', async () => {
    mockApi(); render(<App />);
    await screen.findByText('SIMULATED · UI demonstration only');
    expect(screen.getByText('Performance shown here is not real trading performance.')).toBeTruthy();
    for (const section of sections) {
      fireEvent.click(screen.getByRole('button', { name: section }));
      expect(screen.getByRole('heading', { name: section, level: 1 })).toBeTruthy();
    }
    expect(screen.getByRole('link', { name: 'Judge report' }).getAttribute('href')).toBe('/api/dashboard/reports/demo.md');
  });
  it('filters approved market signals and searches by symbol', async () => {
    mockApi(); render(<App />); await screen.findByText('SIMULATED · UI demonstration only');
    fireEvent.click(screen.getByRole('button', { name: 'Market Monitor' }));
    fireEvent.click(screen.getByRole('button', { name: 'BUY' }));
    expect(screen.getByText('BTC/TMN')).toBeTruthy();
    expect(screen.queryByText('ETH/TMN')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'ALL' }));
    fireEvent.change(screen.getByLabelText('Search approved markets'), { target: { value: 'ETH' } });
    expect(screen.queryByText('BTC/TMN')).toBeNull();
    expect(screen.getByText('ETH/TMN')).toBeTruthy();
  });
  it('exposes fills and rejected signals in read-only tabs', async () => {
    mockApi(); render(<App />); await screen.findByText('SIMULATED · UI demonstration only');
    fireEvent.click(screen.getByRole('button', { name: 'Orders' }));
    fireEvent.click(screen.getByRole('button', { name: 'Fills' }));
    expect(screen.getByText('demo-fill-01')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Rejections' }));
    expect(screen.getByText('AI_VETO · WEAK_MOMENTUM')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /submit|activate|withdraw|buy order/i })).toBeNull();
  });
  it('does not replace unavailable records with a demo', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false })));
    render(<App />);
    await screen.findByRole('alert');
    expect(screen.getByText(/No simulated fallback/)).toBeTruthy();
    expect(screen.queryByText('4.30%')).toBeNull();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
  });
  it('clears old metrics immediately when changing data source', async () => {
    let release!: (value: unknown) => void;
    mockApi(url => url.endsWith('/demo') ? Promise.resolve(structuredClone(fixture)) : new Promise(resolve => { release = resolve; }));
    render(<App />); await screen.findByText('SIMULATED · UI demonstration only');
    await waitFor(() => expect(screen.getAllByRole('option')).toHaveLength(2));
    fireEvent.change(screen.getByLabelText('Data source'), { target: { value: 'recorded' } });
    expect(screen.queryByText('4.30%')).toBeNull();
    expect(screen.queryByText('SIMULATED · UI demonstration only')).toBeNull();
    release({ ...structuredClone(fixture), source: { ...fixture.source, id: 'recorded', kind: 'SHADOW',
      label: 'VIRTUAL · Live-data SHADOW', stale: true } });
    await screen.findByText('VIRTUAL · Live-data SHADOW');
    expect(screen.getByText(/STALE EXPORT/)).toBeTruthy();
  });
  it('keeps unavailable money distinct from zero and validates provenance', () => {
    expect(money(null)).toBe('Not available'); expect(money('0')).toBe('0');
    expect(() => decodeView({ ...fixture, source: { ...fixture.source, simulated: false } }, 'demo')).toThrow();
    expect(() => decodeView(fixture, 'other')).toThrow();
  });
  it('supports the mobile navigation toggle', async () => {
    mockApi(); render(<App />); await screen.findByText('SIMULATED · UI demonstration only');
    const toggle = screen.getByRole('button', { name: 'Toggle navigation' });
    fireEvent.click(toggle); expect(toggle.getAttribute('aria-expanded')).toBe('true');
    fireEvent.click(screen.getByRole('button', { name: 'System Health' }));
    expect(toggle.getAttribute('aria-expanded')).toBe('false');
  });
});
