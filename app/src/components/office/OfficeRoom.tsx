import { useRef } from 'react';
import * as THREE from 'three';
import { Text } from '@react-three/drei';

interface OfficeRoomProps {
  position: [number, number, number];
  size?: [number, number, number];
  name: string;
  color?: string;
  isCEO?: boolean;
  doorDirection?: 'north' | 'south' | 'east' | 'west';
}

export function OfficeRoom({ 
  position, 
  size = [6, 3, 6], 
  name, 
  color = '#8B7355',
  isCEO = false,
  doorDirection = 'south'
}: OfficeRoomProps) {
  const roomSize = isCEO ? [8, 3.5, 8] as [number, number, number] : size;
  
  return (
    <group position={position}>
      {/* Floor - Realistic office carpet/wood */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} receiveShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color={isCEO ? '#2C1810' : '#A0937D'} />
      </mesh>

      {/* Ceiling - Professional drop ceiling */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, roomSize[1], 0]} receiveShadow castShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color="#F8F8F8" />
      </mesh>

      {/* Ceiling grid pattern for realism */}
      {Array.from({ length: 3 }, (_, i) => (
        <mesh key={`grid-x-${i}`} position={[(-roomSize[0]/2) + (i + 1) * (roomSize[0]/4), roomSize[1] - 0.02, 0]} castShadow>
          <boxGeometry args={[0.02, 0.01, roomSize[2]]} />
          <meshStandardMaterial color="#E0E0E0" />
        </mesh>
      ))}
      {Array.from({ length: 3 }, (_, i) => (
        <mesh key={`grid-z-${i}`} position={[0, roomSize[1] - 0.02, (-roomSize[2]/2) + (i + 1) * (roomSize[2]/4)]} castShadow>
          <boxGeometry args={[roomSize[0], 0.01, 0.02]} />
          <meshStandardMaterial color="#E0E0E0" />
        </mesh>
      ))}

      {/* Walls - only render walls that don't have doors */}
      {/* Back Wall (opposite to door) */}
      {doorDirection !== 'north' && (
        <mesh position={[0, roomSize[1] / 2, -roomSize[2] / 2]} receiveShadow castShadow>
          <boxGeometry args={[roomSize[0], roomSize[1], 0.15]} />
          <meshStandardMaterial color={color} />
        </mesh>
      )}
      
      {/* Front Wall (door side) - only render if door is not on this side */}
      {doorDirection !== 'south' && (
        <mesh position={[0, roomSize[1] / 2, roomSize[2] / 2]} receiveShadow castShadow>
          <boxGeometry args={[roomSize[0], roomSize[1], 0.15]} />
          <meshStandardMaterial color={color} />
        </mesh>
      )}

      {/* Left Wall */}
      {doorDirection !== 'west' && (
        <mesh position={[-roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow castShadow>
          <boxGeometry args={[0.15, roomSize[1], roomSize[2]]} />
          <meshStandardMaterial color={color} />
        </mesh>
      )}

      {/* Right Wall */}
      {doorDirection !== 'east' && (
        <mesh position={[roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow castShadow>
          <boxGeometry args={[0.15, roomSize[1], roomSize[2]]} />
          <meshStandardMaterial color={color} />
        </mesh>
      )}

      {/* Baseboards for realism */}
      <mesh position={[0, 0.05, -roomSize[2] / 2 + 0.08]} castShadow>
        <boxGeometry args={[roomSize[0], 0.1, 0.05]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[-roomSize[0] / 2 + 0.08, 0.05, 0]} castShadow>
        <boxGeometry args={[0.05, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[roomSize[0] / 2 - 0.08, 0.05, 0]} castShadow>
        <boxGeometry args={[0.05, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>

      {/* Desk */}
      <Desk position={[0, 0, -1.5]} isCEO={isCEO} />

      {/* Chair */}
      <Chair position={[0, 0, 0.5]} isCEO={isCEO} />

      {/* Name Plate */}
      <Text
        position={[0, 2.5, -roomSize[2] / 2 + 0.1]}
        fontSize={0.3}
        color="#FFFFFF"
        anchorX="center"
        anchorY="middle"
      >
        {name}
      </Text>

      {/* Decorative elements */}
      <Plant position={[roomSize[0] / 2 - 0.5, 0, roomSize[2] / 2 - 0.5]} />
      
      {/* Computer Monitor on desk */}
      <Monitor position={[0, 0.85, -1.8]} />

      {/* Office Lighting - More realistic */}
      <pointLight 
        position={[0, roomSize[1] - 0.2, 0]} 
        intensity={isCEO ? 2.5 : 2.0} 
        distance={8} 
        color="#fff5e6" 
        castShadow 
      />
      <pointLight 
        position={[roomSize[0]/3, roomSize[1] - 0.3, roomSize[2]/3]} 
        intensity={1.0} 
        distance={6} 
        color="#ffcc88" 
      />
      <pointLight 
        position={[-roomSize[0]/3, roomSize[1] - 0.3, -roomSize[2]/3]} 
        intensity={1.0} 
        distance={6} 
        color="#ffcc88" 
      />

      {/* Ceiling Light Fixtures - More realistic */}
      <group position={[0, roomSize[1] - 0.08, 0]}>
        <mesh castShadow>
          <boxGeometry args={[1.5, 0.06, 0.8]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.2} />
        </mesh>
        {/* Light fixture frame */}
        <mesh position={[0, 0.03, 0]} castShadow>
          <boxGeometry args={[1.6, 0.02, 0.9]} />
          <meshStandardMaterial color="#C0C0C0" />
        </mesh>
      </group>

      {/* Additional office furniture for realism */}
      {/* Filing cabinet */}
      <group position={[roomSize[0]/2 - 0.8, 0, -roomSize[2]/2 + 0.8]}>
        <mesh position={[0, 0.6, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.4, 1.2, 0.6]} />
          <meshStandardMaterial color="#D3D3D3" />
        </mesh>
        {/* Drawer handles */}
        <mesh position={[0.21, 0.8, 0]} castShadow>
          <boxGeometry args={[0.02, 0.05, 0.3]} />
          <meshStandardMaterial color="#808080" />
        </mesh>
        <mesh position={[0.21, 0.4, 0]} castShadow>
          <boxGeometry args={[0.02, 0.05, 0.3]} />
          <meshStandardMaterial color="#808080" />
        </mesh>
      </group>

      {/* Waste basket */}
      <group position={[0.8, 0, 0.8]}>
        <mesh position={[0, 0.15, 0]} castShadow>
          <cylinderGeometry args={[0.15, 0.12, 0.3, 12]} />
          <meshStandardMaterial color="#2F4F4F" />
        </mesh>
      </group>

      {/* Wall art/whiteboard */}
      <mesh position={[-roomSize[0]/2 + 0.08, 1.5, -1]} castShadow>
        <boxGeometry args={[0.02, 0.6, 0.8]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
    </group>
  );
}

function Desk({ position, isCEO }: { position: [number, number, number]; isCEO: boolean }) {
  const width = isCEO ? 2.5 : 1.8;
  const depth = isCEO ? 1.2 : 0.9;
  
  return (
    <group position={position}>
      {/* Desktop */}
      <mesh position={[0, 0.75, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, 0.05, depth]} />
        <meshStandardMaterial color={isCEO ? '#2D1B0E' : '#8B4513'} />
      </mesh>
      
      {/* Desktop edge trim */}
      <mesh position={[0, 0.77, 0]} castShadow>
        <boxGeometry args={[width + 0.02, 0.01, depth + 0.02]} />
        <meshStandardMaterial color={isCEO ? '#1A0F08' : '#654321'} />
      </mesh>
      
      {/* Legs */}
      {[[-width/2 + 0.1, 0.375, -depth/2 + 0.1], 
        [width/2 - 0.1, 0.375, -depth/2 + 0.1],
        [-width/2 + 0.1, 0.375, depth/2 - 0.1],
        [width/2 - 0.1, 0.375, depth/2 - 0.1]
      ].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <boxGeometry args={[0.08, 0.75, 0.08]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
      ))}
      
      {/* Desk drawers */}
      <mesh position={[width/2 - 0.3, 0.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.5, 0.4, depth - 0.1]} />
        <meshStandardMaterial color={isCEO ? '#3D2817' : '#A0522D'} />
      </mesh>
      
      {/* Drawer handles */}
      <mesh position={[width/2 - 0.05, 0.6, 0]} castShadow>
        <boxGeometry args={[0.02, 0.05, 0.15]} />
        <meshStandardMaterial color="#C0C0C0" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[width/2 - 0.05, 0.4, 0]} castShadow>
        <boxGeometry args={[0.02, 0.05, 0.15]} />
        <meshStandardMaterial color="#C0C0C0" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Keyboard tray */}
      <mesh position={[0, 0.65, depth/4]} castShadow receiveShadow>
        <boxGeometry args={[0.6, 0.02, 0.3]} />
        <meshStandardMaterial color="#F5F5F5" />
      </mesh>
    </group>
  );
}

function Chair({ position, isCEO }: { position: [number, number, number]; isCEO: boolean }) {
  return (
    <group position={position}>
      {/* Seat */}
      <mesh position={[0, 0.45, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.5, 0.08, 0.5]} />
        <meshStandardMaterial color={isCEO ? '#2D2D2D' : '#4169E1'} />
      </mesh>
      
      {/* Seat cushion detail */}
      <mesh position={[0, 0.49, 0]} castShadow>
        <boxGeometry args={[0.45, 0.02, 0.45]} />
        <meshStandardMaterial color={isCEO ? '#1A1A1A' : '#1E90FF'} />
      </mesh>
      
      {/* Backrest */}
      <mesh position={[0, 0.8, -0.22]} castShadow receiveShadow>
        <boxGeometry args={[0.5, 0.6, 0.08]} />
        <meshStandardMaterial color={isCEO ? '#2D2D2D' : '#4169E1'} />
      </mesh>
      
      {/* Armrests */}
      <mesh position={[-0.25, 0.65, -0.05]} castShadow>
        <boxGeometry args={[0.05, 0.05, 0.3]} />
        <meshStandardMaterial color="#2d2d2d" />
      </mesh>
      <mesh position={[0.25, 0.65, -0.05]} castShadow>
        <boxGeometry args={[0.05, 0.05, 0.3]} />
        <meshStandardMaterial color="#2d2d2d" />
      </mesh>
      
      {/* Base */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.25, 0.25, 0.05, 16]} />
        <meshStandardMaterial color="#2d2d2d" />
      </mesh>
      
      {/* Pole */}
      <mesh position={[0, 0.3, 0]} castShadow>
        <cylinderGeometry args={[0.04, 0.04, 0.3, 8]} />
        <meshStandardMaterial color="#444444" />
      </mesh>
      
      {/* Wheels */}
      {[0, Math.PI/2.5, Math.PI*2/2.5, Math.PI*3/2.5, Math.PI*4/2.5].map((angle, i) => (
        <mesh key={i} position={[Math.cos(angle) * 0.2, 0.05, Math.sin(angle) * 0.2]} castShadow>
          <cylinderGeometry args={[0.03, 0.03, 0.02, 8]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
      ))}
    </group>
  );
}

function Plant({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Pot */}
      <mesh position={[0, 0.15, 0]} castShadow>
        <cylinderGeometry args={[0.15, 0.12, 0.3, 16]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      
      {/* Plant */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <sphereGeometry args={[0.25, 8, 8]} />
        <meshStandardMaterial color="#228B22" />
      </mesh>
    </group>
  );
}

function Monitor({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Monitor bezel */}
      <mesh position={[0, 0.2, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.65, 0.45, 0.04]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      
      {/* Screen */}
      <mesh position={[0, 0.2, 0.021]}>
        <planeGeometry args={[0.58, 0.38]} />
        <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.4} />
      </mesh>
      
      {/* Screen content simulation */}
      <mesh position={[0, 0.25, 0.022]}>
        <planeGeometry args={[0.5, 0.08]} />
        <meshStandardMaterial color="#FFFFFF" emissive="#FFFFFF" emissiveIntensity={0.2} />
      </mesh>
      <mesh position={[0, 0.15, 0.022]}>
        <planeGeometry args={[0.45, 0.15]} />
        <meshStandardMaterial color="#00FF00" emissive="#00FF00" emissiveIntensity={0.1} />
      </mesh>
      
      {/* Stand */}
      <mesh position={[0, -0.05, 0.1]} castShadow>
        <boxGeometry args={[0.08, 0.1, 0.15]} />
        <meshStandardMaterial color="#2d2d2d" />
      </mesh>
      
      {/* Base */}
      <mesh position={[0, -0.1, 0.1]} castShadow>
        <boxGeometry args={[0.25, 0.02, 0.2]} />
        <meshStandardMaterial color="#2d2d2d" />
      </mesh>
      
      {/* Power button */}
      <mesh position={[0.3, 0.1, 0.021]} castShadow>
        <cylinderGeometry args={[0.01, 0.01, 0.005, 8]} />
        <meshStandardMaterial color="#00FF00" emissive="#00FF00" emissiveIntensity={0.5} />
      </mesh>
    </group>
  );
}
