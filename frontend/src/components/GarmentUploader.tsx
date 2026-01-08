"use client";

import { useState } from "react";
import { Upload, Loader2, Plus } from "lucide-react";

export default function GarmentUploader({ onUploadComplete }: { onUploadComplete: () => void }) {
    const [uploading, setUploading] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    // Metadata State
    const [category, setCategory] = useState("");
    const [color, setColor] = useState("");
    const [description, setDescription] = useState("");

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            const file = e.target.files[0];
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setUploading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);
        if (category) formData.append("category", category);
        if (color) formData.append("color", color);
        if (description) formData.append("description", description);

        try {
            const res = await fetch("http://localhost:8000/api/v1/ingestion/upload", {
                method: "POST",
                body: formData,
            });
            if (res.ok) {
                // Clear state
                setSelectedFile(null);
                setPreviewUrl(null);
                setCategory("");
                setColor("");
                setDescription("");

                // Allow some time for background task to start
                setTimeout(() => {
                    onUploadComplete();
                }, 1000);
            } else {
                alert("Upload failed!");
            }
        } catch (err) {
            console.error(err);
            alert("Upload error");
        } finally {
            setUploading(false);
        }
    };

    const handleCancel = () => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setCategory("");
        setColor("");
        setDescription("");
    }

    if (selectedFile) {
        return (
            <div className="p-4 border border-neutral-700 rounded-xl bg-neutral-900/50 flex flex-col gap-4">
                <div className="flex gap-4">
                    {previewUrl && (
                        <img src={previewUrl} alt="Preview" className="w-24 h-32 object-cover rounded bg-neutral-800" />
                    )}
                    <div className="flex-1 space-y-3">
                        <input
                            type="text"
                            placeholder="Category (e.g. Dress, Top)"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full bg-neutral-800 border border-neutral-700 rounded px-3 py-2 text-sm text-white"
                        />
                        <input
                            type="text"
                            placeholder="Color (e.g. Red, Blue)"
                            value={color}
                            onChange={(e) => setColor(e.target.value)}
                            className="w-full bg-neutral-800 border border-neutral-700 rounded px-3 py-2 text-sm text-white"
                        />
                        <input
                            type="text"
                            placeholder="Description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full bg-neutral-800 border border-neutral-700 rounded px-3 py-2 text-sm text-white"
                        />
                    </div>
                </div>
                <div className="flex gap-2 justify-end">
                    <button
                        onClick={handleCancel}
                        disabled={uploading}
                        className="px-4 py-2 text-sm text-neutral-400 hover:text-white"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className="px-4 py-2 text-sm bg-white text-black rounded font-medium hover:bg-neutral-200 disabled:opacity-50"
                    >
                        {uploading ? "Uploading..." : "Upload Garment"}
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="relative group cursor-pointer h-full">
            <input
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                onChange={handleFileSelect}
                disabled={uploading}
            />
            <div className="flex flex-col items-center justify-center w-full h-full min-h-[12rem] border-2 border-dashed border-neutral-700 rounded-xl bg-neutral-900/50 hover:bg-neutral-800 transition-colors group-hover:border-neutral-500 text-center p-4">
                <Plus className="w-8 h-8 text-neutral-400 mb-2" />
                <span className="text-sm text-neutral-400 font-medium">Add New Garment</span>
            </div>
        </div>
    );
}
