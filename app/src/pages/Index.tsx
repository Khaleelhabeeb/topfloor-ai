import { Scene } from '@/components/game/Scene';
import { Minimap } from '@/components/game/Minimap';
import { GameHUD } from '@/components/game/GameHUD';
import { VideoCall } from '@/components/ui/VideoCall';
import { CEODesk } from '@/components/ui/CEODesk';
import { useGameState } from '@/hooks/useGameState';
import { useAuth } from '@/hooks/useAuth';
import { useAgents } from '@/hooks/useAgents';
import { Button } from '@/components/ui/button';
import { LogOut, Loader2 } from 'lucide-react';
import { useEffect } from 'react';

const Index = () => {
  const { mode } = useGameState();
  const { logout, user } = useAuth();
  const { fetchAgents, isLoading: agentsLoading, error: agentsError } = useAgents();

  // Fetch agents on mount
  useEffect(() => {
    fetchAgents().catch((error) => {
      console.error('Failed to fetch agents:', error);
    });
  }, [fetchAgents]);

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  // Show loading state while fetching agents
  if (agentsLoading) {
    return (
      <div className="relative w-full h-screen overflow-hidden bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-sm text-muted-foreground">Loading agents...</p>
        </div>
      </div>
    );
  }

  // Show error state if agents failed to load
  if (agentsError) {
    return (
      <div className="relative w-full h-screen overflow-hidden bg-background flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <p className="text-sm text-destructive">{agentsError}</p>
          <Button onClick={() => fetchAgents()}>Retry</Button>
        </div>
      </div>
    );
  }

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
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-lg font-bold text-foreground">Virtual Office</h1>
              <p className="text-xs text-muted-foreground">
                Logged in as {user?.email}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="h-8 w-8"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
