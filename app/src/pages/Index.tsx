import { Scene } from '@/components/game/Scene';
import { Minimap } from '@/components/game/Minimap';
import { GameHUD } from '@/components/game/GameHUD';
import { VideoCall } from '@/components/ui/VideoCall';
import { CEODesk } from '@/components/ui/CEODesk';
import { useGameState } from '@/hooks/useGameState';

const Index = () => {
  const { mode } = useGameState();

  return (
    <div className="relative w-full h-screen overflow-hidden bg-background">
      {/* 3D Game Scene */}
      <Scene />
      
      {/* Game UI Overlay */}
      {mode === 'exploring' && (
        <>
          <Minimap />
          <GameHUD />
        </>
      )}
      
      {/* Video Call Interface */}
      <VideoCall />
      
      {/* CEO Desk Interface */}
      <CEODesk />
      
      {/* Title overlay for exploration mode */}
      {mode === 'exploring' && (
        <div className="absolute top-4 left-4 bg-card/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-border shadow-lg">
          <h1 className="text-lg font-bold text-foreground">Virtual Office</h1>
          <p className="text-xs text-muted-foreground">Explore and meet your team</p>
        </div>
      )}
    </div>
  );
};

export default Index;
