import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { OrthographicCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useGameState } from '@/hooks/useGameState';

export function Camera() {
  const cameraRef = useRef<THREE.OrthographicCamera>(null);
  const { playerPosition, mode } = useGameState();
  
  const targetPosition = useRef({ x: 0, z: 5 });
  
  useFrame(() => {
    if (!cameraRef.current || mode !== 'exploring') return;
    
    // Smooth follow with lag
    targetPosition.current.x += (playerPosition.x - targetPosition.current.x) * 0.08;
    targetPosition.current.z += (playerPosition.z - targetPosition.current.z) * 0.08;
    
    // Position camera above and behind player (isometric-ish view)
    cameraRef.current.position.x = targetPosition.current.x;
    cameraRef.current.position.z = targetPosition.current.z + 12;
    cameraRef.current.position.y = 15;
    
    // Look at player position
    cameraRef.current.lookAt(
      targetPosition.current.x,
      0,
      targetPosition.current.z
    );
  });

  return (
    <OrthographicCamera
      ref={cameraRef}
      makeDefault
      zoom={40}
      position={[0, 15, 17]}
      near={0.1}
      far={100}
    />
  );
}
