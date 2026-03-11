import { Loader2 } from "lucide-react";

interface Props {
  statusText: string;
}

export default function Processing({ statusText }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      <div className="text-center">
        <p className="text-lg font-medium text-gray-700">Obdelujem dokument</p>
        <p className="text-sm text-gray-500 mt-1">{statusText}</p>
      </div>
    </div>
  );
}
