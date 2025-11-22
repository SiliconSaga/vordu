import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TopBarProps {
    projectName?: string;
}

export const TopBar = ({ projectName = "Yggdrasil" }: TopBarProps) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <motion.div
            initial={false}
            animate={{ height: isCollapsed ? '80px' : '300px' }}
            className="w-full bg-panel-bg border-b border-gray-800 relative overflow-hidden transition-all duration-500 ease-in-out z-50"
        >
            {/* GitHub Ribbon */}
            <div className="absolute top-0 right-0 z-50 pointer-events-none">
                <a
                    href="https://github.com/Cervator/vordu"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group relative block w-32 h-32 overflow-hidden pointer-events-auto"
                >
                    <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-bl from-neon-green/20 to-transparent transform rotate-45 translate-x-16 -translate-y-16 group-hover:translate-x-14 group-hover:-translate-y-14 transition-transform duration-300" />
                    <div className="absolute top-8 right-[-35px] w-[150px] transform rotate-45 bg-neon-green text-black text-xs font-bold text-center py-1 shadow-neon hover:bg-white transition-colors cursor-pointer">
                        Fork on GitHub
                    </div>
                </a>
            </div>

            {/* Toggle Button */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 w-8 h-8 bg-gray-800 border border-gray-700 rounded-full flex items-center justify-center text-gray-400 hover:text-neon-green hover:border-neon-green transition-colors z-50 cursor-pointer"
            >
                {isCollapsed ? '▼' : '▲'}
            </button>

            <div className="container mx-auto h-full flex items-center px-8 gap-12">
                {/* Logo Section */}
                <motion.div
                    layout
                    className={`flex-shrink-0 transition-all duration-500 ${isCollapsed ? 'w-16 h-16' : 'w-72 h-72'}`}
                >
                    <img src="/logo_transparent.png" alt="Vörðu Logo" className="w-full h-full object-contain" />
                </motion.div>

                {/* Text Content */}
                <div className="flex-grow text-left">
                    <motion.h1
                        layout
                        className={`font-semibold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-neon-green to-blue-500 transition-all duration-500 ${isCollapsed ? 'text-4xl' : 'text-7xl'}`}
                    >
                        VÖRÐU - Cairn
                    </motion.h1>

                    <AnimatePresence>
                        {!isCollapsed && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="overflow-hidden"
                            >
                                <div className="space-y-2 mt-4">
                                    <p className="text-gray-300 text-xl max-w-3xl leading-relaxed">
                                        The Living Roadmap. Visualizing ecosystem maturity via Behavior Driven Development.
                                    </p>
                                    <p className="text-gray-400 text-base max-w-3xl">
                                        Track evolution of projects across multiple dimensions as they progress (color in).
                                        Columns are time or maturity, sections are projects, rows are capabilities.
                                        Click any cell to see the underlying Gherkin details.
                                    </p>
                                </div>

                                <div className="flex gap-8 mt-6 text-sm font-mono text-neon-blue/80 border-t border-gray-800 pt-4 w-fit">
                                    <div>PROJECT: <span className="text-neon-green">{projectName}</span></div>
                                    <div>STATUS: <span className="text-neon-green">ONLINE</span></div>
                                    <div>LAST UPDATE: <span className="text-neon-green">JUST NOW</span></div>
                                    <div>VERSION: <span className="text-gray-400">v0.1.0-alpha</span></div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.div>
    );
};
