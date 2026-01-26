import * as THREE from 'three';
import { employees } from '@/data/employees';

// Colors matching the warm corporate theme
const COLORS = {
  floor: '#d4a574', // Warm wood
  carpet: '#8b7355', // Office carpet
  wall: '#f5e6d3', // Cream walls
  wallAccent: '#c9b896', // Accent trim
  desk: '#5c4033', // Dark wood
  chairSeat: '#2d3436', // Dark chair
  chairFrame: '#636e72', // Metal frame
  plant: '#228b22', // Green plant
  pot: '#8b4513', // Terracotta pot
  door: '#6b4423', // Wooden door
  doorFrame: '#8b7355', // Door frame
  glass: '#87ceeb', // Window glass
  ceoDesk: '#3d2914', // Premium dark wood
};

function Floor() {
  return (
    <group>
      {/* Main hallway floor - wood pattern */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[10, 24]} />
        <meshStandardMaterial color={COLORS.floor} />
      </mesh>
      
      {/* Left offices carpet */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-9.5, 0.01, -6]} receiveShadow>
        <planeGeometry args={[9, 10]} />
        <meshStandardMaterial color={COLORS.carpet} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-9.5, 0.01, 6]} receiveShadow>
        <planeGeometry args={[9, 10]} />
        <meshStandardMaterial color={COLORS.carpet} />
      </mesh>
      
      {/* Right offices carpet */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[9.5, 0.01, -6]} receiveShadow>
        <planeGeometry args={[9, 10]} />
        <meshStandardMaterial color={COLORS.carpet} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[9.5, 0.01, 6]} receiveShadow>
        <planeGeometry args={[9, 10]} />
        <meshStandardMaterial color={COLORS.carpet} />
      </mesh>
    </group>
  );
}

