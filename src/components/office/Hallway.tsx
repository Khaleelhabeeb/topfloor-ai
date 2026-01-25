import { Text } from '@react-three/drei';

export function Hallway() {
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

      {/* Left Wall */}
      <mesh position={[-hallwayWidth / 2, hallwayHeight / 2, 0]} receiveShadow>
        <boxGeometry args={[0.2, hallwayHeight, hallwayLength]} />
        <meshStandardMaterial color="#d4c4b0" />
      </mesh>

      {/* Right Wall */}
      <mesh position={[hallwayWidth / 2, hallwayHeight / 2, 0]} receiveShadow>
        <boxGeometry args={[0.2, hallwayHeight, hallwayLength]} />
        <meshStandardMaterial color="#d4c4b0" />
      </mesh>

      {/* Ceiling */}
      <mesh position={[0, hallwayHeight, 0]} receiveShadow>
        <boxGeometry args={[hallwayWidth, 0.15, hallwayLength]} />
        <meshStandardMaterial color="#e8e0d5" />
      </mesh>

      {/* End Walls */}
      <mesh position={[0, hallwayHeight / 2, hallwayLength / 2]} receiveShadow>
        <boxGeometry args={[hallwayWidth, hallwayHeight, 0.2]} />
        <meshStandardMaterial color="#d4c4b0" />
      </mesh>
      
      <mesh position={[0, hallwayHeight / 2, -hallwayLength / 2]} receiveShadow>
        <boxGeometry args={[hallwayWidth, hallwayHeight, 0.2]} />
        <meshStandardMaterial color="#d4c4b0" />
      </mesh>

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
        ← Developer Office
      </Text>

      <Text
        position={[-1.5, 2, 3]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, Math.PI / 2, 0]}
      >
        ← Designer Office
      </Text>

      <Text
        position={[1.5, 2, 0]}
        fontSize={0.2}
        color="#666666"
        anchorX="center"
        rotation={[0, -Math.PI / 2, 0]}
      >
        Marketing Office →
      </Text>

      <Text
        position={[0, 2, -12]}
        fontSize={0.25}
        color="#1a1a1a"
        anchorX="center"
      >
        CEO Office ↑
      </Text>
    </group>
  );
}
