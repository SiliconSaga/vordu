import { useState, useEffect } from 'react';
import { MatrixCell } from './components/MatrixCell';
import './App.css';

// Mock Data for now
const PHASES = [
  { id: 0, label: "Foundation (Norðri)" },
  { id: 1, label: "Utility MVP" },
  { id: 2, label: "Federation" },
  { id: 3, label: "Sovereignty" },
];

const PROJECTS = [
  {
    id: 'demicracy',
    name: 'Demicracy',
    rows: [
      { id: 'identity', label: 'Identity & Trust' },
      { id: 'governance', label: 'Governance' },
    ]
  },
  {
    id: 'autoboros',
    name: 'Autoboros',
    rows: [
      { id: 'agents', label: 'Agent Orchestration' }
    ]
  }
];

function App() {
  const [matrixState, setMatrixState] = useState<any[]>([]);

  useEffect(() => {
    // Simulate fetching data
    setMatrixState([
      { project: 'demicracy', row: 'identity', phase: 0, status: 'pass' },
      { project: 'demicracy', row: 'governance', phase: 1, status: 'fail' },
    ]);
  }, []);

  const getStatus = (project: string, row: string, phase: number) => {
    const cell = matrixState.find(c => c.project === project && c.row === row && c.phase === phase);
    return cell ? cell.status : 'empty';
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white p-8 font-sans">
      <header className="mb-12 flex items-center gap-4">
        <div className="w-16 h-16 rounded-full flex items-center justify-center shadow-neon overflow-hidden">
          <img src="/logo.png" alt="Vörðu Logo" className="w-full h-full object-cover" />
        </div>
        <h1 className="text-4xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-neon-green to-neon-blue">
          VÖRÐU
        </h1>
      </header>

      <div className="space-y-16">
        {PROJECTS.map(project => (
          <section key={project.id} className="relative">
            {/* Project Header */}
            <div className="flex items-center gap-4 mb-6 border-b border-gray-800 pb-2">
              <h2 className="text-2xl font-mono text-neon-blue uppercase tracking-widest">{project.name}</h2>
              <div className="h-px flex-grow bg-gradient-to-r from-neon-blue/50 to-transparent" />
            </div>

            {/* Matrix Grid */}
            <div className="grid grid-cols-[200px_repeat(4,1fr)] gap-4">
              {/* Header Row */}
              <div className="text-right pr-4 pt-2 text-gray-500 font-mono text-sm">CAPABILITY</div>
              {PHASES.map(phase => (
                <div key={phase.id} className="text-center text-gray-400 font-bold text-sm uppercase tracking-widest">
                  {phase.label}
                </div>
              ))}

              {/* Data Rows */}
              {project.rows.map(row => (
                <>
                  <div key={row.id} className="text-right pr-4 py-8 font-medium text-gray-300 flex items-center justify-end">
                    {row.label}
                  </div>
                  {PHASES.map(phase => (
                    <MatrixCell
                      key={`${project.id}-${row.id}-${phase.id}`}
                      project={project.id}
                      row={row.id}
                      phase={phase.id}
                      status={getStatus(project.id, row.id, phase.id)}
                    />
                  ))}
                </>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

export default App;
