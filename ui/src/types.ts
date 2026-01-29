export interface ScenarioDetail {
    feature: string;
    scenario: string;
    status: 'passed' | 'failed' | 'pending' | 'undefined' | 'skipped';
    passed_steps: number;
    total_steps: number;
    tag?: string;
    steps?: StepDetail[];
    feature_file?: string;
}

export interface StepDetail {
    keyword: string;
    name: string;
    status: string;
}

export interface MatrixCellData {
    project: string;
    row: string;
    phase: number;
    status: 'pass' | 'failed' | 'pending' | 'empty';
    completion: number;
    scenarios_total?: number;
    scenarios_passed?: number;
    steps_total?: number;
    steps_passed?: number;
    details?: ScenarioDetail[];
    updateText?: string;
    link?: string;
}

export interface OverlayData extends MatrixCellData {
    color?: string;
}

export interface RowConfig {
  id: string;
  label: string;
}

export interface ProjectConfig {
  id: string;
  name: string;
  repo_slug?: string;
  rows: RowConfig[];
}
