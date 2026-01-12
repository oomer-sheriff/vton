"use client";

import { useState } from "react";
import { Upload, Sparkles, Loader2 } from "lucide-react";

interface Props {
    selectedGarmentId: string | null;
}

export default function MagicMirror({ selectedGarmentId }: Props) {
    const [personImage, setPersonImage] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            const file = e.target.files[0];
            setPersonImage(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResultUrl(null); // Reset result
        }
    };

    const handleTryOn = async () => {
        if (!personImage || !selectedGarmentId) return;

        setLoading(true);
        setStatus("Initiating Try-On...");

        const formData = new FormData();
        formData.append("person_image", personImage);
        formData.append("garment_id", selectedGarmentId);

        try {
            const res = await fetch("http://localhost:8000/api/v1/tryon/", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();

            if (data.task_id) {
                pollStatus(data.task_id);
            }
        } catch (error) {
            console.error(error);
            setLoading(false);
            setStatus("Failed to start.");
        }
    };

    const pollStatus = (taskId: string) => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/v1/tryon/status/${taskId}`);
                const data = await res.json();

                if (data.status === "SUCCESS") {
                    clearInterval(interval);
                    setLoading(false);
                    setStatus("Complete!");
                    // result_path is relative like "media/results/..."
                    setResultUrl(`http://localhost:8000/${data.result.result_path.replace("\\", "/")}`);
                } else if (data.status === "FAILURE") {
                    clearInterval(interval);
                    setLoading(false);
                    setStatus("Failed: " + data.result);
                } else {
                    setStatus(`Processing... (${data.status})`);
                }
            } catch (err) {
                clearInterval(interval);
                setLoading(false);
            }
        }, 2000);
    };

    return (
        <div className="flex flex-col h-full bg-neutral-900 rounded-2xl overflow-hidden border border-neutral-800">
            <div className="flex-1 relative bg-black/50 flex items-center justify-center p-4">
                {resultUrl ? (
                    <img src={resultUrl} alt="Result" className="max-h-full max-w-full object-contain rounded-lg shadow-2xl" />
                ) : previewUrl ? (
                    <img src={previewUrl} alt="Preview" className="max-h-full max-w-full object-contain opacity-50 blur-sm scale-95 transition-all" />
                ) : (
                    <div className="text-center text-neutral-500">
                        <Upload className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Upload your photo to start</p>
                    </div>
                )}

                {loading && (
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center z-10">
                        <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
                        <p className="text-white font-medium animate-pulse">{status}</p>
                    </div>
                )}
            </div>

            <div className="p-6 bg-neutral-900 border-t border-neutral-800">
                <label className="block w-full text-center">
                    <input type="file" className="hidden" onChange={handleImageChange} accept="image/*" />
                    <span className="block w-full py-3 px-4 rounded-xl border border-neutral-700 text-neutral-300 hover:bg-neutral-800 cursor-pointer transition-colors text-sm font-medium mb-4">
                        {previewUrl ? "Change Photo" : "Upload Your Photo"}
                    </span>
                </label>

                <button
                    onClick={handleTryOn}
                    disabled={!personImage || !selectedGarmentId || loading}
                    className={`w-full py-4 rounded-xl flex items-center justify-center space-x-2 font-bold text-lg transition-all ${!personImage || !selectedGarmentId || loading
                            ? "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                            : "bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-900/50 hover:scale-[1.02]"
                        }`}
                >
                    <Sparkles className="w-5 h-5 fill-current" />
                    <span>Magic Try-On</span>
                </button>
            </div>
        </div>
    );
}
