import React, { useState, useEffect } from 'react';
import { X, Download, Copy, Check, FileText } from 'lucide-react';

export default function ReportModal({ isOpen, onClose }) {
  const [reportMarkdown, setReportMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch('/api/export/bundle')
        .then(res => res.json())
        .then(data => {
          setReportMarkdown(data.markdown || 'No report generated yet.');
          setLoading(false);
        })
        .catch(err => {
          setReportMarkdown(`Error loading bundle: ${err.message}`);
          setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(reportMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([reportMarkdown], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `VERIMINION_CORTENSOR_HACKATHON_5_REPORT_${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-tactical-900 border border-tactical-border rounded-lg max-w-3xl w-full p-5 shadow-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between mb-3 border-b border-tactical-border pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <h3 className="font-mono font-bold text-sm text-white">
              Cortensor Hackathon #5 — OpenMinion 0.1 Submission Bundle
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Markdown viewer */}
        <div className="flex-1 bg-tactical-950 border border-tactical-border rounded p-4 font-mono text-xs overflow-y-auto whitespace-pre-wrap text-slate-300 leading-relaxed">
          {loading ? 'Generating dynamic bundle from SQLite audit ledger...' : reportMarkdown}
        </div>

        {/* Footer Actions */}
        <div className="mt-4 flex items-center justify-between border-t border-tactical-border pt-3">
          <span className="text-xs font-mono text-slate-400">
            Export includes live memory snapshots, dead-end signatures & X-Ray metrics
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-tactical-800 hover:bg-tactical-700 text-slate-200 border border-tactical-border rounded font-mono text-xs flex items-center gap-1.5 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Markdown'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-xs font-semibold flex items-center gap-1.5 transition shadow"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .md</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
