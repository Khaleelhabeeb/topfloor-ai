import { useGameState } from '@/hooks/useGameState';
import { employees } from '@/data/employees';

export function GameHUD() {
  const { nearDoor, nearChair, mode } = useGameState();

  if (mode !== 'exploring') return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Interaction prompts */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        {nearDoor && (
          <div className="bg-card/95 backdrop-blur-sm px-4 py-2 rounded-lg border border-border shadow-lg animate-fade-in">
            <p className="text-sm font-medium text-foreground">
              Press <kbd className="px-2 py-0.5 bg-primary text-primary-foreground rounded text-xs mx-1">E</kbd> 
              to enter {employees.find(e => e.id === nearDoor)?.name}'s office
            </p>
          </div>
        )}
        
        {nearChair && !nearDoor && (
          <div className="bg-card/95 backdrop-blur-sm px-4 py-2 rounded-lg border border-border shadow-lg animate-fade-in">
            <p className="text-sm font-medium text-foreground">
              Press <kbd className="px-2 py-0.5 bg-primary text-primary-foreground rounded text-xs mx-1">E</kbd> 
              to sit at the CEO desk
            </p>
          </div>
        )}
      </div>
      
      {/* Controls hint */}
      <div className="absolute bottom-4 left-4 bg-card/80 backdrop-blur-sm px-3 py-2 rounded-lg border border-border">
        <p className="text-xs text-muted-foreground">
          <span className="font-medium">WASD</span> or <span className="font-medium">Arrow Keys</span> to move
        </p>
      </div>
    </div>
  );
}
