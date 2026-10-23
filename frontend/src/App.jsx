import React, { useState, useEffect, useRef } from 'react';
import TopBar from './components/TopBar';
import LeftPanel from './components/LeftPanel';
import CenterPanel from './components/CenterPanel';
import RightPanel from './components/RightPanel';
import ModelConfigModal from './components/ModelConfigModal';
import ReportModal from './components/ReportModal';

export default function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [customPrompt, setCustomPrompt] = useState('');
  
  const [tasks, setTasks] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [deadEnds, setDeadEnds] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState('');

  const [isRunning, setIsRunning] = useState(false);
  const [nodeOutputs, setNodeOutputs] = useState({});
  const [verificationResults, setVerificationResults] = useState({});
  const [airlockData, setAirlockData] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);
  const [consensusVerdict, setConsensusVerdict] = useState('');

  const [xrayStats, setXrayStats] = useState({});
  const [activeBlock, setActiveBlock] = useState(null);

  const [isModelConfigOpen, setIsModelConfigOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);

  const eventSourceRef = useRef(null);

  // Initial Data Fetch
  useEffect(() => {
    fetchStatus();
    fetchScenarios();
    fetchNodes();
    fetchSessions();
    fetchDeadEnds();
    fetchXray();
  }, []);

  const fetchStatus = () => {
    fetch('/api/status').then(r => r.json()).then(setSystemStatus).catch(console.error);
  };

  const fetchScenarios = () => {
    fetch('/api/scenarios')
      .then(r => r.json())
      .then(data => {
        setScenarios(data);
        if (data.length > 0 && !selectedScenario) {
          setSelectedScenario(data[0]);
          setCustomPrompt(data[0].default_prompt);
        }
      })
      .catch(console.error);
  };

  const fetchNodes = () => {
    fetch('/api/nodes').then(r => r.json()).then(setNodes).catch(console.error);
  };

  const fetchSessions = () => {
    fetch('/api/sessions').then(r => r.json()).then(setSessions).catch(console.error);
  };

  const fetchDeadEnds = () => {
    fetch('/api/dead_ends').then(r => r.json()).then(setDeadEnds).catch(console.error);
  };

  const fetchXray = () => {
    fetch('/api/diagnostics/xray').then(r => r.json()).then(setXrayStats).catch(console.error);
  };

  // Scenario switch handler
  const handleSelectScenario = (sc) => {
    setSelectedScenario(sc);
    setCustomPrompt(sc.default_prompt);
    setNodeOutputs({});
    setVerificationResults({});
    setAirlockData(null);
    setConsensusVerdict('');
  };

  // Session selector handler (load snapshot)
  const handleSelectSession = (sid) => {
    fetch(`/api/sessions/${sid}`)
      .then(r => r.json())
      .then(sess => {
        setActiveSessionId(sess.session_id);
        setCustomPrompt(sess.prompt);
        const matching = scenarios.find(s => s.id === sess.scenario_id);
        if (matching) setSelectedScenario(matching);

        if (sess.state_snapshot) {
          const snap = sess.state_snapshot;
          if (snap.evaluations) {
            const vMap = {};
            snap.evaluations.forEach(ev => { vMap[ev.node_id] = ev; });
            setVerificationResults(vMap);
          }
          if (snap.consensus) {
            setConsensusVerdict(snap.consensus.consensus_verdict);
          }
          if (snap.airlock) {
            setAirlockData(snap.airlock);
          }
        }
      })
      .catch(console.error);
  };

  // Launch Proof-of-Cognition Workflow (Live SSE Streaming)
  const handleRunWorkflow = () => {
    if (isRunning) return;

    setIsRunning(true);
    setNodeOutputs({});
    setVerificationResults({});
    setAirlockData(null);
    setConsensusVerdict('');
    setAgentLogs([]);
    setActiveBlock(null);

    const newSessionId = `sess-${Math.random().toString(36).substring(2, 10)}`;
    setActiveSessionId(newSessionId);

    const scenarioId = selectedScenario ? selectedScenario.id : 'cryptographic_smart_contract_audit';
    const encodedPrompt = encodeURIComponent(customPrompt || (selectedScenario ? selectedScenario.default_prompt : ''));

    const sseUrl = `/api/stream/${newSessionId}?scenario_id=${scenarioId}&prompt=${encodedPrompt}`;
    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Highlight active building block in X-Ray
        if (data.building_block) {
          setActiveBlock(data.building_block);
        }

        // Add to live terminal stream
        setAgentLogs(prev => [data, ...prev]);

        // Process event types
        if (data.type === 'TASK_DAG_UPDATE') {
          setTasks(data.tasks);
        } else if (data.type === 'NODE_OUTPUT') {
          setNodeOutputs(prev => ({ ...prev, [data.node_id]: data }));
        } else if (data.type === 'VERIFICATION_RESULT') {
          setVerificationResults(prev => ({ ...prev, [data.node_id]: data }));
        } else if (data.type === 'CONSENSUS_EVALUATION') {
          setConsensusVerdict(data.consensus.consensus_verdict);
        } else if (data.type === 'AIRLOCK_REQUIRED') {
          setAirlockData(data.airlock);
        } else if (data.type === 'WORKFLOW_COMPLETE') {
          setIsRunning(false);
          setActiveBlock(null);
          if (data.updated_nodes) setNodes(data.updated_nodes);
          if (data.xray_stats) setXrayStats(data.xray_stats);
          fetchSessions();
          fetchDeadEnds();
          es.close();
        } else if (data.type === 'ERROR') {
          setIsRunning(false);
          es.close();
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    es.onerror = (err) => {
      console.warn('SSE stream closed or completed:', err);
      setIsRunning(false);
      setActiveBlock(null);
      fetchNodes();
      fetchSessions();
      fetchXray();
      es.close();
    };
  };

  // Resolve Permission Airlock Gate
  const handleResolveAirlock = (actionId, decision, operatorNote) => {
    fetch('/api/airlock/decision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action_id: actionId,
        decision: decision,
        operator_note: operatorNote
      })
    })
      .then(r => r.json())
      .then(res => {
        setAirlockData(null);
        fetchNodes();
        fetchDeadEnds();
        fetchXray();
        setAgentLogs(prev => [
          {
            type: 'AIRLOCK_RESOLVED',
            building_block: 'permissions',
            message: `Operator decision recorded: [${decision}] for target node [${res.target_node}].`,
            timestamp: Date.now() / 1000
          },
          ...prev
        ]);
      })
      .catch(console.error);
  };

  return (
    <div className="min-h-screen bg-[#060a0f] text-slate-200 flex flex-col font-sans select-none">
      {/* Top Tactical Command Bar */}
      <TopBar
        systemStatus={systemStatus}
        scenarios={scenarios}
        selectedScenario={selectedScenario}
        onSelectScenario={handleSelectScenario}
        onRun={handleRunWorkflow}
        isRunning={isRunning}
        activeSessionId={activeSessionId}
        onOpenModelConfig={() => setIsModelConfigOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
      />

      {/* 3-Panel Tactical Command Center */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Mission DAG, Session History & Node Reputation Memory Ledger */}
        <LeftPanel
          tasks={tasks}
          nodes={nodes}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          deadEnds={deadEnds}
        />

        {/* Center Panel: Execution Stream, Consensus Arena & Permission Airlock */}
        <CenterPanel
          selectedScenario={selectedScenario}
          customPrompt={customPrompt}
          onChangePrompt={setCustomPrompt}
          onRun={handleRunWorkflow}
          isRunning={isRunning}
          nodeOutputs={nodeOutputs}
          verificationResults={verificationResults}
          airlockData={airlockData}
          onResolveAirlock={handleResolveAirlock}
          agentLogs={agentLogs}
          consensusVerdict={consensusVerdict}
        />

        {/* Right Panel: OpenMinion 0.1 Building Blocks X-Ray (All 10 Blocks Live) */}
        <RightPanel
          xrayStats={xrayStats}
          activeBlock={activeBlock}
        />
      </div>

      {/* Modals */}
      <ModelConfigModal
        isOpen={isModelConfigOpen}
        onClose={() => setIsModelConfigOpen(false)}
      />
      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
      />
    </div>
  );
}
