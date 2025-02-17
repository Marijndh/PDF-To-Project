interface ImportMetaEnv {
    readonly VITE_EMAIL_FROM: string;
    readonly VITE_EMAIL_TO: string;
    readonly VITE_EMAIL_PASSWORD: string;
    readonly VITE_API_URL: string;
    readonly VITE_API_TOKEN: string;
    readonly VITE_API_KEY: string;
    readonly VITE_APPLICATION_NAME: string;
    readonly VITE_GOOGLE_CLIENT_ID: string;
    readonly VITE_GOOGLE_CLIENT_SECRET: string;
    readonly VITE_GOOGLE_REFRESH_TOKEN: string;
    readonly VITE_GOOGLE_ACCESS_TOKEN: string;
    readonly VITE_PROJECT_URL: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}