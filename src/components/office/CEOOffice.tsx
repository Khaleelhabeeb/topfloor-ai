import { Text } from '@react-three/drei';
import { InteractiveFolder } from './InteractiveFolder';
import { ceoFolders } from './data';
import { Folder } from './types';

interface CEOOfficeProps {
  position: [number, number, number];
  onFolderSelect: (folder: Folder) => void;
  isSeated: boolean;
}

export function CEOOffice({ position, onFolderSelect, isSeated }: CEOOfficeProps) {
  const roomSize: [number, number, number] = [10, 4, 10];

  return (
    <group position={position}>
      {/* Floor - Premium wood */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} receiveShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color="#1a0f08" />
      </mesh>

      {/* Walls */}
      {/* Back wall */}
      <mesh position={[0, roomSize[1] / 2, -roomSize[2] / 2]} receiveShadow>
        <boxGeometry args={[roomSize[0], roomSize[1], 0.2]} />
        <meshStandardMaterial color="#2c2418" />
      </mesh>
      {/* Left wall */}
      <mesh position={[-roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow>
        <boxGeometry args={[0.2, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color="#2c2418" />
      </mesh>
      {/* Right wall */}
      <mesh position={[roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow>
        <boxGeometry args={[0.2, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color="#2c2418" />
      </mesh>
      {/* Front wall sections (with door opening) */}
      <mesh position={[-3, roomSize[1] / 2, roomSize[2] / 2]} receiveShadow>
        <boxGeometry args={[4, roomSize[1], 0.2]} />
        <meshStandardMaterial color="#2c2418" />
      </mesh>
      <mesh position={[3, roomSize[1] / 2, roomSize[2] / 2]} receiveShadow>
        <boxGeometry args={[4, roomSize[1], 0.2]} />
        <meshStandardMaterial color="#2c2418" />
      </mesh>

      {/* Window on back wall */}
      <mesh position={[0, 2, -roomSize[2] / 2 + 0.15]}>
        <boxGeometry args={[4, 2, 0.1]} />
        <meshStandardMaterial color="#87CEEB" emissive="#87CEEB" emissiveIntensity={0.2} transparent opacity={0.7} />
      </mesh>

      {/* Executive Desk */}
      <group position={[0, 0, -2]}>
        {/* Main desktop */}
        <mesh position={[0, 0.8, 0]} castShadow receiveShadow>
          <boxGeometry args={[3, 0.08, 1.5]} />
          <meshStandardMaterial color="#0d0705" />
        </mesh>
        
        {/* Desk front panel */}
        <mesh position={[0, 0.4, 0.7]} castShadow>
          <boxGeometry args={[3, 0.8, 0.05]} />
          <meshStandardMaterial color="#1a0f0a" />
        </mesh>
        
        {/* Desk sides */}
        <mesh position={[-1.45, 0.4, 0]} castShadow>
          <boxGeometry args={[0.1, 0.8, 1.5]} />
          <meshStandardMaterial color="#1a0f0a" />
        </mesh>
        <mesh position={[1.45, 0.4, 0]} castShadow>
          <boxGeometry args={[0.1, 0.8, 1.5]} />
          <meshStandardMaterial color="#1a0f0a" />
        </mesh>
      </group>

      {/* Executive Chair */}
      <group position={[0, 0, 0.5]}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <boxGeometry args={[0.7, 0.1, 0.7]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[0, 1, -0.3]} castShadow>
          <boxGeometry args={[0.7, 0.9, 0.1]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        {/* Armrests */}
        <mesh position={[-0.35, 0.7, 0]} castShadow>
          <boxGeometry args={[0.05, 0.1, 0.5]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
        <mesh position={[0.35, 0.7, 0]} castShadow>
          <boxGeometry args={[0.05, 0.1, 0.5]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
        <mesh position={[0, 0.25, 0]} castShadow>
          <cylinderGeometry args={[0.3, 0.3, 0.05, 16]} />
          <meshStandardMaterial color="#333333" />
        </mesh>
      </group>

      {/* Folders on desk */}
      {ceoFolders.map((folder, index) => (
        <InteractiveFolder
          key={folder.id}
          folder={folder}
          position={[-1 + index * 0.6, 0.88, -2.2]}
          onSelect={onFolderSelect}
        />
      ))}

      {/* Monitors on desk */}
      <group position={[0, 0.85, -2.5]}>
        <mesh position={[-0.5, 0.25, 0]} castShadow>
          <boxGeometry args={[0.7, 0.45, 0.03]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[-0.5, 0.25, 0.02]}>
          <planeGeometry args={[0.65, 0.4]} />
          <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.3} />
        </mesh>
        
        <mesh position={[0.5, 0.25, 0]} castShadow>
          <boxGeometry args={[0.7, 0.45, 0.03]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[0.5, 0.25, 0.02]}>
          <planeGeometry args={[0.65, 0.4]} />
          <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.3} />
        </mesh>
      </group>

      {/* Bookshelf */}
      <group position={[-4, 0, 0]}>
        <mesh position={[0, 1.5, 0]} castShadow>
          <boxGeometry args={[0.4, 3, 1.5]} />
          <meshStandardMaterial color="#2c1810" />
        </mesh>
        {/* Books */}
        {[0.8, 1.3, 1.8, 2.3].map((y, i) => (
          <mesh key={i} position={[0.1, y, 0]} castShadow>
            <boxGeometry args={[0.15, 0.25, 1.2]} />
            <meshStandardMaterial color={['#8B0000', '#00008B', '#006400', '#4B0082'][i]} />
          </mesh>
        ))}
      </group>

      {/* Plants */}
      <group position={[4, 0, -3]}>
        <mesh position={[0, 0.3, 0]} castShadow>
          <cylinderGeometry args={[0.3, 0.25, 0.6, 16]} />
          <meshStandardMaterial color="#4a3728" />
        </mesh>
        <mesh position={[0, 0.9, 0]} castShadow>
          <sphereGeometry args={[0.5, 12, 12]} />
          <meshStandardMaterial color="#1a5c1a" />
        </mesh>
      </group>

      {/* Lighting */}
      <pointLight position={[0, 3.5, 0]} intensity={1.5} distance={12} color="#fff5e6" castShadow />
      <pointLight position={[-3, 2, -3]} intensity={0.5} distance={6} color="#ffcc88" />
      <pointLight position={[3, 2, -3]} intensity={0.5} distance={6} color="#ffcc88" />

      {/* Name plate */}
      <Text
        position={[0, 3.2, -roomSize[2] / 2 + 0.3]}
        fontSize={0.4}
        color="#D4AF37"
        anchorX="center"
        anchorY="middle"
      >
        CEO OFFICE
      </Text>

      {/* Sit instruction */}
      {!isSeated && (
        <Text
          position={[0, 1.5, 1.5]}
          fontSize={0.15}
          color="#FFD700"
          anchorX="center"
          anchorY="middle"
        >
          Walk to chair and press E to sit
        </Text>
      )}
    </group>
  );
}
