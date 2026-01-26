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
import { CollisionSystem } from './CollisionSystem';
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
  const [playerPosition, setPlayerPosition] = useState<THREE.Vector3>(new THREE.Vector3(0, 1.7, 10));
  const [doorStates, setDoorStates] = useState<Map<string, boolean>>(new Map());
  
  // Initialize collision system
  const collisionSystemRef = useRef<CollisionSystem>(new CollisionSystem());

  const checkRoomEntry = useCallback((position: THREE.Vector3) => {
    setPlayerPosition(position);
    
    const currentRoom = collisionSystemRef.current.getPlayerRoom(position);
    
    // Handle room transitions
    if (currentRoom === 'office1' && state.currentRoom !== 'office1' && !state.activeMember) {
      setState(prev => ({ ...prev, currentRoom: 'office1', activeMember: teamMembers[0] }));
    } else if (currentRoom === 'office2' && state.currentRoom !== 'office2' && !state.activeMember) {
      setState(prev => ({ ...prev, currentRoom: 'office2', activeMember: teamMembers[1] }));
    } else if (currentRoom === 'office3' && state.currentRoom !== 'office3' && !state.activeMember) {
      setState(prev => ({ ...prev, currentRoom: 'office3', activeMember: teamMembers[2] }));
    } else if (currentRoom === 'office4' && state.currentRoom !== 'office4' && !state.activeMember) {
      setState(prev => ({ ...prev, currentRoom: 'office4', activeMember: teamMembers[3] }));
    } else if (currentRoom === 'ceo' && state.currentRoom !== 'ceo') {
      setState(prev => ({ ...prev, currentRoom: 'ceo' }));
    } else if (currentRoom === 'hallway' && state.currentRoom !== 'hallway') {
      setState(prev => ({ ...prev, currentRoom: 'hallway' }));
    }
  }, [state.currentRoom, state.activeMember]);

  const handleDoorInteract = useCallback((doorId: string) => {
    const collisionSystem = collisionSystemRef.current;
    const isOpen = collisionSystem.isDoorOpen(doorId);
    
    if (isOpen) {
      collisionSystem.closeDoor(doorId);
    } else {
      collisionSystem.openDoor(doorId);
    }
    
    // Update door states for rendering
    setDoorStates(new Map(collisionSystem.getAllDoors().map(door => [door.id, door.isOpen])));
  }, []);

  const handleFolderSelect = useCallback((folder: Folder) => {
    setState(prev => ({ ...prev, activeFolder: folder }));
  }, []);

  const handleCloseChat = useCallback(() => {
    setState(prev => ({ ...prev, activeMember: null }));
  }, []);

  const handleCloseDocument = useCallback(() => {
    setState(prev => ({ ...prev, activeFolder: null }));
  }, []);

  // Handle ESC key to close overlays and E key for door interaction
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code === 'Escape') {
        if (state.activeFolder) {
          handleCloseDocument();
        } else if (state.activeMember) {
          handleCloseChat();
        }
      }
      // E key to sit in CEO office or interact with doors
      if (event.code === 'KeyE') {
        if (state.currentRoom === 'ceo' && !state.isSeated) {
          setState(prev => ({ ...prev, isSeated: true }));
        } else {
          // Check if player is near any door and interact with it
          const collisionSystem = collisionSystemRef.current;
          const doors = collisionSystem.getAllDoors();
          
          for (const door of doors) {
            const distance = playerPosition.distanceTo(door.position);
            if (distance < 2) {
              handleDoorInteract(door.id);
              break;
            }
          }
        }
      }
      // Q key to stand up
      if (event.code === 'KeyQ' && state.isSeated) {
        setState(prev => ({ ...prev, isSeated: false }));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state.activeFolder, state.activeMember, state.currentRoom, state.isSeated, playerPosition, handleCloseChat, handleCloseDocument, handleDoorInteract]);

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
              <p>• <kbd className="px-1 bg-muted rounded">E</kbd> - Interact with doors / Sit in CEO chair</p>
              <p>• <kbd className="px-1 bg-muted rounded">Q</kbd> - Stand up</p>
              <p>• <kbd className="px-1 bg-muted rounded">ESC</kbd> - Close dialogs / unlock mouse</p>
            </div>
            <p className="text-sm text-muted-foreground">
              Approach doors to see interaction prompts. Walk into team offices to see their info. Visit the CEO office to access folders.
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
             state.currentRoom === 'office1' ? 'James Wilson\'s Office' :
             state.currentRoom === 'office2' ? 'Sarah Miller\'s Office' :
             state.currentRoom === 'office3' ? 'Alex Chen\'s Office' :
             state.currentRoom === 'office4' ? 'Peter Rodriguez\'s Office' :
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
        WASD to move • Click to look • E to interact
      </div>

      {/* 3D Canvas */}
      <Canvas shadows camera={{ fov: 75, near: 0.1, far: 1000 }}>
        <Sky sunPosition={[100, 20, 100]} />
        <ambientLight intensity={0.6} />
        <directionalLight
          position={[10, 20, 10]}
          intensity={1.2}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />

        {/* Main Hallway */}
        <Hallway 
          onDoorInteract={handleDoorInteract}
          doorStates={doorStates}
          playerPosition={playerPosition}
        />

        {/* Team Member Offices */}
        <OfficeRoom
          position={[-6, 0, -5]}
          name="James Wilson"
          color="#8B8680"
          doorDirection="east"
        />
        <OfficeRoom
          position={[-6, 0, 5]}
          name="Sarah Miller"
          color="#9B8B9B"
          doorDirection="east"
        />
        <OfficeRoom
          position={[6, 0, 0]}
          name="Alex Chen"
          color="#B8A082"
          doorDirection="west"
        />
        <OfficeRoom
          position={[6, 0, 10]}
          name="Peter Rodriguez"
          color="#A8B8A0"
          doorDirection="west"
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
          collisionSystem={collisionSystemRef.current}
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
