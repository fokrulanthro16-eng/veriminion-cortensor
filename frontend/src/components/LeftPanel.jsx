import React from 'react';
import { 
  GitBranch, 
  Database, 
  History, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  AlertTriangle,
  Server,
  Zap,
  ArrowRight
} from 'lucide-react';

export default function LeftPanel({
  tasks,
  nodes,
  sessions,
  activeSessionId,
  onSelectSession,
  deadEnds
}) {
  return (
    <aside className="w-80 border-r border-tactical-border bg-tactical-950 flex flex-col h-[calc(100vh-60px)] overflow-hidden text-xs">
      {/* 1. MISSION DAG & DELEGATION */}
      <div className="p-3 border-b border-tactical-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 font-mono uppercase font-semibold text-slate-300">
            <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
            <span>Mission DAG & A2A Flow</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-tactical-850 border border-tactical-border text-slate-400">
            tasks / delegation
          </span>
        </div>

        {/* Dynamic DAG Tasks */}
        <div className="space-y-1.5 mb-3">
          {tasks && tasks.length > 0 ? (
            tasks.map((t, idx) => (
              <div 
                key={t.id} 
                className={`p-2 rounded border flex items-center justify-between transition-colors ${
                  t.status === 'DONE' 
                    ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' 
                    : t.status === 'IN_PROGRESS'
                    ? 'bg-cyan-950/30 border-cyan-500/50 text-cyan-200 animate-pulse'
                    : 'bg-tactical-900 border-tactical-border text-slate-400'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-slate-500">#{idx + 1}</span>
                  <span className="font-medium truncate max-w-[170px]">{t.name}</span>
                </div>
                <span className="font-mono text-[9px] uppercase px-1 py-0.5 rounded bg-black/40">
                  {t.status}
                </span>
              </div>
            ))
          ) : (
            <div className="text-slate-500 italic p-2 text-center border border-dashed border-tactical-border rounded">
              Ready for workflow launch
            </div>
          )}
        </div>

        {/* Visual Multi-Minion Delegation Hierarchy */}
        <div className="p-2 rounded bg-tactical-900/60 border border-tactical-border/70 space-y-1.5">
          <div className="text-[11px] font-mono text-cyan-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            Lead Orchestrator Minion
          </div>
          <div className="pl-3 border-l border-slate-700/60 space-y-1 text-[10px] font-mono text-slate-400">
            <div className="flex items-center gap-1">
              <ArrowRight className="w-2.5 h-2.5 text-slate-500" />
              <span>Node-Alpha (Cortensor Primary)</span>
            </div>
            <div className="flex items-center gap-1">
              <ArrowRight className="w-2.5 h-2.5 text-slate-500" />
              <span>Node-Beta (Gemma4 Fast Tier)</span>
            </div>
            <div className="flex items-center gap-1">
              <ArrowRight className="w-2.5 h-2.5 text-slate-500" />
              <span>Node-Gamma (Adversarial Drift)</span>
            </div>
          </div>
          <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-1 pt-1 border-t border-tactical-border/50">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Auditor Minion (AST & SymPy Verifier)
          </div>
        </div>
      </div>

      {/* 2. NODE REPUTATION MEMORY LEDGER */}
      <div className="p-3 border-b border-tactical-border flex-1 overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 font-mono uppercase font-semibold text-slate-300">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>Node Reputation Ledger</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-tactical-850 border border-tactical-border text-slate-400">
            memory (sqlite)
          </span>
        </div>

        <div className="space-y-2">
          {nodes.map(n => {
            const isQuarantined = n.status === 'QUARANTINED';
            const isDegraded = n.status === 'DEGRADED';
            return (
              <div 
                key={n.node_id}
                className={`p-2.5 rounded border transition-all ${
                  isQuarantined
                    ? 'bg-crimson/10 border-red-500/40 text-red-300'
                    : isDegraded
                    ? 'bg-amber-950/20 border-amber-500/40 text-amber-300'
                    : 'bg-tactical-900 border-tactical-border hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="font-mono font-semibold text-slate-200 truncate max-w-[170px]">
                    {n.display_name}
                  </div>
                  <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                    isQuarantined 
                      ? 'bg-red-950 text-red-400 border border-red-500/40' 
                      : isDegraded
                      ? 'bg-amber-950 text-amber-400 border border-amber-500/40'
                      : 'bg-emerald-950 text-emerald-400 border border-emerald-500/40'
                  }`}>
                    {n.status}
                  </span>
                </div>

                {/* Trust Score Bar */}
                <div className="space-y-1 mb-2">
                  <div className="flex justify-between text-[10px] font-mono">
                    <span className="text-slate-400">Trust Score</span>
                    <strong className="text-slate-200">{n.trust_score}%</strong>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${
                        n.trust_score > 85 ? 'bg-emerald-500' : n.trust_score > 60 ? 'bg-amber-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(5, n.trust_score))}%` }}
                    />
                  </div>
                </div>

                {/* Node Metrics */}
                <div className="grid grid-cols-3 gap-1 text-[10px] font-mono text-slate-400 text-center">
                  <div className="p-1 rounded bg-tactical-950 border border-tactical-border">
                    <div className="text-slate-500 text-[8px]">TOTAL</div>
                    <div className="text-slate-200 font-semibold">{n.total_runs}</div>
                  </div>
                  <div className="p-1 rounded bg-tactical-950 border border-tactical-border">
                    <div className="text-slate-500 text-[8px]">DRIFT</div>
                    <div className={`font-semibold ${n.drift_count > 0 ? 'text-red-400' : 'text-slate-200'}`}>
                      {n.drift_count}
                    </div>
                  </div>
                  <div className="p-1 rounded bg-tactical-950 border border-tactical-border">
                    <div className="text-slate-500 text-[8px]">LATENCY</div>
                    <div className="text-slate-200 font-semibold">{n.avg_latency_ms}ms</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Semantic Dead-End Memory Box */}
        {deadEnds && deadEnds.length > 0 && (
          <div className="mt-3 p-2 rounded bg-red-950/20 border border-red-500/30">
            <div className="flex items-center gap-1.5 text-red-400 font-mono font-semibold mb-1">
              <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
              <span>Semantic Dead-Ends ({deadEnds.length})</span>
            </div>
            <div className="space-y-1 text-[10px] font-mono text-slate-400">
              {deadEnds.slice(0, 3).map((de, idx) => (
                <div key={idx} className="p-1 rounded bg-black/40 border border-red-900/40 truncate">
                  <span className="text-red-400">[{de.failure_signature}]</span> {de.evidence}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. PERSISTENT SESSIONS */}
      <div className="p-3 border-t border-tactical-border bg-tactical-900/40">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 font-mono uppercase font-semibold text-slate-300">
            <History className="w-3.5 h-3.5 text-cyan-400" />
            <span>Persistent Sessions</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-tactical-850 border border-tactical-border text-slate-400">
            sessions
          </span>
        </div>

        <div className="space-y-1 max-h-32 overflow-y-auto">
          {sessions && sessions.length > 0 ? (
            sessions.slice(0, 8).map(s => (
              <button
                key={s.session_id}
                onClick={() => onSelectSession(s.session_id)}
                className={`w-full text-left p-1.5 rounded font-mono text-[10px] border flex items-center justify-between transition ${
                  activeSessionId === s.session_id
                    ? 'bg-cyan-950/60 border-cyan-500/50 text-cyan-300 font-medium'
                    : 'bg-tactical-950 border-tactical-border text-slate-400 hover:text-slate-200'
                }`}
              >
                <span className="truncate max-w-[170px]">{s.session_id}</span>
                <span className="text-[9px] text-slate-500">{s.status}</span>
              </button>
            ))
          ) : (
            <div className="text-slate-500 italic p-1 text-center">No persistent runs yet</div>
          )}
        </div>
      </div>
    </aside>
  );
}
