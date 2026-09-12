import React from 'react';

export default function Watermark() {
  return (
    <aside aria-label="Author Watermark" className="architect-watermark">
      <div className="watermark-inner">
        <span className="watermark-beacon" aria-hidden="true"></span>
        <div className="watermark-content">
          <span className="watermark-label">Built by</span>
          <span className="watermark-author">Divyansh Mishra</span>
        </div>
        <div className="watermark-tag">Project</div>
      </div>
    </aside>
  );
}
