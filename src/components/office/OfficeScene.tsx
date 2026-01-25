import { useRef, useState, useCallback, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Sky } from '@react-three/drei';
import * as THREE from 'three';
import { Hallway } from './Hallway';
import { OfficeRoom } from './OfficeRoom';
import { CEOOffice } from './CEOOffice';
import { FirstPersonControls } from './FirstPersonControls';
import { ChatInterface } from './ChatInterface';
import { DocumentViewer } from './DocumentViewer';
import { teamMembers } from './data';
import { TeamMember, Folder, OfficeState } from './types';

export function OfficeScene() {
  const [state, setState] = useState<OfficeState>({
    currentRoom: 'hallway',
    isSeated: false,
    activeFolder: null,
    activeMember: null
  });

  const [showInstructions, setShowInstructions] = useState(true);

  const checkRoomEntry = useCallback((position: THREE.Vector3) => {
    // Check if player entered Developer office (left side, z around -5)
    if (position.x < -3 && position.z > -8 && position.z < -2) {
      if (state.currentRoom !== 'office1' && !state.activeMember) {
        setState(prev => ({ ...prev, currentRoom: 'office1', activeMember: teamMembers[0] }));
      }
    }
    // Check if player entered Designer office (left side, z around 5)
    else if (position.x < -3 && position.z > 2 && position.z < 8) {
      if (state.currentRoom !== 'office2' && !state.activeMember) {
        setState(prev => ({ ...prev, currentRoom: 'office2', activeMember: teamMembers[1] }));
      }
    }
    // Check if player entered Marketing office (right side)
    else if (position.x > 3 && position.z > -3 && position.z < 3) {
      if (state.currentRoom !== 'office3' && !state.activeMember) {
        setState(prev => ({ ...prev, currentRoom: 'office3', activeMember: teamMembers[2] }));
      }
    }
    // Check if player entered CEO office (far end)
    else if (position.z < -12) {
      if (state.currentRoom !== 'ceo') {
        setState(prev => ({ ...prev, currentRoom: 'ceo' }));
      }
    }
    // Back in hallway
    else if (Math.abs(position.x) < 2 && position.z > -12) {
      if (state.currentRoom !== 'hallway') {
        setState(prev => ({ ...prev, currentRoom: 'hallway' }));
      }
    }
  }, [state.currentRoom, state.activeMember]);

  const handleFolderSelect = useCallback((folder: Folder) => {
    setState(prev => ({ ...prev, activeFolder: folder }));
  }, []);

  const handleCloseChat = useCallback(() => {
    setState(prev => ({ ...prev, activeMember: null }));
  }, []);

  const handleCloseDocument = useCallback(() => {
    setState(prev => ({ ...prev, activeFolder: null }));
  }, []);

  // Handle ESC key to close overlays
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code === 'Escape') {
        if (state.activeFolder) {
          handleCloseDocument();
        } else if (state.activeMember) {
          handleCloseChat();
        }
      }
      // E key to sit in CEO office
      if (event.code === 'KeyE' && state.currentRoom === 'ceo' && !state.isSeated) {
        setState(prev => ({ ...prev, isSeated: true }));
      }
      // Q key to stand up
      if (event.code === 'KeyQ' && state.isSeated) {
        setState(prev => ({ ...prev, isSeated: false }));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state.activeFolder, state.activeMember, state.currentRoom, state.isSeated, handleCloseChat, handleCloseDocument]);

  const controlsEnabled = !state.activeMember && !state.activeFolder;

  return (
    <div className="w-full h-screen bg-background relative">
      {/* Instructions overlay */}
      {showInstructions && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="bg-card p-8 rounded-xl max-w-md text-center space-y-4 border border-border">
            <h1 className="text-2xl font-bold text-foreground">Virtual Office</h1>
            <div className="text-muted-foreground space-y-2 text-left">
              <p><strong>Controls:</strong></p>
              <p>• <kbd className="px-1 bg-muted rounded">WASD</kbd> - Move around</p>
              <p>• <kbd className="px-1 bg-muted rounded">Mouse</kbd> - Look around (click to lock)</p>
              <p>• <kbd className="px-1 bg-muted rounded">E</kbd> - Sit in CEO chair</p>
              <p>• <kbd className="px-1 bg-muted rounded">Q</kbd> - Stand up</p>
              <p>• <kbd className="px-1 bg-muted rounded">ESC</kbd> - Close dialogs / unlock mouse</p>
            </div>
            <p className="text-sm text-muted-foreground">
              Walk into team offices to see their info. Visit the CEO office to access folders.
            </p>
            <button 
              onClick={() => setShowInstructions(false)}
              className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
            >
              Enter Office
            </button>
          </div>
        </div>
      )}

      {/* HUD */}
      <div className="absolute top-4 left-4 z-40 bg-card/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
        <p className="text-sm text-foreground">
          <span className="text-muted-foreground">Location:</span>{' '}
          <span className="font-medium capitalize">
            {state.currentRoom === 'ceo' ? 'CEO Office' : 
             state.currentRoom === 'hallway' ? 'Hallway' :
             state.currentRoom.replace('office', 'Office ')}
          </span>
        </p>
        {state.isSeated && (
          <p className="text-xs text-muted-foreground mt-1">
            Press Q to stand up
          </p>
        )}
      </div>

      {/* Mini controls hint */}
      <div className="absolute bottom-4 left-4 z-40 bg-card/80 backdrop-blur-sm px-3 py-2 rounded-lg border border-border text-xs text-muted-foreground">
        WASD to move • Click to look
      </div>

      {/* 3D Canvas */}
      <Canvas shadows camera={{ fov: 75, near: 0.1, far: 1000 }}>
        <Sky sunPosition={[100, 20, 100]} />
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[10, 20, 10]}
          intensity={0.8}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />

        {/* Main Hallway */}
        <Hallway />

        {/* Team Member Offices */}
        <OfficeRoom
          position={[-6, 0, -5]}
          name="Alex Chen - Developer"
          color="#6B7280"
        />
        <OfficeRoom
          position={[-6, 0, 5]}
          name="Sarah Miller - Designer"
          color="#8B5CF6"
        />
        <OfficeRoom
          position={[6, 0, 0]}
          name="Jordan Park - Marketing"
          color="#F59E0B"
        />

        {/* CEO Office */}
        <CEOOffice
          position={[0, 0, -18]}
          onFolderSelect={handleFolderSelect}
          isSeated={state.isSeated}
        />

        {/* First Person Controls */}
        <FirstPersonControls
          speed={4}
          enabled={controlsEnabled}
          onPositionChange={checkRoomEntry}
        />
      </Canvas>

      {/* Chat Interface Overlay */}
      {state.activeMember && (
        <ChatInterface member={state.activeMember} onClose={handleCloseChat} />
      )}

      {/* Document Viewer Overlay */}
      {state.activeFolder && (
        <DocumentViewer folder={state.activeFolder} onClose={handleCloseDocument} />
      )}
    </div>
  );
}
