import { useRef } from 'react';
import * as THREE from 'three';
import { Text } from '@react-three/drei';

interface OfficeRoomProps {
  position: [number, number, number];
  size?: [number, number, number];
  name: string;
  color?: string;
  isCEO?: boolean;
}

export function OfficeRoom({ 
  position, 
  size = [6, 3, 6], 
  name, 
  color = '#8B7355',
  isCEO = false 
}: OfficeRoomProps) {
  const roomSize = isCEO ? [8, 3.5, 8] as [number, number, number] : size;
  
  return (
    <group position={position}>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} receiveShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color={isCEO ? '#2C1810' : '#3D2817'} />
      </mesh>

      {/* Back Wall */}
      <mesh position={[0, roomSize[1] / 2, -roomSize[2] / 2]} receiveShadow>
        <boxGeometry args={[roomSize[0], roomSize[1], 0.15]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Left Wall */}
      <mesh position={[-roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow>
        <boxGeometry args={[0.15, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Right Wall */}
      <mesh position={[roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow>
        <boxGeometry args={[0.15, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color={color} />
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
        <meshStandardMaterial color={isCEO ? '#1a0f0a' : '#4a3728'} />
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
    </group>
  );
}

function Chair({ position, isCEO }: { position: [number, number, number]; isCEO: boolean }) {
  return (
    <group position={position}>
      {/* Seat */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[0.5, 0.08, 0.5]} />
        <meshStandardMaterial color={isCEO ? '#1a1a1a' : '#333333'} />
      </mesh>
      
      {/* Backrest */}
      <mesh position={[0, 0.8, -0.22]} castShadow>
        <boxGeometry args={[0.5, 0.6, 0.08]} />
        <meshStandardMaterial color={isCEO ? '#1a1a1a' : '#333333'} />
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
      {/* Screen */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <boxGeometry args={[0.6, 0.4, 0.03]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      
      {/* Screen display */}
      <mesh position={[0, 0.2, 0.02]}>
        <planeGeometry args={[0.55, 0.35]} />
        <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.3} />
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
    </group>
  );
}
