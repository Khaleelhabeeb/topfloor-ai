import { Canvas } from '@react-three/fiber';
import { Character } from './Character';
import { OfficeLayout } from './OfficeLayout';
import { Camera } from './Camera';
import { useGameState } from '@/hooks/useGameState';

export function Scene() {
  const { mode } = useGameState();

  if (mode !== 'exploring') return null;

  return (
    <div className="absolute inset-0">
      <Canvas shadows>
        <Camera />
        
        {/* Lighting - warm corporate feel */}
        <ambientLight intensity={0.4} color="#fff5e6" />
        <directionalLight
          position={[10, 20, 10]}
          intensity={0.8}
          color="#fff8f0"
          castShadow
          shadow-mapSize={[2048, 2048]}
          shadow-camera-far={50}
          shadow-camera-left={-20}
          shadow-camera-right={20}
          shadow-camera-top={20}
          shadow-camera-bottom={-20}
        />
        <directionalLight
          position={[-5, 10, -5]}
          intensity={0.3}
          color="#ffe4c4"
        />
        
        {/* Scene content */}
        <OfficeLayout />
        <Character />
        
        {/* Floor plane for shadows */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
          <planeGeometry args={[50, 50]} />
          <shadowMaterial opacity={0.15} />
        </mesh>
      </Canvas>
    </div>
  );
}
