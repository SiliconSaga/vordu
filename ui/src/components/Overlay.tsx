import { motion, AnimatePresence } from 'framer-motion';
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

                                            <div className="bg-black/30 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition-colors space-y-3">
                                                {scenarios.map((scen, idx) => (
                                                    <div key={idx} className="flex items-start gap-3">
                                                        <StatusIcon status={scen.status} />
                                                        <div>
                                                            <p className="font-bold text-white text-sm">{scen.scenario}</p>
                                                            <p className="text-xs font-mono text-gray-500">
                                                                {scen.total_steps > 0 && (
                                                                    <span>Steps: {scen.passed_steps}/{scen.total_steps}</span>
                                                                )}
                                                                {(scen.status === 'pending' || scen.status === 'skipped') && scen.total_steps > 0 &&
                                                                    <span className="ml-2 text-yellow-600/70 italic">
                                                                        (Planned / Not Implemented)
                                                                    </span>
                                                                }
                                                            </p>
                                                        </div>
                                                    </div>
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

