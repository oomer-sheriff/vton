"use client";

import { useState } from "react";
import { Upload, Loader2, Plus } from "lucide-react";

export default function GarmentUploader({ onUploadComplete }: { onUploadComplete: () => void }) {
    const [uploading, setUploading] = useState(false);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        setUploading(true);
        const formData = new FormData();
        formData.append("file", e.target.files[0]);

        try {
            const res = await fetch("http://localhost:8000/api/v1/ingestion/upload", {
                method: "POST",
                body: formData,
            });
            if (res.ok) {
                // We could poll for status here, but for now let's just wait a bit or trigger refresh
                // Since processing takes time (rembg), immediate refresh might not show it in "processed" list yet.
                // Ideally we show a "Processing..." toast.
                setTimeout(() => {
                    onUploadComplete();
                }, 2000);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="relative group cursor-pointer">
            <input
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                onChange={handleUpload}
                disabled={uploading}
            />
            <div className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-neutral-700 rounded-xl bg-neutral-900/50 hover:bg-neutral-800 transition-colors group-hover:border-neutral-500">
                {uploading ? (
                    <Loader2 className="w-8 h-8 text-neutral-400 animate-spin" />
                ) : (
                    <>
                        <Plus className="w-8 h-8 text-neutral-400 mb-2" />
                        <span className="text-sm text-neutral-400 font-medium">Add Garment</span>
                    </>
                )}
            </div>
        </div>
    );
}
