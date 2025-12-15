import { useState, useEffect } from 'react';
import { MatrixCell } from './components/MatrixCell';
import { TopBar } from './components/TopBar';
import { Overlay } from './components/Overlay';
import { generateNeonColor } from './utils/colors';
import './App.css';
import type { MatrixCellData, OverlayData } from './types';

// Hardcoded Phases for MVP (Configurable later via Domain entity)
const PHASES = [
  { id: 0, label: "Foundation (Norðri)" },
  { id: 1, label: "Utility MVP" },
  { id: 2, label: "Federation" },
  { id: 3, label: "Sovereignty" },
];

interface RowConfig {
  id: string;
  label: string;
}

interface ProjectConfig {
  id: string;
  name: string;
  rows: RowConfig[];
}

function App() {
  const [matrixState, setMatrixState] = useState<MatrixCellData[]>([]);
  const [projectConfig, setProjectConfig] = useState<ProjectConfig[]>([]);
  const [selectedCell, setSelectedCell] = useState<OverlayData | null>(null);

  useEffect(() => {
    const fetchConfigAndData = async () => {
      try {
        // 1. Fetch Project Configuration (Structure)
        const configResp = await fetch('/config');
        if (configResp.ok) {
          const configData = await configResp.json();
          setProjectConfig(configData);
        } else {
          console.error("Failed to fetch config");
        }

        // 2. Fetch Matrix Data (Status)
        const dataResp = await fetch('/matrix');
        if (dataResp.ok) {
          const apiData = await dataResp.json();
          setMatrixState(apiData);
        }
      } catch (error) {
        console.error("Error connecting to API:", error);
      }
    };

    fetchConfigAndData();
  }, []);

  const getCellData = (project: string, row: string, phase: number) => {
    return matrixState.find(c => c.project === project && c.row === row && c.phase === phase);
  };

  const handleCellClick = (cellData: MatrixCellData | undefined, color: string) => {
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

      {/* Legend */}
      <div className="flex justify-center items-center gap-6 text-xs text-gray-500 font-mono uppercase tracking-wider py-4 border-b border-gray-900/50">
        <span>Color intensity = Completion</span>
        <span>Scenarios - Tests (Passing/Total)</span>
      </div>

      <div className="p-8 space-y-16">
        {projectConfig.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <p>Loading Roadmap Configuration...</p>
            <small>Ensure Vörðu API is running and data has been ingested.</small>
          </div>
        )}

        {projectConfig.map(project => {
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
                    >
                      {row.label}
                    </a>
                    {PHASES.map(phase => {
                      const cellData = getCellData(project.id, row.id, phase.id);
                      const cellColor = projectColor;

                      return (
                        <MatrixCell
                          key={`${project.id}-${row.id}-${phase.id}`}
                          project={project.id}
                          row={row.id}
                          phase={phase.id}
                          status={cellData ? cellData.status : 'empty'}
                          completion={cellData ? cellData.completion : 0}
                          scenariosTotal={cellData ? cellData.scenarios_total : 0}
                          scenariosPassed={cellData ? cellData.scenarios_passed : 0}
                          stepsTotal={cellData ? cellData.steps_total : 0}
                          stepsPassed={cellData ? cellData.steps_passed : 0}
                          color={cellColor}
                          onClick={() => handleCellClick(cellData, cellColor)}
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
