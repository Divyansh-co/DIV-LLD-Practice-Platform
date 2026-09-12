import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#0d1117',
    primaryColor: '#161b22',
    primaryTextColor: '#e6edf3',
    primaryBorderColor: '#30363d',
    lineColor: '#58a6ff',
    secondaryColor: '#21262d',
    tertiaryColor: '#161b22',
  },
  securityLevel: 'loose',
});

export default function MermaidRenderer({ chart }) {
  const [svgContent, setSvgContent] = useState('');
  const [renderError, setRenderError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function renderChart() {
      if (!chart || !chart.trim()) {
        setSvgContent('');
        setRenderError(null);
        return;
      }

      try {
        const uniqueId = `mermaid-svg-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        const { svg } = await mermaid.render(uniqueId, chart.trim());
        if (isMounted) {
          setSvgContent(svg);
          setRenderError(null);
        }
      } catch (err) {
        if (isMounted) {
          setRenderError('Could not render diagram. Please check your Mermaid classDiagram syntax.');
          setSvgContent('');
        }
      }
    }

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  if (!chart || !chart.trim()) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
        No diagram written yet. Enter Mermaid classDiagram code to see it rendered.
      </div>
    );
  }

  if (renderError) {
    return (
      <div
        style={{
          padding: '1rem',
          margin: '1rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid var(--status-failed)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--status-failed)',
          fontSize: '0.85rem',
        }}
      >
        {renderError}
      </div>
    );
  }

  return (
    <div
      style={{
        width: '100%',
        overflow: 'auto',
        display: 'flex',
        justifyContent: 'center',
        padding: '1rem',
      }}
      dangerouslySetInnerHTML={{ __html: svgContent }}
    />
  );
}
