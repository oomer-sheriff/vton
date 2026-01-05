"use client";

import { Garment } from "@/types";
import { Check } from "lucide-react";
import Image from "next/image";

interface Props {
    garments: Garment[];
    selectedId: string | null;
    onSelect: (id: string) => void;
}

export default function GarmentSelector({ garments, selectedId, onSelect }: Props) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-fr">
            {garments.map((g) => (
                <div
                    key={g.id}
                    onClick={() => onSelect(g.id)}
                    className={`relative aspect-[3/4] rounded-xl overflow-hidden cursor-pointer border-2 transition-all ${selectedId === g.id ? "border-purple-500 shadow-lg shadow-purple-500/20" : "border-transparent hover:border-neutral-700"
                        }`}
                >
                    {/* Use standard img tag for local dev if Next/Image config is tricky with localhost usually */}
                    {/* But we configured backend media serving in main.py? Wait, we need to serve media files! */}
                    {/* Assuming we need to mount media/processed statically or use huge base64? 
              For now let's point to localhost:8000 media path if we serve it.
              Actually, I haven't added StaticFiles mount yet in backend! 
              I should do that. For now, let's assume standard path structure.
          */}
                    <img
                        src={`http://localhost:8000/${g.image}`}
                        alt="Garment"
                        className="w-full h-full object-cover bg-neutral-800"
                    />

                    {selectedId === g.id && (
                        <div className="absolute top-2 right-2 bg-purple-500 text-white p-1 rounded-full">
                            <Check className="w-4 h-4" />
                        </div>
                    )}

                    <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-3 pt-8">
                        <p className="text-xs text-white capitalize font-medium">
                            {g.metadata?.category || "Unknown"}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
}
