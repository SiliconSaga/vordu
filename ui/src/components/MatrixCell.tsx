import { motion } from 'framer-motion';

interface MatrixCellProps {
    project: string;
    row: string;
    phase: number;
    status: 'pass' | 'fail' | 'pending' | 'empty';
    completion?: number; // 0-100
    scenariosTotal?: number;
    scenariosPassed?: number;
    stepsTotal?: number;
    stepsPassed?: number;
    color?: string;
    label?: string;
    onClick?: () => void;
}

export const MatrixCell = ({
    status,
    completion = 0,
    scenariosTotal = 0,
    scenariosPassed = 0,
    stepsTotal = 0,
    stepsPassed = 0,
    color = '#39ff14',
    label,
    onClick
}: MatrixCellProps) => {
    // Calculate opacity: 10% baseline + up to 90% based on completion
    const opacity = 0.1 + (Math.min(100, Math.max(0, completion)) / 100) * 0.9;

    return (
        <motion.div
            onClick={onClick}
            whileHover={{ scale: 1.05, opacity: 1 }}
            className="relative w-full h-24 rounded-lg border flex flex-col items-center justify-center px-1 py-2 cursor-pointer overflow-hidden group"
            style={{ borderColor: color, color: color }}
        >
            {/* Background Layer with Opacity */}
            <div
                className="absolute inset-0 transition-all duration-300"
                style={{
                    backgroundColor: 'transparent',
                    opacity: opacity,
                    boxShadow: `inset 0 0 50px ${color}`, // Strong inner glow fading to center
                }}
            />

            {/* Content Layer */}
            <div className="relative z-10 flex flex-col items-center text-center gap-0.5 w-full">
                {label && <span className="text-[10px] font-bold uppercase tracking-wider opacity-80" style={{ color }}>{label}</span>}

                {/* Content: Metrics OR Percentage */}
                {(completion > 0 || scenariosTotal > 0) && (
                    <>
                        {(scenariosTotal > 0 || stepsTotal > 0) ? (
                            <div className="flex flex-row items-center justify-center gap-1 text-base font-bold font-mono drop-shadow-md" style={{ textShadow: `0 0 5px ${color}` }}>
                                <span>{scenariosPassed}/{scenariosTotal}</span>
                                <span>-</span>
                                <span>{stepsPassed}/{stepsTotal}</span>
                            </div>
                        ) : (
                            <span className="text-3xl font-black drop-shadow-md" style={{ textShadow: `0 0 5px ${color}` }}>
                                {completion}%
                            </span>
                        )}
                    </>
                )}

                {/* Empty State Indicator */}
                {status === 'empty' && completion === 0 && (
                    <div className="w-2 h-2 rounded-full opacity-50" style={{ backgroundColor: color }} />
                )}
            </div>
        </motion.div>
    );
};
