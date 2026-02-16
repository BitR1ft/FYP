'use client';

import { useCallback } from 'react';
import { ImageDown, FileJson, FileSpreadsheet } from 'lucide-react';
import type { GraphNode, GraphRelationship } from '@/lib/api';

interface GraphExportProps {
  graphRef: React.RefObject<any>;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

export default function GraphExport({ graphRef, nodes, relationships }: GraphExportProps) {
  const exportPNG = useCallback(() => {
    const fg = graphRef.current;
    if (!fg) return;
    // Try the ForceGraph2D canvas accessor first, then query the DOM
    const canvas =
      (fg.canvas?.() as HTMLCanvasElement | undefined) ??
      document.querySelector<HTMLCanvasElement>('.force-graph-container canvas');
    if (!canvas) return;
    downloadDataURL(canvas.toDataURL('image/png'), 'attack-graph.png');
  }, [graphRef]);

  const exportJSON = useCallback(() => {
    const data = JSON.stringify({ nodes, relationships }, null, 2);
    downloadBlob(data, 'attack-graph.json', 'application/json');
  }, [nodes, relationships]);

  const exportCSV = useCallback(() => {
    if (nodes.length === 0) return;
    const allKeys = new Set<string>();
    allKeys.add('id');
    allKeys.add('labels');
    for (const node of nodes) {
      for (const key of Object.keys(node.properties)) {
        allKeys.add(key);
      }
    }
    const headers = Array.from(allKeys);
    const rows = nodes.map((node) => {
      return headers.map((h) => {
        if (h === 'id') return csvEscape(node.id);
        if (h === 'labels') return csvEscape(node.labels.join(';'));
        const val = node.properties[h];
        return val != null ? csvEscape(String(val)) : '';
      }).join(',');
    });
    const csv = [headers.join(','), ...rows].join('\n');
    downloadBlob(csv, 'attack-graph-nodes.csv', 'text/csv');
  }, [nodes]);

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={exportPNG}
        title="Export as PNG"
        className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
      >
        <ImageDown className="h-4 w-4" />
      </button>
      <button
        onClick={exportJSON}
        title="Export as JSON"
        className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
      >
        <FileJson className="h-4 w-4" />
      </button>
      <button
        onClick={exportCSV}
        title="Export as CSV"
        className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
      >
        <FileSpreadsheet className="h-4 w-4" />
      </button>
    </div>
  );
}

function csvEscape(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function downloadDataURL(dataURL: string, filename: string) {
  const a = document.createElement('a');
  a.href = dataURL;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function downloadBlob(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
