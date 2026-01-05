"use client";

import { useState, useEffect } from "react";
import GarmentSelector from "@/components/GarmentSelector";
import GarmentUploader from "@/components/GarmentUploader";
import MagicMirror from "@/components/MagicMirror";
import { Garment } from "@/types";
import { Shirt } from "lucide-react";

export default function Home() {
  const [garments, setGarments] = useState<Garment[]>([]);
  const [selectedGarmentId, setSelectedGarmentId] = useState<string | null>(null);

  const fetchGarments = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/ingestion/garments");
      const data = await res.json();
      setGarments(data);
    } catch (err) {
      console.error("Failed to fetch garments", err);
    }
  };

  useEffect(() => {
    fetchGarments();
  }, []);

  return (
    <main className="min-h-screen bg-black text-white p-4 lg:p-8 font-sans">
      <header className="mb-8 flex items-center space-x-3">
        <div className="w-10 h-10 bg-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-900/20">
          <Shirt className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-neutral-400">
          VTON Magic Mirror
        </h1>
      </header>

      <div className="grid lg:grid-cols-12 gap-8 max-w-7xl mx-auto h-[85vh]">
        {/* Left Panel: Closet (Scrollable) */}
        <div className="lg:col-span-4 flex flex-col space-y-6 h-full overflow-hidden">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-neutral-200">Your Closet</h2>
            <span className="text-xs text-neutral-500 bg-neutral-900 px-2 py-1 rounded-full">{garments.length} items</span>
          </div>

          <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
            <GarmentUploader onUploadComplete={fetchGarments} />
            <GarmentSelector
              garments={garments}
              selectedId={selectedGarmentId}
              onSelect={(id) => setSelectedGarmentId(id)}
            />
          </div>
        </div>

        {/* Right Panel: Try-On Area (Fixed) */}
        <div className="lg:col-span-8 h-full">
          <MagicMirror selectedGarmentId={selectedGarmentId} />
        </div>
      </div>
    </main>
  );
}
