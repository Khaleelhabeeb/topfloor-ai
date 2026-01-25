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
      {/* Floor - Premium hardwood */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} receiveShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color="#3D2817" />
      </mesh>

      {/* Floor wood grain pattern */}
      {Array.from({ length: 8 }, (_, i) => (
        <mesh key={`plank-${i}`} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, -4 + i * 1]} receiveShadow>
          <planeGeometry args={[roomSize[0], 0.8]} />
          <meshStandardMaterial color="#2D1B0E" transparent opacity={0.3} />
        </mesh>
      ))}

      {/* Ceiling - Executive coffered ceiling */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, roomSize[1], 0]} receiveShadow castShadow>
        <planeGeometry args={[roomSize[0], roomSize[2]]} />
        <meshStandardMaterial color="#2a2a2a" />
      </mesh>

      {/* Coffered ceiling details */}
      {Array.from({ length: 3 }, (_, i) => 
        Array.from({ length: 3 }, (_, j) => (
          <mesh key={`coffer-${i}-${j}`} position={[-3 + i * 3, roomSize[1] - 0.1, -3 + j * 3]} castShadow>
            <boxGeometry args={[2.5, 0.15, 2.5]} />
            <meshStandardMaterial color="#1a1a1a" />
          </mesh>
        ))
      )}

      {/* Walls */}
      {/* Back wall */}
      <mesh position={[0, roomSize[1] / 2, -roomSize[2] / 2]} receiveShadow castShadow>
        <boxGeometry args={[roomSize[0], roomSize[1], 0.2]} />
        <meshStandardMaterial color="#4a3c28" />
      </mesh>
      {/* Left wall */}
      <mesh position={[-roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[0.2, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color="#4a3c28" />
      </mesh>
      {/* Right wall */}
      <mesh position={[roomSize[0] / 2, roomSize[1] / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[0.2, roomSize[1], roomSize[2]]} />
        <meshStandardMaterial color="#4a3c28" />
      </mesh>
      {/* Front wall sections (with door opening) */}
      <mesh position={[-3, roomSize[1] / 2, roomSize[2] / 2]} receiveShadow castShadow>
        <boxGeometry args={[4, roomSize[1], 0.2]} />
        <meshStandardMaterial color="#4a3c28" />
      </mesh>
      <mesh position={[3, roomSize[1] / 2, roomSize[2] / 2]} receiveShadow castShadow>
        <boxGeometry args={[4, roomSize[1], 0.2]} />
        <meshStandardMaterial color="#4a3c28" />
      </mesh>

      {/* Crown molding */}
      <mesh position={[0, roomSize[1] - 0.1, -roomSize[2] / 2 + 0.1]} castShadow>
        <boxGeometry args={[roomSize[0], 0.1, 0.1]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[-roomSize[0] / 2 + 0.1, roomSize[1] - 0.1, 0]} castShadow>
        <boxGeometry args={[0.1, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[roomSize[0] / 2 - 0.1, roomSize[1] - 0.1, 0]} castShadow>
        <boxGeometry args={[0.1, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>

      {/* Baseboards */}
      <mesh position={[0, 0.05, -roomSize[2] / 2 + 0.1]} castShadow>
        <boxGeometry args={[roomSize[0], 0.1, 0.1]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[-roomSize[0] / 2 + 0.1, 0.05, 0]} castShadow>
        <boxGeometry args={[0.1, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>
      <mesh position={[roomSize[0] / 2 - 0.1, 0.05, 0]} castShadow>
        <boxGeometry args={[0.1, 0.1, roomSize[2]]} />
        <meshStandardMaterial color="#FFFFFF" />
      </mesh>

      {/* Window on back wall with detailed frame */}
      <mesh position={[0, 2, -roomSize[2] / 2 + 0.15]}>
        <boxGeometry args={[4, 2, 0.1]} />
        <meshStandardMaterial color="#B0E0E6" emissive="#B0E0E6" emissiveIntensity={0.1} transparent opacity={0.8} />
      </mesh>
      {/* Window frame */}
      <mesh position={[0, 2, -roomSize[2] / 2 + 0.2]} castShadow>
        <boxGeometry args={[4.2, 2.2, 0.05]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      {/* Window mullions */}
      <mesh position={[0, 2, -roomSize[2] / 2 + 0.16]} castShadow>
        <boxGeometry args={[0.05, 2, 0.02]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>
      <mesh position={[0, 2, -roomSize[2] / 2 + 0.16]} castShadow>
        <boxGeometry args={[4, 0.05, 0.02]} />
        <meshStandardMaterial color="#8B4513" />
      </mesh>

      {/* Executive Desk - Much more detailed */}
      <group position={[0, 0, -2]}>
        {/* Main desktop */}
        <mesh position={[0, 0.8, 0]} castShadow receiveShadow>
          <boxGeometry args={[3, 0.08, 1.5]} />
          <meshStandardMaterial color="#2D1B0E" />
        </mesh>
        
        {/* Desktop leather inlay */}
        <mesh position={[0, 0.81, 0]} castShadow>
          <boxGeometry args={[2.5, 0.01, 1]} />
          <meshStandardMaterial color="#1a4d1a" />
        </mesh>
        
        {/* Desk front panel */}
        <mesh position={[0, 0.4, 0.7]} castShadow>
          <boxGeometry args={[3, 0.8, 0.05]} />
          <meshStandardMaterial color="#3D2817" />
        </mesh>
        
        {/* Desk sides */}
        <mesh position={[-1.45, 0.4, 0]} castShadow>
          <boxGeometry args={[0.1, 0.8, 1.5]} />
          <meshStandardMaterial color="#3D2817" />
        </mesh>
        <mesh position={[1.45, 0.4, 0]} castShadow>
          <boxGeometry args={[0.1, 0.8, 1.5]} />
          <meshStandardMaterial color="#3D2817" />
        </mesh>
        
        {/* Desk drawers */}
        <mesh position={[-1, 0.6, 0]} castShadow>
          <boxGeometry args={[0.8, 0.15, 1.2]} />
          <meshStandardMaterial color="#2D1B0E" />
        </mesh>
        <mesh position={[-1, 0.4, 0]} castShadow>
          <boxGeometry args={[0.8, 0.15, 1.2]} />
          <meshStandardMaterial color="#2D1B0E" />
        </mesh>
        
        {/* Drawer handles */}
        <mesh position={[-0.6, 0.6, 0]} castShadow>
          <boxGeometry args={[0.02, 0.05, 0.2]} />
          <meshStandardMaterial color="#FFD700" metalness={0.9} roughness={0.1} />
        </mesh>
        <mesh position={[-0.6, 0.4, 0]} castShadow>
          <boxGeometry args={[0.02, 0.05, 0.2]} />
          <meshStandardMaterial color="#FFD700" metalness={0.9} roughness={0.1} />
        </mesh>
      </group>

      {/* Executive Chair - Ultra detailed */}
      <group position={[0, 0, 0.5]}>
        <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.7, 0.1, 0.7]} />
          <meshStandardMaterial color="#2D2D2D" />
        </mesh>
        {/* Seat cushion tufting */}
        <mesh position={[0, 0.52, 0]} castShadow>
          <boxGeometry args={[0.6, 0.02, 0.6]} />
          <meshStandardMaterial color="#1A1A1A" />
        </mesh>
        <mesh position={[0, 1, -0.3]} castShadow>
          <boxGeometry args={[0.7, 0.9, 0.1]} />
          <meshStandardMaterial color="#2D2D2D" />
        </mesh>
        {/* High-back executive styling */}
        <mesh position={[0, 1.3, -0.32]} castShadow>
          <boxGeometry args={[0.6, 0.3, 0.08]} />
          <meshStandardMaterial color="#1A1A1A" />
        </mesh>
        {/* Armrests */}
        <mesh position={[-0.35, 0.7, 0]} castShadow>
          <boxGeometry args={[0.05, 0.1, 0.5]} />
          <meshStandardMaterial color="#4D4D4D" />
        </mesh>
        <mesh position={[0.35, 0.7, 0]} castShadow>
          <boxGeometry args={[0.05, 0.1, 0.5]} />
          <meshStandardMaterial color="#4D4D4D" />
        </mesh>
        {/* Armrest padding */}
        <mesh position={[-0.35, 0.72, 0]} castShadow>
          <boxGeometry args={[0.08, 0.02, 0.4]} />
          <meshStandardMaterial color="#2D2D2D" />
        </mesh>
        <mesh position={[0.35, 0.72, 0]} castShadow>
          <boxGeometry args={[0.08, 0.02, 0.4]} />
          <meshStandardMaterial color="#2D2D2D" />
        </mesh>
        <mesh position={[0, 0.25, 0]} castShadow>
          <cylinderGeometry args={[0.3, 0.3, 0.05, 16]} />
          <meshStandardMaterial color="#555555" />
        </mesh>
        {/* Chair wheels */}
        {[0, Math.PI/2.5, Math.PI*2/2.5, Math.PI*3/2.5, Math.PI*4/2.5].map((angle, i) => (
          <mesh key={i} position={[Math.cos(angle) * 0.25, 0.05, Math.sin(angle) * 0.25]} castShadow>
            <cylinderGeometry args={[0.04, 0.04, 0.03, 8]} />
            <meshStandardMaterial color="#1a1a1a" />
          </mesh>
        ))}
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

      {/* Dual monitors on desk - Ultra realistic */}
      <group position={[0, 0.85, -2.5]}>
        <mesh position={[-0.5, 0.25, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.75, 0.5, 0.04]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[-0.5, 0.25, 0.021]}>
          <planeGeometry args={[0.7, 0.45]} />
          <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.4} />
        </mesh>
        {/* Screen content */}
        <mesh position={[-0.5, 0.3, 0.022]}>
          <planeGeometry args={[0.6, 0.1]} />
          <meshStandardMaterial color="#FFFFFF" emissive="#FFFFFF" emissiveIntensity={0.3} />
        </mesh>
        
        <mesh position={[0.5, 0.25, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.75, 0.5, 0.04]} />
          <meshStandardMaterial color="#1a1a1a" />
        </mesh>
        <mesh position={[0.5, 0.25, 0.021]}>
          <planeGeometry args={[0.7, 0.45]} />
          <meshStandardMaterial color="#0a1628" emissive="#1e3a5f" emissiveIntensity={0.4} />
        </mesh>
        
        {/* Monitor stands */}
        <mesh position={[-0.5, -0.05, 0.15]} castShadow>
          <boxGeometry args={[0.1, 0.15, 0.2]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
        <mesh position={[0.5, -0.05, 0.15]} castShadow>
          <boxGeometry args={[0.1, 0.15, 0.2]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
      </group>

      {/* Enhanced Bookshelf */}
      <group position={[-4, 0, 0]}>
        <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
          <boxGeometry args={[0.4, 3, 1.5]} />
          <meshStandardMaterial color="#5D4E37" />
        </mesh>
        {/* Shelves */}
        {[0.5, 1, 1.5, 2, 2.5].map((y, i) => (
          <mesh key={`shelf-${i}`} position={[0.1, y, 0]} castShadow>
            <boxGeometry args={[0.3, 0.02, 1.4]} />
            <meshStandardMaterial color="#4A3C28" />
          </mesh>
        ))}
        {/* Books with more variety */}
        {[0.6, 1.1, 1.6, 2.1, 2.6].map((y, i) => (
          <group key={`book-group-${i}`}>
            <mesh position={[0.15, y + 0.1, -0.3]} castShadow>
              <boxGeometry args={[0.15, 0.15, 0.03]} />
              <meshStandardMaterial color={['#8B4513', '#2F4F4F', '#556B2F', '#800080', '#B22222'][i]} />
            </mesh>
            <mesh position={[0.15, y + 0.1, -0.1]} castShadow>
              <boxGeometry args={[0.15, 0.18, 0.03]} />
              <meshStandardMaterial color={['#4682B4', '#228B22', '#FF6347', '#9932CC', '#DC143C'][i]} />
            </mesh>
            <mesh position={[0.15, y + 0.1, 0.1]} castShadow>
              <boxGeometry args={[0.15, 0.12, 0.03]} />
              <meshStandardMaterial color={['#DAA520', '#CD853F', '#20B2AA', '#FF69B4', '#32CD32'][i]} />
            </mesh>
          </group>
        ))}
      </group>

      {/* Large executive plant */}
      <group position={[4, 0, -3]}>
        <mesh position={[0, 0.4, 0]} castShadow receiveShadow>
          <cylinderGeometry args={[0.35, 0.3, 0.8, 16]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
        <mesh position={[0, 1.2, 0]} castShadow>
          <sphereGeometry args={[0.6, 12, 12]} />
          <meshStandardMaterial color="#228B22" />
        </mesh>
        {/* Additional foliage */}
        <mesh position={[0.3, 1.4, 0.2]} castShadow>
          <sphereGeometry args={[0.3, 8, 8]} />
          <meshStandardMaterial color="#32CD32" />
        </mesh>
        <mesh position={[-0.2, 1.1, -0.3]} castShadow>
          <sphereGeometry args={[0.25, 8, 8]} />
          <meshStandardMaterial color="#228B22" />
        </mesh>
      </group>

      {/* Conference area */}
      <group position={[3, 0, 2]}>
        {/* Small conference table */}
        <mesh position={[0, 0.4, 0]} castShadow receiveShadow>
          <cylinderGeometry args={[0.8, 0.8, 0.05, 16]} />
          <meshStandardMaterial color="#2D1B0E" />
        </mesh>
        <mesh position={[0, 0.2, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.1, 0.4, 8]} />
          <meshStandardMaterial color="#2d2d2d" />
        </mesh>
        {/* Chairs around table */}
        {[0, Math.PI/2, Math.PI, 3*Math.PI/2].map((angle, i) => (
          <group key={`conf-chair-${i}`} position={[Math.cos(angle) * 1.2, 0, Math.sin(angle) * 1.2]}>
            <mesh position={[0, 0.4, 0]} castShadow>
              <boxGeometry args={[0.4, 0.06, 0.4]} />
              <meshStandardMaterial color="#654321" />
            </mesh>
            <mesh position={[0, 0.7, -0.18]} castShadow>
              <boxGeometry args={[0.4, 0.5, 0.06]} />
              <meshStandardMaterial color="#654321" />
            </mesh>
          </group>
        ))}
      </group>

      {/* Lighting - Ultra realistic */}
      <pointLight position={[0, 3.8, 0]} intensity={4.0} distance={15} color="#fff5e6" castShadow />
      <pointLight position={[-2, 3.5, -2]} intensity={2.5} distance={10} color="#ffcc88" />
      <pointLight position={[2, 3.5, -2]} intensity={2.5} distance={10} color="#ffcc88" />
      <pointLight position={[0, 3.5, 2]} intensity={2.0} distance={8} color="#fff5e6" />
      
      {/* Desk lamp */}
      <pointLight position={[1, 1.2, -2]} intensity={2.0} distance={4} color="#ffffcc" />
      
      {/* Ambient office lighting */}
      <pointLight position={[-3, 2.5, 0]} intensity={1.5} distance={8} color="#ffeecc" />
      <pointLight position={[3, 2.5, 0]} intensity={1.5} distance={8} color="#ffeecc" />
      <pointLight position={[0, 2.5, -4]} intensity={1.8} distance={8} color="#fff5e6" />

      {/* Ceiling Light Fixtures - Chandelier style */}
      <group position={[0, roomSize[1] - 0.2, 0]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.8, 0.6, 0.15, 8]} />
          <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={0.3} metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Chandelier arms */}
        {[0, Math.PI/2, Math.PI, 3*Math.PI/2].map((angle, i) => (
          <mesh key={`arm-${i}`} position={[Math.cos(angle) * 0.4, -0.1, Math.sin(angle) * 0.4]} castShadow>
            <cylinderGeometry args={[0.02, 0.02, 0.1, 8]} />
            <meshStandardMaterial color="#FFD700" metalness={0.8} roughness={0.2} />
          </mesh>
        ))}
      </group>

      {/* Additional ceiling fixtures */}
      <group position={[-2.5, roomSize[1] - 0.1, -2]}>
        <mesh castShadow>
          <boxGeometry args={[1, 0.08, 0.5]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.3} />
        </mesh>
      </group>
      <group position={[2.5, roomSize[1] - 0.1, -2]}>
        <mesh castShadow>
          <boxGeometry args={[1, 0.08, 0.5]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.3} />
        </mesh>
      </group>

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