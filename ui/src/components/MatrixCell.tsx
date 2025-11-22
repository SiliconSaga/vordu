import { motion } from 'framer-motion';

interface MatrixCellProps {
    project: string;
    row: string;
    phase: number;
    status: 'pass' | 'fail' | 'pending' | 'empty';
    completion?: number; // 0-100
    color?: string;
    label?: string;
}

export const MatrixCell = ({ status, completion = 0, color = '#39ff14', label }: MatrixCellProps) => {
    // Calculate opacity: 10% baseline + up to 90% based on completion
    const opacity = 0.1 + (Math.min(100, Math.max(0, completion)) / 100) * 0.9;

    return (
        <motion.div
            whileHover={{ scale: 1.05, opacity: 1 }}
            className="relative w-full h-24 rounded-lg border flex items-center justify-center p-2 cursor-pointer overflow-hidden group"
            style={{ borderColor: color }}
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

            {/* Content Layer (keeps text opaque-ish) */}
            <div className="relative z-10">
                {label && <span className="text-xs font-bold text-black uppercase tracking-wider">{label}</span>}
                {status === 'empty' && completion === 0 && (
                    <div className="w-2 h-2 rounded-full bg-gray-600 opacity-50" />
                )}
            </div>
        </motion.div>
    );
};
