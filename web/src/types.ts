export interface JobDescription {
    id: string;
    name: string;
    job_description: string;
    html_content?: string;
}

export interface Candidate {
    id: string;
    name: string;
    email: string;
    phone: string;
    status: string;
    stage_name: string;
    opening_name: string;
    cv_url?: string;
    cv_text?: string;
    reviews?: any[];
    test_results?: any[];
}

export interface Interview {
    id: string;
    candidate_name: string;
    opening_name: string;
    time_dt: string;
}

export interface ToolOutput {
    type: string;
    data: any;
    message?: string;
    success?: boolean;
}

declare global {
    interface Window {
        openai: {
            toolOutput: ToolOutput;
            callTool: (name: string, args: any) => Promise<any>;
            uploadFile: (file: File) => Promise<{ fileId: string }>;
            getFileDownloadUrl: (options: { fileId: string }) => Promise<{ downloadUrl: string }>;
        };
    }
}
