import React from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Settings, 
  Download, 
  Play, 
  Radio, 
  Sparkles 
} from 'lucide-react';

export default function TopBar({
  systemStatus,
  scenarios,
  selectedScenario,
  onSelectScenario,
  onRun,
  isRunning,
  activeSessionId,
  onOpenModelConfig,
  onOpenReport
}) {
  return (
    <header className="border-b border-tactical-border bg-tactical-900/90 backdrop-blur px-4 py-2.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40">
      {/* Brand & Connection Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-9 h-9 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 shadow-sm shadow-cyan-500/20">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold tracking-wider text-base text-white">VERIMINION</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-400">
              CORTENSOR HACKATHON #5
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Portal: <strong className="text-slate-200">Ready</strong>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              SDK: <strong className="text-cyan-300">v{systemStatus?.openminion_sdk_version || '0.1.9'}</strong>
            </span>
            <span>•</span>
            <span className="text-slate-500">
              Session: <strong className="text-slate-300">{activeSessionId ? activeSessionId.slice(0, 12) : 'STANDBY'}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* 4 1-Click Scenario Presets */}
      <div className="flex items-center gap-1.5 bg-tactical-950 p-1 rounded-lg border border-tactical-border/70 overflow-x-auto">
        {scenarios.map((sc, idx) => {
          const isSelected = selectedScenario?.id === sc.id;
          return (
            <button
              key={sc.id}
              onClick={() => onSelectScenario(sc)}
              className={`px-3 py-1.5 text-xs font-mono rounded flex items-center gap-1.5 transition-all whitespace-nowrap ${
                isSelected
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm shadow-cyan-500/20 font-medium'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-tactical-850'
              }`}
              title={sc.description}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-cyan-400' : 'bg-slate-600'}`} />
              <span>{`P${idx + 1}: ${sc.badge}`}</span>
            </button>
          );
        })}
      </div>

      {/* Global Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenModelConfig}
          className="px-2.5 py-1.5 text-xs font-mono text-slate-300 hover:text-white bg-tactical-850 hover:bg-tactical-800 border border-tactical-border rounded flex items-center gap-1.5 transition"
          title="Configure Cortensor Portal & LLM Endpoints"
        >
          <Settings className="w-3.5 h-3.5 text-slate-400" />
          <span>Models</span>
        </button>

        <button
          onClick={onOpenReport}
          className="px-2.5 py-1.5 text-xs font-mono text-cyan-300 hover:text-cyan-200 bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-500/40 rounded flex items-center gap-1.5 transition"
          title="Generate Hackathon QA & Diagnostic Bundle"
        >
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export Bundle</span>
        </button>

        <button
          onClick={onRun}
          disabled={isRunning}
          className={`px-4 py-1.5 text-xs font-mono font-semibold rounded flex items-center gap-2 transition shadow-lg ${
            isRunning
              ? 'bg-slate-700 text-slate-400 cursor-not-allowed border border-slate-600'
              : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 border border-emerald-400 shadow-emerald-500/20 active:scale-95'
          }`}
        >
          {isRunning ? (
            <>
              <Activity className="w-4 h-4 animate-spin text-slate-300" />
              <span>AUDITING...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-slate-950" />
              <span>LAUNCH AUDIT</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
}
