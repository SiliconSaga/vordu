import { useState, useEffect } from 'react';
import { MatrixCell } from './components/MatrixCell';
import { TopBar } from './components/TopBar';
import { Overlay } from './components/Overlay';
import { generateNeonColor } from './utils/colors';
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
  const [selectedCell, setSelectedCell] = useState<any>(null);

  useEffect(() => {
    // Simulate fetching data with completion percentages
    setMatrixState([
      {
        project: 'demicracy',
        row: 'identity',
        phase: 0,
        status: 'pass',
        completion: 100,
        updateText: 'Core identity module verified',
        link: 'https://github.com/Cervator/demicracy'
      },
      {
        project: 'demicracy',
        row: 'identity',
        phase: 1,
        status: 'pending',
        completion: 40,
        updateText: 'OAuth integration in progress',
        link: 'https://github.com/Cervator/demicracy/issues'
      },
      {
        project: 'demicracy',
        row: 'governance',
        phase: 1,
        status: 'fail',
        completion: 10,
        updateText: 'Voting mechanism failing tests',
        link: 'https://github.com/Cervator/demicracy/actions'
      },
      {
        project: 'autoboros',
        row: 'agents',
        phase: 0,
        status: 'pending',
        completion: 25,
        updateText: 'Agent framework scaffolding',
        link: 'https://github.com/Cervator/autoboros'
      },
    ]);
  }, []);

  const getCellData = (project: string, row: string, phase: number) => {
    return matrixState.find(c => c.project === project && c.row === row && c.phase === phase);
  };

  const handleCellClick = (cellData: any, color: string) => {
    if (cellData) {
      setSelectedCell({ ...cellData, color });
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white font-sans">
      <TopBar projectName="Overview" />

      <Overlay
        isOpen={!!selectedCell}
        onClose={() => setSelectedCell(null)}
        data={selectedCell}
        color={selectedCell?.color || '#fff'}
      />

      <div className="p-8 space-y-16">
        {PROJECTS.map(project => {
          const projectColor = generateNeonColor(project.name);

          return (
            <section key={project.id} className="relative">
              {/* Project Header */}
              <div className="flex items-center gap-4 mb-6 border-b border-gray-800 pb-2">
                <h2
                  className="text-2xl font-mono uppercase tracking-widest"
                  style={{ color: projectColor, textShadow: `0 0 10px ${projectColor}` }}
                >
                  {project.name}
                </h2>
                <div
                  className="h-px flex-grow"
                  style={{
                    background: `linear-gradient(to right, ${projectColor} 0%, transparent 100%)`,
                    opacity: 0.5
                  }}
                />
              </div>

              {/* Matrix Grid */}
              <div className="grid grid-cols-[200px_repeat(4,1fr)] gap-4">
                {/* Header Row */}
                <div className="text-right pr-4 pt-2 text-gray-500 font-mono text-sm">CAPABILITY</div>
                {PHASES.map(phase => (
                  <a
                    key={phase.id}
                    href="#"
                    className="text-center text-gray-400 font-bold text-sm uppercase tracking-widest hover:text-white transition-colors"
                    title="View Quarterly Planning Blog"
                  >
                    {phase.label}
                  </a>
                ))}

                {/* Data Rows */}
                {project.rows.map(row => (
                  <>
                    <a
                      key={row.id}
                      href="#"
                      className="text-right pr-4 py-8 font-medium text-gray-300 flex items-center justify-end hover:text-white transition-colors"
                      title="View Subject Area Definition"
                    >
                      {row.label}
                    </a>
                    {PHASES.map(phase => {
                      const cellData = getCellData(project.id, row.id, phase.id);
                      return (
                        <MatrixCell
                          key={`${project.id}-${row.id}-${phase.id}`}
                          project={project.id}
                          row={row.id}
                          phase={phase.id}
                          status={cellData ? cellData.status : 'empty'}
                          completion={cellData ? cellData.completion : 0}
                          color={projectColor}
                          onClick={() => handleCellClick(cellData, projectColor)}
                        />
                      );
                    })}
                  </>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}

export default App;
