import React, { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function Card({ children }) {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: 12,
      padding: 14,
      marginBottom: 12,
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
    }}>
      {children}
    </div>
  )
}

function CodeBlock({ obj }) {
  return (
    <pre style={{
      background: '#0b1020',
      color: '#e8f0ff',
      padding: 12,
      borderRadius: 12,
      overflow: 'auto',
      fontSize: 12
    }}>
      {JSON.stringify(obj, null, 2)}
    </pre>
  )
}

export default function App() {
  const [query, setQuery] = useState('')
  const [k, setK] = useState(8)
  const [hits, setHits] = useState([])
  const [loadingSearch, setLoadingSearch] = useState(false)

  const [extracting, setExtracting] = useState(false)
  const [extraction, setExtraction] = useState(null)
  const [error, setError] = useState(null)

  const grouped = useMemo(() => {
    const byPaper = new Map()
    for (const h of hits) {
      const arr = byPaper.get(h.paper_id) || []
      arr.push(h)
      byPaper.set(h.paper_id, arr)
    }
    return Array.from(byPaper.entries())
  }, [hits])

  async function doSearch() {
    setError(null)
    setExtraction(null)
    setLoadingSearch(true)
    try {
      const resp = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, k: Number(k) })
      })
      if (!resp.ok) throw new Error(await resp.text())
      const js = await resp.json()
      setHits(js.hits || [])
    } catch (e) {
      setError(String(e))
    } finally {
      setLoadingSearch(false)
    }
  }

  async function doExtract() {
    setError(null)
    setExtraction(null)
    setExtracting(true)
    try {
      const resp = await fetch(`${API_BASE}/api/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, k: 10 })
      })
      if (!resp.ok) throw new Error(await resp.text())
      const js = await resp.json()
      setExtraction(js)
    } catch (e) {
      setError(String(e))
    } finally {
      setExtracting(false)
    }
  }

  return (
    <div style={{ maxWidth: 1040, margin: '32px auto', padding: '0 16px', fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' }}>
      <h1 style={{ marginBottom: 6 }}>Lit RAG Extractor</h1>
      <div style={{ color: '#444', marginBottom: 18 }}>
        Question-driven prevalence/incidence extraction with citations.
      </div>

      <Card>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask: prevalence/incidence question (e.g., 'What is the prevalence of diabetes in US adults after 2018?')"
            style={{ flex: 1, padding: 12, borderRadius: 10, border: '1px solid #ccc' }}
          />
          <input
            value={k}
            onChange={(e) => setK(e.target.value)}
            type="number"
            min="3"
            max="30"
            style={{ width: 90, padding: 12, borderRadius: 10, border: '1px solid #ccc' }}
            title="top-k"
          />
          <button onClick={doSearch} disabled={!query || loadingSearch}
            style={{ padding: '12px 14px', borderRadius: 10, border: '1px solid #111', background: loadingSearch ? '#eee' : '#111', color: loadingSearch ? '#111' : '#fff', cursor: 'pointer' }}>
            {loadingSearch ? 'Searching…' : 'Search'}
          </button>
          <button onClick={doExtract} disabled={!query || extracting}
            style={{ padding: '12px 14px', borderRadius: 10, border: '1px solid #0a5', background: extracting ? '#eafff3' : '#eafff3', color: '#063', cursor: 'pointer' }}>
            {extracting ? 'Extracting…' : 'Extract'}
          </button>
        </div>
        <div style={{ marginTop: 10, color: '#666', fontSize: 13 }}>
          Tip: run Search first to inspect passages; run Extract for structured JSON.
        </div>
      </Card>

      {error && (
        <Card>
          <div style={{ color: '#b00', whiteSpace: 'pre-wrap' }}>{error}</div>
        </Card>
      )}

      {extraction && (
        <Card>
          <h3 style={{ marginTop: 0 }}>Extraction (JSON)</h3>
          <CodeBlock obj={extraction} />
        </Card>
      )}

      <h2 style={{ marginTop: 18 }}>Search results</h2>

      {grouped.length === 0 && (
        <div style={{ color: '#666' }}>No results yet. Build the index, then search.</div>
      )}

      {grouped.map(([paperId, arr]) => (
        <Card key={paperId}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>{paperId}</div>
          {arr.slice(0, 6).map((h) => (
            <div key={h.chunk_id} style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', fontSize: 12, color: '#555' }}>
                <span>score: {h.score.toFixed(3)}</span>
                {h.source && <span>source: {h.source}</span>}
                {h.year && <span>year: {h.year}</span>}
                {h.section && <span>section: {h.section}</span>}
                <span>chunk: {h.chunk_id}</span>
              </div>
              <div style={{ marginTop: 6, lineHeight: 1.35, whiteSpace: 'pre-wrap' }}>
                {h.text}
              </div>
              <hr style={{ border: 0, borderTop: '1px solid #eee', marginTop: 10 }} />
            </div>
          ))}
        </Card>
      ))}
    </div>
  )
}
