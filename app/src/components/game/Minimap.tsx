import { useGameState } from '@/hooks/useGameState';
import { employees } from '@/data/employees';

export function Minimap() {
  const { playerPosition, nearDoor } = useGameState();
  
  // Scale factor for minimap (office is roughly 30x24, minimap is 150x120)
  const scaleX = 150 / 30;
  const scaleZ = 120 / 24;
  
  // Convert world position to minimap position
  const playerX = (playerPosition.x + 15) * scaleX;
  const playerY = (playerPosition.z + 12) * scaleZ;

  return (
    <div className="absolute top-4 right-4 w-[150px] h-[120px] bg-card/90 rounded-lg border-2 border-border shadow-lg overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-secondary/50" />
      
      {/* Hallway */}
      <div 
        className="absolute bg-amber-200/60"
        style={{
          left: '25%',
          right: '25%',
          top: 0,
          bottom: 0,
        }}
      />
      
      {/* Left offices */}
      <div 
        className="absolute bg-muted border border-border"
        style={{
          left: 2,
          top: 2,
          width: '35%',
          height: '45%',
        }}
      >
        <span className="text-[6px] text-muted-foreground p-0.5 block truncate">Sarah</span>
      </div>
      <div 
        className="absolute bg-muted border border-border"
        style={{
          left: 2,
          bottom: 2,
          width: '35%',
          height: '45%',
        }}
      >
        <span className="text-[6px] text-muted-foreground p-0.5 block truncate">James</span>
      </div>
      
      {/* Right offices */}
      <div 
        className="absolute bg-muted border border-border"
        style={{
          right: 2,
          top: 2,
          width: '35%',
          height: '45%',
        }}
      >
        <span className="text-[6px] text-muted-foreground p-0.5 block truncate">Alex</span>
      </div>
      <div 
        className="absolute bg-muted border border-border"
        style={{
          right: 2,
          bottom: 2,
          width: '35%',
          height: '45%',
        }}
      >
        <span className="text-[6px] text-muted-foreground p-0.5 block truncate">Peter</span>
      </div>
      
      {/* CEO area indicator */}
      <div 
        className="absolute bg-primary/20 border border-primary/40"
        style={{
          left: '35%',
          right: '35%',
          top: 4,
          height: 15,
        }}
      >
        <span className="text-[5px] text-primary p-0.5 block text-center">CEO</span>
      </div>
      
      {/* Player dot */}
      <div 
        className="absolute w-2.5 h-2.5 bg-primary rounded-full border border-primary-foreground shadow-md transition-all duration-75"
        style={{
          left: playerX - 5,
          top: playerY - 5,
        }}
      />
      
      {/* Door highlights */}
      {nearDoor && (
        <div className="absolute bottom-1 left-1/2 -translate-x-1/2">
          <span className="text-[7px] text-primary font-medium bg-primary/10 px-1 rounded">
            Near: {employees.find(e => e.id === nearDoor)?.name.split(' ')[0]}
          </span>
        </div>
      )}
    </div>
  );
}
