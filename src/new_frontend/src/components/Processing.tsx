import { Loader2 } from "lucide-react";

interface Props {
  statusText: string;
}

export default function Processing({ statusText }: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-5">
      <div className="relative">
        <div className="w-14 h-14 rounded-2xl bg-cyan-50 flex items-center justify-center">
          <Loader2 className="w-7 h-7 text-cyan-600 animate-spin" />
        </div>
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">Obdelujem dokument</p>
        <p className="text-xs text-gray-400 mt-1 max-w-xs">{statusText}</p>
      </div>
    </div>
  );
}
