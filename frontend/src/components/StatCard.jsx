import React from 'react';

export default function StatCard({ label, value, placeholderTag, subtext, iconText }) {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <span>{label}</span>
        {iconText && <div className="stat-icon-badge">{iconText}</div>}
      </div>

      <div className="stat-value">{value}</div>

      {placeholderTag && (
        <div className="mock-tag">{placeholderTag}</div>
      )}

      {subtext && <div className="stat-footer">{subtext}</div>}
    </div>
  );
}
