export interface MatrixCellData {
    project: string;
    row: string;
    phase: number;
    status: 'pass' | 'fail' | 'pending' | 'empty';
    completion: number;
    scenarios_total?: number;
    scenarios_passed?: number;
    steps_total?: number;
    steps_passed?: number;
    updateText?: string;
    link?: string;
}

export interface OverlayData extends MatrixCellData {
    color?: string;
}
