import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  Terminal, 
  Hash, 
  Send, 
  AlertTriangle,
  Play,
  RotateCcw,
  Code2,
  FileText,
  Clock
} from 'lucide-react';

export default function CenterPanel({
  selectedScenario,
  customPrompt,
  onChangePrompt,
  onRun,
  isRunning,
  nodeOutputs,
  verificationResults,
  airlockData,
  onResolveAirlock,
  agentLogs,
  consensusVerdict
}) {
  const [operatorNote, setOperatorNote] = useState('');

  return (
    <main className="flex-1 flex flex-col h-[calc(100vh-60px)] bg-tactical-950 overflow-hidden text-slate-200">
      {/* 1. SCENARIO HEADER & PROMPT BAR */}
      <div className="p-3 border-b border-tactical-border bg-tactical-900/60">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="font-mono text-xs text-cyan-400 font-semibold uppercase tracking-wider">
              {selectedScenario?.title || 'Proof-of-Cognition Verification Arena'}
            </div>
            <div className="text-xs text-slate-400">
              {selectedScenario?.description}
            </div>
          </div>
          {consensusVerdict && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-tactical-850 border border-tactical-border text-xs font-mono">
              <span className="text-slate-400">Verdict:</span>
              <span className="font-bold text-emerald-400">{consensusVerdict}</span>
            </div>
          )}
        </div>

        {/* Custom Prompt Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={customPrompt}
            onChange={(e) => onChangePrompt(e.target.value)}
            placeholder="Enter high-stakes verification prompt..."
            className="flex-1 bg-tactical-950 border border-tactical-border rounded px-3 py-1.5 text-xs font-mono text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={onRun}
            disabled={isRunning}
            className="px-3 py-1.5 bg-tactical-800 hover:bg-tactical-700 text-slate-200 border border-tactical-border rounded font-mono text-xs flex items-center gap-1.5 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 text-cyan-400" />
            <span>Audit</span>
          </button>
        </div>
      </div>

      {/* 2. INTERACTIVE PERMISSION AIRLOCK BANNER / MODAL */}
      {airlockData && (
        <div className="m-3 p-3.5 rounded-lg bg-red-950/40 border border-red-500/70 shadow-lg shadow-red-950/50 animate-airlock">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-2.5">
              <div className="p-2 rounded bg-red-900/40 border border-red-500/50 text-red-400">
                <ShieldAlert className="w-5 h-5 text-red-400 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-xs text-red-400 tracking-wider">
                    CRITICAL: PERMISSION AIRLOCK ENGAGED [PENDING_APPROVAL]
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-red-900/60 text-red-200 border border-red-500/40">
                    permissions / policy
                  </span>
                </div>
                <div className="text-xs text-slate-300 mt-1">
                  Target: <strong className="text-red-300 font-mono">[{airlockData.target_node}]</strong> • Proposed Mutation: <span className="font-mono text-amber-300">{airlockData.action_type}</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5 font-mono">
                  Evidence: {airlockData.details}
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono mt-1">
                  <Hash className="w-3 h-3 text-slate-600" />
                  <span>SHA-256 Mutation Hash: </span>
                  <code className="text-slate-400">{airlockData.mutation_hash}</code>
                </div>
              </div>
            </div>

            {/* Operator Actions */}
            <div className="flex flex-col gap-1.5 min-w-[200px]">
              <input 
                type="text"
                placeholder="Optional operator note..."
                value={operatorNote}
                onChange={(e) => setOperatorNote(e.target.value)}
                className="bg-black/50 border border-red-900/60 rounded px-2 py-1 text-[11px] font-mono text-slate-300 focus:outline-none focus:border-red-500"
              />
              <div className="flex gap-1.5">
                <button
                  onClick={() => onResolveAirlock(airlockData.action_id, 'APPROVE', operatorNote)}
                  className="flex-1 px-2.5 py-1.5 bg-red-600 hover:bg-red-500 text-white font-mono text-xs font-bold rounded shadow transition flex items-center justify-center gap-1"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>APPROVE QUARANTINE</span>
                </button>
                <button
                  onClick={() => onResolveAirlock(airlockData.action_id, 'REJECT', operatorNote)}
                  className="px-2.5 py-1.5 bg-tactical-800 hover:bg-tactical-700 text-slate-300 font-mono text-xs rounded border border-tactical-border transition"
                >
                  OVERRIDE
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. SIDE-BY-SIDE CONSENSUS ARENA */}
      <div className="p-3 border-b border-tactical-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 font-mono text-xs uppercase font-semibold text-slate-300">
            <Code2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Decentralized Consensus Arena (Node Output Comparison)</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            models / tools / skills
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2.5">
          {['node-alpha', 'node-beta', 'node-gamma'].map(nid => {
            const out = nodeOutputs[nid];
            const ver = verificationResults[nid];
            const displayName = nid === 'node-alpha' ? 'Node-Alpha (Cortensor Primary)' : nid === 'node-beta' ? 'Node-Beta (Gemma4 Fast Tier)' : 'Node-Gamma (Adversarial Drift)';

            return (
              <div 
                key={nid}
                className={`p-2.5 rounded border flex flex-col justify-between h-48 transition-all ${
                  ver
                    ? ver.is_valid
                      ? 'bg-tactical-900/80 border-emerald-500/40'
                      : 'bg-red-950/20 border-red-500/50'
                    : 'bg-tactical-900 border-tactical-border'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono font-semibold text-xs text-slate-200 truncate max-w-[160px]">
                      {displayName}
                    </span>
                    {out && (
                      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                        <Clock className="w-2.5 h-2.5 text-slate-500" />
                        {out.latency_ms}ms
                      </span>
                    )}
                  </div>

                  {/* Verification Badge */}
                  {ver && (
                    <div className="mb-1.5">
                      {ver.is_valid ? (
                        <div className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/50 text-emerald-400 font-semibold">
                          <CheckCircle className="w-3 h-3 text-emerald-400" />
                          <span>VERIFIED BY AST/MATH TOOL</span>
                        </div>
                      ) : (
                        <div className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/80 border border-red-500/50 text-red-400 font-semibold">
                          <XCircle className="w-3 h-3 text-red-400" />
                          <span>BYZANTINE DRIFT DETECTED</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Code / Output Container */}
                  <div className="bg-tactical-950 p-2 rounded border border-tactical-border/70 font-mono text-[11px] text-slate-300 max-h-24 overflow-y-auto whitespace-pre-wrap">
                    {out ? out.content : <span className="text-slate-600 italic">Waiting for node response...</span>}
                  </div>
                </div>

                {ver && ver.divergence_reason && (
                  <div className="text-[10px] font-mono text-red-400 truncate pt-1 border-t border-red-900/40">
                    Reason: {ver.divergence_reason}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. REAL-TIME EXECUTION STREAM (TERMINAL AUDIT LOG) */}
      <div className="p-3 flex-1 flex flex-col overflow-hidden bg-tactical-950">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5 font-mono text-xs uppercase font-semibold text-slate-300">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            <span>Real-Time SDK Execution & Verification Stream</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            execution / diagnostics / trace
          </span>
        </div>

        <div className="flex-1 bg-[#04070a] border border-tactical-border/80 rounded p-2.5 font-mono text-xs overflow-y-auto space-y-1.5 shadow-inner">
          {agentLogs && agentLogs.length > 0 ? (
            agentLogs.map((log, idx) => (
              <div key={idx} className="flex items-start gap-2 text-slate-300 leading-relaxed">
                <span className="text-slate-600 select-none text-[10px]">
                  [{new Date(log.timestamp * 1000).toLocaleTimeString()}]
                </span>
                <span className={`text-[10px] uppercase px-1 py-0.2 rounded font-bold ${
                  log.building_block === 'permissions' ? 'bg-red-950 text-red-400 border border-red-900' :
                  log.building_block === 'skills' ? 'bg-amber-950 text-amber-400 border border-amber-900' :
                  log.building_block === 'tools' ? 'bg-cyan-950 text-cyan-400 border border-cyan-900' :
                  'bg-tactical-850 text-slate-400 border border-slate-700'
                }`}>
                  {log.building_block || 'SYS'}
                </span>
                <span className="text-slate-200">
                  {log.agent_role ? <strong className="text-cyan-300">{log.agent_role}: </strong> : null}
                  {log.message || log.type}
                </span>
              </div>
            ))
          ) : (
            <div className="text-slate-600 italic">No active audit logs. Select a scenario preset and click "LAUNCH AUDIT" to stream live events.</div>
          )}
        </div>
      </div>
    </main>
  );
}
