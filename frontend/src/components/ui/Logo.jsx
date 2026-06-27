import {Home} from 'lucide-react'
export default function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
        <Home className='w-10 h-10'/>
      </div>
      <span className="font-bold text-slate-900 tracking-tight">BookMyVenue</span>
    </div>
  );
}