function Walls() {
  const wallHeight = 3;
  const wallThickness = 0.3;
  
  return (
    <group>
      {/* Outer walls */}
      {/* North wall */}
      <mesh position={[0, wallHeight / 2, -11.5]} castShadow receiveShadow>
        <boxGeometry args={[30, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* South wall */}
      <mesh position={[0, wallHeight / 2, 11.5]} castShadow receiveShadow>
        <boxGeometry args={[30, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* West wall */}
      <mesh position={[-14.5, wallHeight / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 24]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* East wall */}
      <mesh position={[14.5, wallHeight / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 24]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* Interior walls - Sarah's office */}
      <mesh position={[-9.5, wallHeight / 2, -1]} castShadow receiveShadow>
        <boxGeometry args={[9, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      {/* Sarah's wall with door cutout - split into two parts */}
      <mesh position={[-5, wallHeight / 2, -8.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      <mesh position={[-5, wallHeight / 2, -3.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* Interior walls - James's office */}
      <mesh position={[-9.5, wallHeight / 2, 1]} castShadow receiveShadow>
        <boxGeometry args={[9, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      {/* James's wall with door cutout - split into two parts */}
      <mesh position={[-5, wallHeight / 2, 3.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      <mesh position={[-5, wallHeight / 2, 8.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* Interior walls - Alex's office */}
      <mesh position={[9.5, wallHeight / 2, -1]} castShadow receiveShadow>
        <boxGeometry args={[9, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      {/* Alex's wall with door cutout - split into two parts */}
      <mesh position={[5, wallHeight / 2, -8.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      <mesh position={[5, wallHeight / 2, -3.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      
      {/* Interior walls - Peter's office */}
      <mesh position={[9.5, wallHeight / 2, 1]} castShadow receiveShadow>
        <boxGeometry args={[9, wallHeight, wallThickness]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      {/* Peter's wall with door cutout - split into two parts */}
      <mesh position={[5, wallHeight / 2, 3.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
      <mesh position={[5, wallHeight / 2, 8.5]} castShadow receiveShadow>
        <boxGeometry args={[wallThickness, wallHeight, 3]} />
        <meshStandardMaterial color={COLORS.wall} />
      </mesh>
    </group>
  );
}

function Door({ position, label, rotation = 0 }: { position: [number, number, number]; label: string; rotation?: number }) {
  return (
    <group position={position} rotation={[0, rotation, 0]}>
      {/* Door frame - left side */}
      <mesh position={[-0.55, 1.25, 0]} castShadow>
        <boxGeometry args={[0.1, 2.5, 0.15]} />
        <meshStandardMaterial color={COLORS.doorFrame} />
      </mesh>
      
      {/* Door frame - right side */}
      <mesh position={[0.55, 1.25, 0]} castShadow>
        <boxGeometry args={[0.1, 2.5, 0.15]} />
        <meshStandardMaterial color={COLORS.doorFrame} />
      </mesh>
      
      {/* Door frame - top */}
      <mesh position={[0, 2.5, 0]} castShadow>
        <boxGeometry args={[1.2, 0.1, 0.15]} />
        <meshStandardMaterial color={COLORS.doorFrame} />
      </mesh>
      
      {/* Open door - swung to the side */}
      <mesh position={[-0.95, 1.15, 0.4]} rotation={[0, Math.PI / 2.5, 0]} castShadow>
        <boxGeometry args={[0.9, 2.2, 0.08]} />
        <meshStandardMaterial color={COLORS.door} />
      </mesh>
      
      {/* Door handle on open door */}
      <mesh position={[-0.95, 1.1, 0.65]} castShadow>
        <boxGeometry args={[0.05, 0.05, 0.12]} />
        <meshStandardMaterial color="#c0a060" metalness={0.8} roughness={0.2} />
      </mesh>
      
      {/* Name plate above door */}
      <mesh position={[0, 2.65, 0.08]} castShadow>
        <boxGeometry args={[0.8, 0.2, 0.05]} />
        <meshStandardMaterial color="#2d3436" />
      </mesh>
    </group>
  );
}

function Desk({ position, rotation = 0, isPremium = false }: { position: [number, number, number]; rotation?: number; isPremium?: boolean }) {
  const deskColor = isPremium ? COLORS.ceoDesk : COLORS.desk;
  const scale = isPremium ? 1.3 : 1;
  
  return (
    <group position={position} rotation={[0, rotation, 0]} scale={[scale, scale, scale]}>
      {/* Desktop */}
      <mesh position={[0, 0.75, 0]} castShadow receiveShadow>
        <boxGeometry args={[2, 0.08, 1]} />
        <meshStandardMaterial color={deskColor} />
      </mesh>
      
      {/* Legs */}
      {[[-0.9, 0.35, 0.4], [0.9, 0.35, 0.4], [-0.9, 0.35, -0.4], [0.9, 0.35, -0.4]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <boxGeometry args={[0.08, 0.7, 0.08]} />
          <meshStandardMaterial color={deskColor} />
        </mesh>
      ))}
      
      {/* Monitor */}
      <mesh position={[0, 1.1, -0.3]} castShadow>
        <boxGeometry args={[0.8, 0.5, 0.05]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[0, 1.1, -0.28]} castShadow>
        <boxGeometry args={[0.7, 0.4, 0.02]} />
        <meshStandardMaterial color="#4a90d9" emissive="#4a90d9" emissiveIntensity={0.2} />
      </mesh>
      
      {/* Keyboard */}
      <mesh position={[0, 0.8, 0.15]} castShadow>
        <boxGeometry args={[0.5, 0.02, 0.15]} />
        <meshStandardMaterial color="#2d3436" />
      </mesh>
    </group>
  );
}

function Chair({ position, rotation = 0, isPremium = false }: { position: [number, number, number]; rotation?: number; isPremium?: boolean }) {
  const scale = isPremium ? 1.2 : 1;
  const seatColor = isPremium ? '#1a0a00' : COLORS.chairSeat;
  
  return (
    <group position={position} rotation={[0, rotation, 0]} scale={[scale, scale, scale]}>
      {/* Seat */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[0.5, 0.08, 0.5]} />
        <meshStandardMaterial color={seatColor} />
      </mesh>
      
      {/* Back */}
      <mesh position={[0, 0.75, -0.22]} castShadow>
        <boxGeometry args={[0.5, 0.6, 0.08]} />
        <meshStandardMaterial color={seatColor} />
      </mesh>
      
      {/* Base */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.25, 0.25, 0.05, 16]} />
        <meshStandardMaterial color={COLORS.chairFrame} metalness={0.6} roughness={0.4} />
      </mesh>
      
      {/* Pole */}
      <mesh position={[0, 0.3, 0]} castShadow>
        <cylinderGeometry args={[0.04, 0.04, 0.25, 8]} />
        <meshStandardMaterial color={COLORS.chairFrame} metalness={0.6} roughness={0.4} />
      </mesh>
    </group>
  );
}

function Plant({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      {/* Pot */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.2, 0.15, 0.4, 8]} />
        <meshStandardMaterial color={COLORS.pot} />
      </mesh>
      
      {/* Plant leaves */}
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh 
          key={i} 
          position={[
            Math.sin(i * 1.25) * 0.15,
            0.5 + i * 0.08,
            Math.cos(i * 1.25) * 0.15
          ]} 
          rotation={[0.2, i * 1.25, 0.1]}
          castShadow
        >
          <boxGeometry args={[0.15, 0.25, 0.02]} />
          <meshStandardMaterial color={COLORS.plant} />
        </mesh>
      ))}
    </group>
  );
}

export function OfficeLayout() {
  return (
    <group>
      <Floor />
      <Walls />
      
      {/* Doors with labels - positioned in the doorway cutouts */}
      <Door position={[-5, 0, -6]} label="Sarah" rotation={Math.PI / 2} />
      <Door position={[-5, 0, 6]} label="James" rotation={Math.PI / 2} />
      <Door position={[5, 0, -6]} label="Alex" rotation={-Math.PI / 2} />
      <Door position={[5, 0, 6]} label="Peter" rotation={-Math.PI / 2} />
      
      {/* Sarah's office furniture */}
      <Desk position={[-10.5, 0, -8]} rotation={Math.PI} />
      <Chair position={[-10.5, 0, -6.5]} rotation={Math.PI} />
      <Plant position={[-13, 0, -10]} />
      
      {/* James's office furniture */}
      <Desk position={[-10.5, 0, 8]} />
      <Chair position={[-10.5, 0, 6.5]} />
      <Plant position={[-13, 0, 10]} />
      
      {/* Alex's office furniture */}
      <Desk position={[10.5, 0, -8]} rotation={Math.PI} />
      <Chair position={[10.5, 0, -6.5]} rotation={Math.PI} />
      <Plant position={[13, 0, -10]} />
      
      {/* Peter's office furniture */}
      <Desk position={[10.5, 0, 8]} />
      <Chair position={[10.5, 0, 6.5]} />
      <Plant position={[13, 0, 10]} />
      
      {/* CEO Office - larger premium desk at the north end of hallway */}
      <Desk position={[0, 0, -9]} rotation={Math.PI} isPremium />
      <Chair position={[0, 0, -7]} rotation={Math.PI} isPremium />
      <Plant position={[-3.5, 0, -10.5]} />
      <Plant position={[3.5, 0, -10.5]} />
      
      {/* Hallway plants */}
      <Plant position={[-4, 0, 0]} />
      <Plant position={[4, 0, 0]} />
    </group>
  );
}
