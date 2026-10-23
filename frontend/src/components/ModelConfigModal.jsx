import React, { useState } from 'react';
import { X, Server, Key, Globe, Check } from 'lucide-react';

export default function ModelConfigModal({ isOpen, onClose }) {
  const [portalUrl, setPortalUrl] = useState('https://portal.cortensor.network');
  const [cortensorKey, setCortensorKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [mode, setMode] = useState('deterministic');
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-tactical-900 border border-tactical-border rounded-lg max-w-lg w-full p-5 shadow-2xl">
        <div className="flex items-center justify-between mb-4 border-b border-tactical-border pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            <h3 className="font-mono font-bold text-sm text-white">Cortensor Portal & Multi-Provider Config</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4 font-mono text-xs">
          {/* Provider Mode Selector */}
          <div>
            <label className="block text-slate-400 mb-1.5 font-semibold">Active Execution Profile</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setMode('deterministic')}
                className={`p-2.5 rounded border text-left transition ${
                  mode === 'deterministic'
                    ? 'bg-cyan-950/60 border-cyan-500 text-cyan-300'
                    : 'bg-tactical-950 border-tactical-border text-slate-400 hover:border-slate-600'
                }`}
              >
                <div className="font-bold">Deterministic Engine (Judge Mode)</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Zero API keys needed, 100% reproducible AST & SymPy tool audit</div>
              </button>
              <button
                type="button"
                onClick={() => setMode('live')}
                className={`p-2.5 rounded border text-left transition ${
                  mode === 'live'
                    ? 'bg-cyan-950/60 border-cyan-500 text-cyan-300'
                    : 'bg-tactical-950 border-tactical-border text-slate-400 hover:border-slate-600'
                }`}
              >
                <div className="font-bold">Live Inference Endpoints</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Route prompts through live Cortensor Portal / OpenAI / Gemini</div>
              </button>
            </div>
          </div>

          {/* Cortensor Portal URL */}
          <div>
            <label className="block text-slate-400 mb-1">Cortensor Portal API Gateway</label>
            <div className="flex items-center gap-2 bg-tactical-950 border border-tactical-border rounded px-3 py-1.5">
              <Globe className="w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={portalUrl}
                onChange={(e) => setPortalUrl(e.target.value)}
                className="bg-transparent flex-1 text-slate-200 focus:outline-none"
              />
            </div>
          </div>

          {/* Cortensor API Key */}
          <div>
            <label className="block text-slate-400 mb-1">Cortensor Portal API Key (Optional)</label>
            <div className="flex items-center gap-2 bg-tactical-950 border border-tactical-border rounded px-3 py-1.5">
              <Key className="w-4 h-4 text-slate-500" />
              <input
                type="password"
                placeholder="cor_live_..."
                value={cortensorKey}
                onChange={(e) => setCortensorKey(e.target.value)}
                className="bg-transparent flex-1 text-slate-200 focus:outline-none"
              />
            </div>
          </div>

          {/* OpenAI Key */}
          <div>
            <label className="block text-slate-400 mb-1">OpenAI API Key (Optional)</label>
            <div className="flex items-center gap-2 bg-tactical-950 border border-tactical-border rounded px-3 py-1.5">
              <Key className="w-4 h-4 text-slate-500" />
              <input
                type="password"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="bg-transparent flex-1 text-slate-200 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2 border-t border-tactical-border pt-3">
          <button
            onClick={onClose}
            className="px-3 py-1.5 bg-tactical-850 hover:bg-tactical-800 text-slate-300 rounded font-mono text-xs"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-xs font-semibold flex items-center gap-1.5 transition"
          >
            {saved ? (
              <>
                <Check className="w-3.5 h-3.5 text-white" />
                <span>Saved!</span>
              </>
            ) : (
              <span>Save & Apply</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
