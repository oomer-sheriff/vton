export interface Garment {
    id: string;
    image: string;
    metadata?: {
        category?: string;
        color?: string;
        pattern?: string;
        style_tags?: string[];
    };
}

export interface TryOnResult {
    task_id: string;
    status: string;
    result_path?: string;
    error?: string;
}
