import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';

interface DoorProps {
  position: [number, number, number];
  rotation?: [number, number, number];
  isOpen?: boolean;
  onInteract?: () => void;
  label?: string;
  playerPosition?: THREE.Vector3;
}

export function Door({ 
  position, 
  rotation = [0, 0, 0], 
  isOpen = false, 
  onInteract,
  label,
  playerPosition 
}: DoorProps) {
  const doorRef = useRef<THREE.Group>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);

  // Check if player is near door
  useFrame(() => {
    if (playerPosition && doorRef.current) {
      const doorPosition = new THREE.Vector3(...position);
      const distance = playerPosition.distanceTo(doorPosition);
      const wasShowingPrompt = showPrompt;
      
      // Show interaction prompt when within 2 units
      setShowPrompt(distance < 2);
      
      // Auto-open door when very close (within 1.5 units)
      if (distance < 1.5 && !isOpen && onInteract) {
        onInteract();
      }
    }
  });

  const doorWidth = 1.2;
  const doorHeight = 2.2;
  const doorThickness = 0.08;
  const frameThickness = 0.15;
  const frameWidth = 0.1;

  return (
    <group ref={doorRef} position={position} rotation={rotation}>
      {/* Door Frame */}
      <group>
        {/* Left Frame */}
        <mesh position={[-doorWidth/2 - frameWidth/2, doorHeight/2, 0]}>
          <boxGeometry args={[frameWidth, doorHeight + frameWidth, frameThickness + 0.02]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
        
        {/* Right Frame */}
        <mesh position={[doorWidth/2 + frameWidth/2, doorHeight/2, 0]}>
          <boxGeometry args={[frameWidth, doorHeight + frameWidth, frameThickness + 0.02]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
        
        {/* Top Frame */}
        <mesh position={[0, doorHeight + frameWidth/2, 0]}>
          <boxGeometry args={[doorWidth + frameWidth*2, frameWidth, frameThickness + 0.02]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
      </group>

      {/* Door Panel */}
      <group rotation={[0, isOpen ? -Math.PI/2 : 0, 0]}>
        <mesh 
          position={[isOpen ? 0 : 0, doorHeight/2, 0]} 
          castShadow 
          receiveShadow
          onPointerEnter={() => setIsHovered(true)}
          onPointerLeave={() => setIsHovered(false)}
          onClick={onInteract}
        >
          <boxGeometry args={[doorWidth, doorHeight, doorThickness]} />
          <meshStandardMaterial 
            color={isHovered ? "#A0522D" : "#8B4513"} 
            emissive={isHovered ? "#2D1810" : "#000000"}
            emissiveIntensity={isHovered ? 0.1 : 0}
          />
        </mesh>
        
        {/* Door Handle */}
        <mesh position={[doorWidth/2 - 0.15, doorHeight/2 - 0.2, doorThickness/2 + 0.02]} castShadow>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial color="#FFD700" metalness={0.8} roughness={0.2} />
        </mesh>
        
        {/* Door Panels (decorative) */}
        <mesh position={[0, doorHeight/2 + 0.3, doorThickness/2 + 0.005]}>
          <boxGeometry args={[doorWidth - 0.2, 0.4, 0.01]} />
          <meshStandardMaterial color="#654321" />
        </mesh>
        <mesh position={[0, doorHeight/2 - 0.3, doorThickness/2 + 0.005]}>
          <boxGeometry args={[doorWidth - 0.2, 0.4, 0.01]} />
          <meshStandardMaterial color="#654321" />
        </mesh>
      </group>

      {/* Interaction Prompt */}
      {showPrompt && (
        <group position={[0, doorHeight + 0.5, 0]}>
          <Text
            fontSize={0.2}
            color="#FFFFFF"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.02}
            outlineColor="#000000"
          >
            {isOpen ? "Door Open" : "Press E to Enter"}
          </Text>
          {label && (
            <Text
              position={[0, -0.3, 0]}
              fontSize={0.15}
              color="#CCCCCC"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.01}
              outlineColor="#000000"
            >
              {label}
            </Text>
          )}
        </group>
      )}

      {/* Door Light */}
      {isOpen && (
        <pointLight
          position={[0, doorHeight/2, 1]}
          intensity={0.3}
          distance={4}
          color="#fff5e6"
        />
      )}
    </group>
  );
}