import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import { Folder } from './types';

interface InteractiveFolderProps {
  folder: Folder;
  position: [number, number, number];
  onSelect: (folder: Folder) => void;
}

export function InteractiveFolder({ folder, position, onSelect }: InteractiveFolderProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 3) * 0.02;
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={() => onSelect(folder)}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
      >
        {/* Folder base */}
        <boxGeometry args={[0.25, 0.03, 0.35]} />
        <meshStandardMaterial 
          color={folder.color} 
          emissive={hovered ? folder.color : '#000000'}
          emissiveIntensity={hovered ? 0.3 : 0}
        />
      </mesh>
      
      {/* Folder tab */}
      <mesh position={[-0.05, 0.025, -0.15]} castShadow>
        <boxGeometry args={[0.1, 0.02, 0.05]} />
        <meshStandardMaterial color={folder.color} />
      </mesh>

      {/* Label */}
      <Text
        position={[0, 0.05, 0]}
        fontSize={0.04}
        color="#FFFFFF"
        anchorX="center"
        anchorY="middle"
        rotation={[-Math.PI / 2, 0, 0]}
      >
        {folder.name}
      </Text>

      {/* Hover indicator */}
      {hovered && (
        <Text
          position={[0, 0.15, 0]}
          fontSize={0.06}
          color="#FFD700"
          anchorX="center"
          anchorY="middle"
        >
          Click to Open
        </Text>
      )}
    </group>
  );
}
