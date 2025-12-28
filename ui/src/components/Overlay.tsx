import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import type { OverlayData, ScenarioDetail } from '../types';

interface OverlayProps {
    isOpen: boolean;
    onClose: () => void;
    data: OverlayData | null;
    color: string;
}

export const Overlay = ({ isOpen, onClose, data, color }: OverlayProps) => {
    if (!data) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop - Fades the background */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60]"
                    />

                    {/* Modal Container */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 flex items-center justify-center z-[70] pointer-events-none"
                    >
                        <div
                            className="w-[90vw] h-[85vh] bg-panel-bg border-2 rounded-xl overflow-hidden flex flex-col pointer-events-auto shadow-2xl relative"
                            style={{ borderColor: color, boxShadow: `0 0 30px ${color}40` }}
                        >
                            {/* Header */}
                            <div className="p-6 border-b border-gray-800 flex justify-between items-start bg-black/20">
                                <div>
                                    <h2 className="text-3xl font-bold text-white mb-2" style={{ textShadow: `0 0 10px ${color}` }}>
                                        {data.project} / {data.row}
                                    </h2>
                                    <div className="flex gap-4 text-sm font-mono text-gray-400">
                                        <span>PHASE: <span className="text-white">{data.phase}</span></span>
                                        <span>STATUS: <span style={{ color }}>{data.status.toUpperCase()}</span></span>
                                        <span>COMPLETION: <span className="text-white">{data.completion}%</span></span>
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="text-gray-500 hover:text-white transition-colors text-2xl leading-none"
                                >
                                    ✕
                                </button>
                            </div>

                            {/* Content - Scrollable */}
                            <div className="flex-grow overflow-y-auto p-8">
                                <div className="max-w-4xl mx-auto space-y-8">

                                    {(!data.details || data.details.length === 0) && (
                                        <div className="text-gray-500 text-center italic">
                                            No detailed scenarios recorded for this capability.
                                        </div>
                                    )}

                                    {/* Group by Feature */}
                                    {data.details && Object.entries(groupByFeature(data.details)).map(([feature, scenarios]) => (
                                        <div key={feature} className="space-y-4">
                                            <h3 className="text-xl font-mono text-gray-300 border-b border-gray-800 pb-2">
                                                {feature}
                                            </h3>

                                            <div className="space-y-3">
                                                {scenarios.map((scen, idx) => (
                                                    <ScenarioRow key={idx} scenario={scen} />
                                                ))}
                                            </div>
                                        </div>
                                    ))}

                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

// Helper components
const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
        case 'passed': return <span className="text-neon-green">✔</span>;
        case 'failed': return <span className="text-red-500">✘</span>;
        case 'pending':
        case 'skipped':
        case 'undefined':
            return <span className="text-yellow-500">⚠</span>;
        default: return <span className="text-gray-500">?</span>;
    }
};

const groupByFeature = (details: ScenarioDetail[]) => {
    return details.reduce((groups, item) => {
        const feature = item.feature || 'Unknown Feature';
        if (!groups[feature]) {
            groups[feature] = [];
        }
        groups[feature].push(item);
        return groups;
    }, {} as Record<string, ScenarioDetail[]>);
};

const ScenarioRow = ({ scenario }: { scenario: ScenarioDetail }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    // Icons
    const JenkinsIcon = () => (
        <button
            onClick={(e) => { e.stopPropagation(); /* TODO: Link */ }}
            className="hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
            aria-label="See scenario results in Jenkins"
            title="See scenario results in Jenkins"
        >
            <img
                src="/jenkins.png"
                alt=""
                className="w-5 h-5 cursor-pointer"
            />
        </button>
    );

    const GitHubIcon = () => (
        <button
            onClick={(e) => { e.stopPropagation(); /* TODO: Link */ }}
            className="hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
            aria-label="See scenario definition on GitHub"
            title="See scenario definition on GitHub"
        >
            <img
                src="/GitHub.png"
                alt=""
                className="w-5 h-5 cursor-pointer"
            />
        </button>
    );

    const GitHubCreateIssueIcon = () => (
        <button
            onClick={(e) => { e.stopPropagation(); /* TODO: Link */ }}
            className="hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
            aria-label="Create an issue for this scenario on GitHub"
            title="Create an issue for this scenario on GitHub"
        >
            <img
                src="/CreateIssueGitHub.png"
                alt=""
                className="w-5 h-5 cursor-pointer"
            />
        </button>
    );

    return (
        <div className="border border-gray-800 rounded-lg overflow-hidden bg-black/30 transition-all">
            <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-3">
                    <StatusIcon status={scenario.status} />
                    <div>
                        <p className="font-bold text-white text-sm">{scenario.scenario}</p>
                        <p className="text-xs font-mono text-gray-500">
                            {scenario.total_steps > 0 && (
                                <span>Steps: {scenario.passed_steps}/{scenario.total_steps}</span>
                            )}
                            {(scenario.status === 'pending' || scenario.status === 'skipped') && scenario.total_steps > 0 &&
                                <span className="ml-2 text-yellow-600/70 italic">
                                    (Planned / Not Implemented)
                                </span>
                            }
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3 bg-gray-900/50 p-2 rounded border border-gray-800">
                    <JenkinsIcon />
                    <GitHubIcon />
                    <GitHubCreateIssueIcon />
                </div>
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="bg-black/50 p-4 border-t border-gray-800 space-y-2">
                            {scenario.steps && scenario.steps.length > 0 ? (
                                scenario.steps.map((step, idx) => (
                                    <div key={idx} className="flex gap-2 text-sm font-mono items-center">
                                        <StatusIcon status={step.status} />
                                        <span className="text-yellow-500 font-bold">{step.keyword}</span>
                                        <span className="text-gray-300">{step.name}</span>
                                    </div>
                                ))
                            ) : (
                                <p className="text-gray-500 text-sm italic">No detailed steps recorded.</p>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

