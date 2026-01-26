import { Text } from '@react-three/drei';
import { Door } from './Door';
import * as THREE from 'three';

interface HallwayProps {
  onDoorInteract?: (doorId: string) => void;
  doorStates?: Map<string, boolean>;
  playerPosition?: THREE.Vector3;
}
export function Hallway({ onDoorInteract, doorStates, playerPosition }: HallwayProps) {
  const hallwayLength = 30;
  const hallwayWidth = 4;
  const hallwayHeight = 3.5;

  return (
    <group>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[hallwayWidth, hallwayLength]} />
        <meshStandardMaterial color="#4a4a4a" />
      </mesh>

      {/* Left Wall with door openings */}
      <group>
        {/* Left wall section 1 (before dev office) */}
        <mesh position={[-hallwayWidth / 2, hallwayHeight / 2, -9]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 6]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
        
        {/* Left wall section 2 (between offices) */}
        <mesh position={[-hallwayWidth / 2, hallwayHeight / 2, 0]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 4]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
        
        {/* Left wall section 3 (after designer office) */}
        <mesh position={[-hallwayWidth / 2, hallwayHeight / 2, 11]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 8]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
      </group>

      {/* Right Wall with door openings */}
      <group>
        {/* Right wall section 1 */}
        <mesh position={[hallwayWidth / 2, hallwayHeight / 2, -8.5]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 13]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
        
        {/* Right wall section 2 (between marketing and peter's office) */}
        <mesh position={[hallwayWidth / 2, hallwayHeight / 2, 5]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 4]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
        
        {/* Right wall section 3 (after peter's office) */}
        <mesh position={[hallwayWidth / 2, hallwayHeight / 2, 12.5]} receiveShadow>
          <boxGeometry args={[0.2, hallwayHeight, 5]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
      </group>

      {/* Ceiling */}
      <mesh position={[0, hallwayHeight, 0]} receiveShadow>
        <boxGeometry args={[hallwayWidth, 0.15, hallwayLength]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>

      {/* Ceiling extension over door areas to prevent sky gaps */}
      <mesh position={[-4, hallwayHeight, -5]} receiveShadow>
        <boxGeometry args={[4, 0.15, 6]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>
      <mesh position={[-4, hallwayHeight, 5]} receiveShadow>
        <boxGeometry args={[4, 0.15, 6]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>
      <mesh position={[4, hallwayHeight, 0]} receiveShadow>
        <boxGeometry args={[4, 0.15, 6]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>
      <mesh position={[4, hallwayHeight, 10]} receiveShadow>
        <boxGeometry args={[4, 0.15, 6]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>
      <mesh position={[0, hallwayHeight, -15.5]} receiveShadow>
        <boxGeometry args={[10, 0.15, 5]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>

      {/* End Walls */}
      <mesh position={[0, hallwayHeight / 2, hallwayLength / 2]} receiveShadow>
        <boxGeometry args={[hallwayWidth, hallwayHeight, 0.2]} />
        <meshStandardMaterial color="#d4c4b0" />
      </mesh>
      
      {/* End wall with CEO office door opening */}
      <group>
        <mesh position={[-1.5, hallwayHeight / 2, -hallwayLength / 2]} receiveShadow>
          <boxGeometry args={[1, hallwayHeight, 0.2]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
        <mesh position={[1.5, hallwayHeight / 2, -hallwayLength / 2]} receiveShadow>
          <boxGeometry args={[1, hallwayHeight, 0.2]} />
          <meshStandardMaterial color="#d4c4b0" />
        </mesh>
      </group>

      {/* Ceiling Lights */}
      {[-10, -3, 3, 10].map((z, i) => (
        <group key={i} position={[0, hallwayHeight - 0.1, z]}>
          <mesh>
            <boxGeometry args={[0.8, 0.05, 0.4]} />
            <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.5} />
          </mesh>
          <pointLight intensity={0.8} distance={6} color="#fff5e6" position={[0, -0.5, 0]} />
        </group>
      ))}

      {/* Welcome Sign */}
      <Text
        position={[0, 2.5, 12]}
        fontSize={0.4}
        color="#333333"
        anchorX="center"
        anchorY="middle"
      >
        VIRTUAL OFFICE
      </Text>

      {/* Directional Signs */}
      <Text
        position={[-1.5, 2, -3]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, Math.PI / 2, 0]}
      >
        ← James Wilson
      </Text>

      <Text
        position={[-1.5, 2, 3]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, Math.PI / 2, 0]}
      >
        ← Sarah Miller
      </Text>

      <Text
        position={[1.5, 2, -2]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, -Math.PI / 2, 0]}
      >
        Alex Chen →
      </Text>

      <Text
        position={[1.5, 2, 8]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, -Math.PI / 2, 0]}
      >
        Peter Rodriguez →
      </Text>

      <Text
        position={[0, 2, -12]}
        fontSize={0.25}
        color="#1a1a1a"
        anchorX="center"
      >
        CEO Office ↑
      </Text>

      {/* Doors */}
      <Door
        position={[-2, 0, -5]}
        rotation={[0, Math.PI / 2, 0]}
        isOpen={doorStates?.get('james-office-door') || false}
        onInteract={() => onDoorInteract?.('james-office-door')}
        label="James Wilson"
        playerPosition={playerPosition}
      />
      
      <Door
        position={[-2, 0, 5]}
        rotation={[0, Math.PI / 2, 0]}
        isOpen={doorStates?.get('sarah-office-door') || false}
        onInteract={() => onDoorInteract?.('sarah-office-door')}
        label="Sarah Miller"
        playerPosition={playerPosition}
      />
      
      <Door
        position={[2, 0, 0]}
        rotation={[0, -Math.PI / 2, 0]}
        isOpen={doorStates?.get('alex-office-door') || false}
        onInteract={() => onDoorInteract?.('alex-office-door')}
        label="Alex Chen"
        playerPosition={playerPosition}
      />
      
      <Door
        position={[2, 0, 10]}
        rotation={[0, -Math.PI / 2, 0]}
        isOpen={doorStates?.get('peter-office-door') || false}
        onInteract={() => onDoorInteract?.('peter-office-door')}
        label="Peter Rodriguez"
        playerPosition={playerPosition}
      />
      
      <Door
        position={[0, 0, -13]}
        isOpen={doorStates?.get('ceo-office-door') || false}
        onInteract={() => onDoorInteract?.('ceo-office-door')}
        label="CEO"
        playerPosition={playerPosition}
      />
    </group>
  );
}
