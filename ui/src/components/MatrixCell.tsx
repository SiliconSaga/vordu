import { motion } from 'framer-motion';

interface MatrixCellProps {
    project: string;
    row: string;
    phase: number;
    status: 'pass' | 'fail' | 'pending' | 'empty';
    label?: string;
}

export const MatrixCell = ({ status, label }: MatrixCellProps) => {
    const getStatusColor = () => {
        switch (status) {
            case 'pass': return 'bg-neon-green shadow-neon border-neon-green';
            case 'fail': return 'bg-red-500 shadow-red-500/50 border-red-500';
            case 'pending': return 'bg-yellow-500 shadow-yellow-500/50 border-yellow-500';
            default: return 'bg-panel-bg border-gray-700 opacity-30';
        }
    };

    return (
        <motion.div
            whileHover={{ scale: 1.05 }}
            className={`
        w-full h-24 rounded-lg border-2 flex items-center justify-center p-2
        transition-colors duration-300 cursor-pointer
        ${getStatusColor()}
      `}
        >
            {label && <span className="text-xs font-bold text-black uppercase tracking-wider">{label}</span>}
            {status === 'empty' && <div className="w-2 h-2 rounded-full bg-gray-600" />}
        </motion.div>
    );
};
