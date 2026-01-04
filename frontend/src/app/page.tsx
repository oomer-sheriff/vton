"use client";

import { useState } from "react";
import { Upload, X, Loader2, CheckCircle, Shirt } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [tasks, setTasks] = useState<{ bg: string; meta: string } | null>(null);
  const [results, setResults] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResults(null);
      setTasks(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/v1/ingestion/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      console.log("Upload response:", data);

      if (res.ok) {
        setTasks({
          bg: data.tasks.background_removal,
          meta: data.tasks.metadata_extraction
        });
        // Start polling
        pollStatus(data.tasks.background_removal, "bg");
        pollStatus(data.tasks.metadata_extraction, "meta");
      } else {
        alert("Upload failed: " + data.detail);
        setUploading(false);
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading file");
      setUploading(false);
    }
  };

  const pollStatus = async (taskId: string, type: "bg" | "meta") => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/ingestion/status/${taskId}`);
        const data = await res.json();

        console.log(`Polling ${type}:`, data);

        if (data.status === "SUCCESS") {
          clearInterval(interval);
          setResults((prev: any) => ({ ...prev, [type]: data.result }));

          // If this was the last pending task (simplification)
          setUploading(false); // Ideally wait for both
        } else if (data.status === "FAILURE") {
          clearInterval(interval);
          alert(`Task ${type} failed`);
          setUploading(false);
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-12">

        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Garment Ingestion
          </h1>
          <p className="text-neutral-400">Upload a raw photo to process it for Virtual Try-On.</p>
        </div>

        {/* Upload Area */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            {/* Input Section */}
            <div className="space-y-6">
              <div
                className="border-2 border-dashed border-neutral-700 rounded-xl p-8 flex flex-col items-center justify-center text-center hover:border-purple-500 transition-colors cursor-pointer relative h-64 bg-neutral-900/50"
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />

                {preview ? (
                  <img src={preview} alt="Preview" className="h-full w-full object-contain rounded-lg" />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-neutral-500 mb-4" />
                    <p className="text-neutral-300 font-medium">Click to upload or drag image</p>
                    <p className="text-sm text-neutral-500 mt-2">JPEG, PNG, WEBP (Max 10MB)</p>
                  </>
                )}
              </div>

              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`w-full py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${!file || uploading
                  ? "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                  : "bg-white text-black hover:bg-neutral-200"
                  }`}
              >
                {uploading ? (
                  <> <Loader2 className="animate-spin" /> Processing... </>
                ) : (
                  <> <Shirt className="w-5 h-5" /> Ingest Garment </>
                )}
              </button>
            </div>

            {/* Results Section */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-neutral-300 flex items-center gap-2">
                Processing Results
              </h3>

              {/* Background Removal Result */}
              <div className="bg-neutral-950 rounded-xl p-4 border border-neutral-800">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-purple-400">Background Removal (rembg)</span>
                  {results?.bg ? <CheckCircle className="w-4 h-4 text-green-500" /> : <div className="w-4 h-4 rounded-full border border-neutral-700" />}
                </div>

                {results?.bg ? (
                  // Since local path is returned by backend, in real app we'd serve this via static URL.
                  // For demo, we might not see it unless we map the volume. 
                  // We will assume backend serves it or just show success msg.
                  <div className="text-green-400 text-sm">
                    Process Complete! <br />
                    <span className="text-xs text-neutral-500 break-all">{results.bg.output_path}</span>
                  </div>
                ) : (
                  <div className="h-32 flex items-center justify-center text-neutral-600 text-sm italic">
                    {uploading ? "Removing background..." : "Waiting for upload..."}
                  </div>
                )}
              </div>

              {/* Metadata Result */}
              <div className="bg-neutral-950 rounded-xl p-4 border border-neutral-800">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-pink-400">AI Metadata (Gemini)</span>
                  {results?.meta ? <CheckCircle className="w-4 h-4 text-green-500" /> : <div className="w-4 h-4 rounded-full border border-neutral-700" />}
                </div>

                {results?.meta ? (
                  <pre className="text-xs text-neutral-300 bg-neutral-900 p-2 rounded overflow-auto h-32">
                    {results.meta.metadata
                      ? JSON.stringify(JSON.parse(results.meta.metadata), null, 2)
                      : JSON.stringify(results.meta, null, 2)
                    }
                  </pre>
                ) : (
                  <div className="h-32 flex items-center justify-center text-neutral-600 text-sm italic">
                    {uploading ? "Extracting tags..." : "Waiting for upload..."}
                  </div>
                )}
              </div>

            </div>

          </div>
        </div>
      </div>
    </main>
  );
}
