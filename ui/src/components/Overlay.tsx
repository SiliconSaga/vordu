import { motion, AnimatePresence } from 'framer-motion';
import type { OverlayData } from '../types';

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

                                    {/* Mock BDD Features */}
                                    <div className="space-y-4">
                                        <h3 className="text-xl font-mono text-gray-300 border-b border-gray-800 pb-2">
                                            Verified Features
                                        </h3>
                                        <div className="space-y-4">
                                            {/* Mock Feature 1 */}
                                            <div className="bg-black/30 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition-colors">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="text-neon-green">✔</span>
                                                    <span className="font-bold text-white">Feature: User Authentication</span>
                                                </div>
                                                <div className="pl-7 text-gray-400 font-mono text-sm space-y-1">
                                                    <p>Scenario: Successful login with valid credentials</p>
                                                    <p>Scenario: Password reset flow</p>
                                                </div>
                                            </div>

                                            {/* Mock Feature 2 */}
                                            <div className="bg-black/30 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition-colors">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="text-neon-green">✔</span>
                                                    <span className="font-bold text-white">Feature: Session Management</span>
                                                </div>
                                                <div className="pl-7 text-gray-400 font-mono text-sm space-y-1">
                                                    <p>Scenario: Token refresh on expiry</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Failing/Pending Features */}
                                    {(data.status === 'fail' || data.status === 'pending') && (
                                        <div className="space-y-4">
                                            <h3 className="text-xl font-mono text-gray-300 border-b border-gray-800 pb-2">
                                                {data.status === 'fail' ? 'Failing Scenarios' : 'Pending Implementation'}
                                            </h3>
                                            <div className="bg-black/30 border border-gray-800 rounded-lg p-4 hover:border-gray-600 transition-colors">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className={data.status === 'fail' ? "text-red-500" : "text-yellow-500"}>
                                                        {data.status === 'fail' ? '✘' : '⚠'}
                                                    </span>
                                                    <span className="font-bold text-white">Feature: Advanced Permissions</span>
                                                </div>
                                                <div className="pl-7 text-gray-400 font-mono text-sm space-y-1">
                                                    <p>Scenario: Role-based access control for admins</p>
                                                    <p className="text-red-400 italic">
                                                        {data.status === 'fail' ? 'Error: Expected 403 but got 200' : 'Not implemented yet'}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};
