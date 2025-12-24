import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import type { OverlayData, ScenarioDetail} from '../types';

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
    const GitHubIcon = () => (
        <svg className="w-5 h-5 text-gray-400 hover:text-white cursor-pointer transition-colors" viewBox="0 0 16 16" fill="currentColor" onClick={(e) => { e.stopPropagation(); /* TODO: Link */ }}>
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
        </svg>
    );

    const JenkinsIcon = () => (
        <svg className="w-5 h-5 text-gray-400 hover:text-white cursor-pointer transition-colors" viewBox="0 0 24 24" fill="currentColor" onClick={(e) => { e.stopPropagation(); /* TODO: Link */ }}>
            <title>Jenkins</title>
            <path d="M2.872 24h-.975a3.866 3.866 0 01-.07-.197c-.215-.666-.594-1.49-.692-2.154-.146-.984.78-1.039 1.374-1.465.915-.66 1.635-1.025 2.627-1.62.295-.179 1.182-.624 1.281-.829.201-.408-.345-.982-.49-1.3-.225-.507-.345-.937-.376-1.435-.824-.13-1.455-.627-1.844-1.185-.63-.925-1.066-2.635-.525-3.936.045-.103.254-.305.285-.463.06-.308-.105-.72-.12-1.048-.06-1.692.284-3.15 1.425-3.66.463-1.84 2.113-2.453 3.673-3.367.58-.342 1.224-.562 1.89-.807 2.372-.877 6.027-.712 7.994.783.836.633 2.176 1.97 2.656 2.939 1.262 2.555 1.17 6.825.287 9.934-.12.421-.29 1.032-.533 1.533-.168.35-.689 1.05-.625 1.36.064.314 1.19 1.17 1.432 1.395.434.422 1.26.975 1.324 1.5.07.557-.248 1.336-.41 1.875-.217.721-.436 1.441-.654 2.131H2.87zm11.104-3.54c-.545-.3-1.361-.622-2.065-.757-.87-.164-.78 1.188-.75 1.994.03.643.36 1.316.51 1.744.076.197.09.41.256.449.3.068 1.29-.326 1.575-.479.6-.328 1.064-.844 1.574-1.189.016-.17.016-.34.03-.508a2.648 2.648 0 00-1.095-.277c.314-.15.75-.15 1.035-.332l.016-.193c-.496-.03-.69-.254-1.021-.436zm7.454 2.935a17.78 17.78 0 00.465-1.752c.06-.287.215-.918.178-1.176-.059-.459-.684-.799-1.004-1.086-.584-.525-.95-.975-1.56-1.469-.249.375-.78.615-.983.914 1.447-.689 1.71 2.625 1.141 3.69.09.329.391.45.514.735l-.086.166h1.29c.013 0 .03 0 .044.014zm-6.634-.012c-.05-.074-.1-.135-.15-.209l-.301.195h.45zm2.77 0c.008-.209.018-.404.03-.598-.53.029-.825-.48-1.196-.527-.324-.045-.6.361-1.02.195-.095.105-.183.227-.284.316.154.18.295.375.424.584h.815c.014-.164.135-.285.3-.285.165 0 .284.121.284.27h.66zm2.116 0c-.314-.479-.947-.898-1.68-.555l-.03.541h1.71zm-8.51 0l-.104-.344c-.225-.72-.36-1.26-.405-1.68-.914-.436-1.875-.87-2.654-1.426-.15-.105-1.109-1.35-1.23-1.305-1.739.676-3.359 1.86-4.814 2.984.256.557.48 1.141.69 1.74h8.505zm8.265-2.113c-.029-.512-.164-1.56-.48-1.74-.66-.39-1.846.78-2.34.943.045.15.135.271.15.48.285-.074.645-.029.898.092-.299.03-.629.03-.824.164-.074.195.016.48-.029.764.69.197 1.5.303 2.385.332.164-.227.225-.645.211-1.082zm-4.08-.36c-.044.375.046.51.12.943 1.26.391 1.034-1.74-.135-.959zM8.76 19.5c-.45.457 1.27 1.082 1.814 1.115 0-.29.165-.564.135-.77-.65-.118-1.502-.042-1.945-.347zm5.565.215c0 .043-.061.03-.068.064.58.451 1.014.545 1.802.51.354-.262.67-.563 1.043-.807-.855.074-1.931.607-2.774.23zm3.42-17.726c-1.606-.906-4.35-1.591-6.076-.731-1.38.692-3.27 1.84-3.899 3.292.6 1.402-.166 2.686-.226 4.109-.018.757.36 1.42.391 2.242-.2.338-.825.38-1.26.356-.146-.729-.4-1.549-1.155-1.63-1.064-.116-1.845.764-1.89 1.683-.06 1.08.833 2.864 2.085 2.745.488-.046.608-.54 1.139-.54.285.57-.445.75-.523 1.154-.016.105.06.511.104.705.233.944.744 2.16 1.245 2.88.635.9 1.884 1.051 3.229 1.141.24-.525 1.125-.48 1.706-.346-.691-.27-1.336-.945-1.875-1.529-.615-.676-1.23-1.41-1.261-2.28 1.155 1.604 2.1 3 4.2 3.704 1.59.525 3.45-.254 4.664-1.109.51-.359.811-.93 1.17-1.439 1.35-1.936 1.98-4.71 1.846-7.394-.06-1.111-.06-2.221-.436-2.955-.389-.781-1.695-1.471-2.475-.781-.15-.764.63-1.23 1.545-.96-.66-.854-1.336-1.858-2.266-2.384zM13.58 14.896c.615 1.544 2.724 1.361 4.505 1.323-.084.194-.256.435-.465.515-.57.232-2.145.408-2.937-.012-.506-.27-.824-.873-1.102-1.227-.137-.172-.795-.608-.012-.609zm.164-.87c.893.464 2.52.517 3.731.48.066.267.066.593.068.913-1.55.08-3.386-.304-3.794-1.395h-.005zm6.675-.586c-.473.9-1.145 1.897-2.539 1.928-.023-.284-.045-.735 0-.904 1.064-.103 1.727-.646 2.543-1.017zm-.649-.667c-1.02.66-2.154 1.375-3.824 1.21-.351-.31-.485-1-.14-1.458.181.313.06.885.57.97.944.165 2.038-.579 2.73-.84.42-.713-.046-.976-.42-1.433-.782-.93-1.83-2.1-1.802-3.51.314-.224.346.346.391.45.404.96 1.424 2.175 2.174 3 .18.21.48.39.51.524.092.39-.254.854-.209 1.11zm-13.439-.675c-.314-.184-.393-.99-.768-1.01-.535-.03-.438 1.05-.436 1.68-.37-.33-.435-1.365-.164-1.89-.308-.15-.445.164-.618.284.22-1.59 2.34-.734 1.99.96zM4.713 5.995c-.685.756-.54 2.174-.459 3.188 1.244-.785 2.898.06 2.883 1.394.595-.016.223-.744.115-1.215-.353-1.528.592-3.187.041-4.59-1.064.084-1.939.52-2.578 1.215zm9.12 1.113c.307.562.404 1.148.84 1.57.195.19.574.424.387.95-.045.121-.365.391-.551.45-.674.195-2.254.03-1.721-.81.563.015 1.314.36 1.732-.045-.314-.524-.885-1.53-.674-2.13zm6.198-.013h.068c.33.668.6 1.375 1.004 1.965-.27.628-2.053 1.19-2.023.057.39-.17 1.05-.035 1.395-.25-.193-.556-.48-1.006-.434-1.771zm-6.927-1.617c-1.422-.33-2.131.592-2.56 1.553-.384-.094-.231-.615-.135-.883.255-.701 1.28-1.633 2.119-1.506.359.057.848.386.576.834zM9.642 1.593c-1.56.44-3.56 1.574-4.2 2.974.495-.07.84-.321 1.33-.351.186-.016.428.074.641.015.424-.104.78-1.065 1.102-1.41.31-.345.685-.496.94-.81.167-.09.409-.074.42-.33-.073-.075-.15-.135-.232-.105v.017z" /></svg>
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
                    <GitHubIcon />
                    <JenkinsIcon />
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

