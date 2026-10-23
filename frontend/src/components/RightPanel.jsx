import React, { useState } from 'react';
import { 
  Activity, 
  Cpu, 
  Wrench, 
  Lock, 
  Clock, 
  Database, 
  BookOpen, 
  CheckSquare, 
  Users, 
  Gauge,
  Sparkles,
  Info,
  X
} from 'lucide-react';

const BLOCK_METADATA = [
  { id: 'execution', name: '1. Execution', icon: Activity, desc: 'Deterministic step-by-step agent loop, state transitions & trace capture' },
  { id: 'models', name: '2. Models', icon: Cpu, desc: 'Multi-provider router: Cortensor Portal, Gemma4, OpenAI, Gemini & Deterministic engine' },
  { id: 'tools', name: '3. Tools', icon: Wrench, desc: 'AST Syntax Auditor, SymPy Math Verifier, Sandboxed Code Runner, SLA Tool' },
  { id: 'permissions', name: '4. Permissions', icon: Lock, desc: 'Cryptographic Human-in-the-Loop Airlock (SHA-256 mutation hash approval gate)' },
  { id: 'sessions', name: '5. Sessions', icon: Clock, desc: 'Multi-turn persistent session lifecycle management with replayable SQLite snapshots' },
  { id: 'memory', name: '6. Memory', icon: Database, desc: 'Episodic Node Trust Ledger + Semantic Dead-End Memory for quarantined signatures' },
  { id: 'skills', name: '7. Skills', icon: BookOpen, desc: 'Composable packs: AdversarialCodeAudit, QuantitativeProof, ByzantineConsensus, Telemetry' },
  { id: 'tasks', name: '8. Tasks', icon: CheckSquare, desc: 'Structured DAG task decomposition with dependency tracking & verifiable criteria' },
  { id: 'delegation', name: '9. Delegation', icon: Users, desc: 'Lead Orchestrator Minion dynamically delegating to Worker & Auditor Minions' },
  { id: 'diagnostics', name: '10. Diagnostics', icon: Gauge, desc: 'Real-time SDK X-Ray engine capturing ms latency, tokens/sec & rough-edge detection' }
];

export default function RightPanel({ xrayStats, activeBlock }) {
  const [inspectBlock, setInspectBlock] = useState(null);

  return (
    <aside className="w-84 border-l border-tactical-border bg-tactical-950 flex flex-col h-[calc(100vh-60px)] overflow-hidden text-xs">
      {/* Header */}
      <div className="p-3 border-b border-tactical-border flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-mono uppercase font-semibold text-slate-300">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>OpenMinion 0.1 X-Ray Studio</span>
        </div>
        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40">
          10/10 BLOCKS
        </span>
      </div>

      {/* 10-Card Matrix */}
      <div className="p-3 flex-1 overflow-y-auto space-y-2">
        {BLOCK_METADATA.map((block) => {
          const stats = (xrayStats && xrayStats[block.id]) || { invocations: 0, avg_duration_ms: 0.0, status: 'READY' };
          const isActive = activeBlock === block.id;
          const Icon = block.icon;

          return (
            <div
              key={block.id}
              onClick={() => setInspectBlock({ ...block, stats })}
              className={`p-2.5 rounded border cursor-pointer transition-all ${
                isActive
                  ? 'bg-cyan-950/40 border-cyan-400 shadow-md shadow-cyan-500/20 pulse-glow'
                  : 'bg-tactical-900 border-tactical-border hover:border-slate-600 hover:bg-tactical-850'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1.5 font-mono font-semibold text-slate-200">
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{block.name}</span>
                </div>
                <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-bold ${
                  stats.invocations > 0 ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                }`}>
                  {stats.invocations > 0 ? `${stats.invocations} RUNS` : 'READY'}
                </span>
              </div>

              <div className="text-[10px] text-slate-400 line-clamp-1 mb-2">
                {block.desc}
              </div>

              <div className="flex items-center justify-between text-[10px] font-mono pt-1.5 border-t border-tactical-border/50 text-slate-400">
                <span>Avg Latency:</span>
                <span className="text-slate-200 font-semibold">{stats.avg_duration_ms} ms</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Block Inspector Modal / Flyout */}
      {inspectBlock && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-tactical-900 border border-tactical-border rounded-lg max-w-lg w-full p-4 shadow-2xl">
            <div className="flex items-center justify-between mb-3 border-b border-tactical-border pb-2">
              <div className="flex items-center gap-2">
                <inspectBlock.icon className="w-5 h-5 text-cyan-400" />
                <h3 className="font-mono font-bold text-sm text-white">{inspectBlock.name} X-Ray</h3>
              </div>
              <button 
                onClick={() => setInspectBlock(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <span className="text-slate-500">Architecture Description:</span>
                <p className="text-slate-300 mt-0.5">{inspectBlock.desc}</p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div className="p-2 rounded bg-tactical-950 border border-tactical-border">
                  <div className="text-slate-500 text-[10px]">TOTAL INVOCATIONS</div>
                  <div className="text-base font-bold text-cyan-400">{inspectBlock.stats.invocations}</div>
                </div>
                <div className="p-2 rounded bg-tactical-950 border border-tactical-border">
                  <div className="text-slate-500 text-[10px]">AVG LATENCY</div>
                  <div className="text-base font-bold text-emerald-400">{inspectBlock.stats.avg_duration_ms} ms</div>
                </div>
              </div>

              <div className="p-2 rounded bg-cyan-950/30 border border-cyan-500/30 text-cyan-300 text-[11px]">
                <div className="font-bold flex items-center gap-1 mb-1">
                  <Info className="w-3.5 h-3.5" />
                  <span>OpenMinion 0.1 SDK Telemetry Hook:</span>
                </div>
                <p className="text-slate-300 text-[10px] leading-relaxed">
                  Instrumented via <code>openminion.modules.{inspectBlock.id}</code>. Captures execution timings, state transitions, and feeds the Cortensor Proof-of-Cognition consensus engine.
                </p>
              </div>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setInspectBlock(null)}
                className="px-3 py-1.5 bg-tactical-800 hover:bg-tactical-700 text-slate-200 rounded font-mono text-xs"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
