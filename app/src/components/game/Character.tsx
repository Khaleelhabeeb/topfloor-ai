import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useKeyboard } from '@/hooks/useKeyboard';
import { useGameState } from '@/hooks/useGameState';
import { useCollision } from '@/hooks/useCollision';
import { employees } from '@/data/employees';

const SPEED = 5;
const ACCELERATION = 0.15;

export function Character() {
  const groupRef = useRef<THREE.Group>(null);
  const velocityRef = useRef({ x: 0, z: 0 });
  const rotationRef = useRef(0);
  
  const keys = useKeyboard();
  const { mode, setPlayerPosition, setNearDoor, setNearChair, enterVideoCall, enterCEODesk } = useGameState();
  const { checkCollision, getNearDoor, isNearCEOChair } = useCollision();

  useFrame((_, delta) => {
    if (!groupRef.current || mode !== 'exploring') return;

    const { forward, backward, left, right, interact } = keys.current;
    
    // Calculate target velocity
    let targetVelX = 0;
    let targetVelZ = 0;
    
    if (forward) targetVelZ -= 1;
    if (backward) targetVelZ += 1;
    if (left) targetVelX -= 1;
    if (right) targetVelX += 1;
    
    // Normalize diagonal movement
    const length = Math.sqrt(targetVelX * targetVelX + targetVelZ * targetVelZ);
    if (length > 0) {
      targetVelX = (targetVelX / length) * SPEED;
      targetVelZ = (targetVelZ / length) * SPEED;
    }
    
    // Smooth acceleration
    velocityRef.current.x += (targetVelX - velocityRef.current.x) * ACCELERATION;
    velocityRef.current.z += (targetVelZ - velocityRef.current.z) * ACCELERATION;
    
    // Calculate new position
    const newX = groupRef.current.position.x + velocityRef.current.x * delta;
    const newZ = groupRef.current.position.z + velocityRef.current.z * delta;
    
    // Check collision and apply movement
    if (!checkCollision(newX, groupRef.current.position.z)) {
      groupRef.current.position.x = newX;
    }
    if (!checkCollision(groupRef.current.position.x, newZ)) {
      groupRef.current.position.z = newZ;
    }
    
    // Rotate character to face movement direction
    if (Math.abs(velocityRef.current.x) > 0.1 || Math.abs(velocityRef.current.z) > 0.1) {
      const targetRotation = Math.atan2(velocityRef.current.x, velocityRef.current.z);
      rotationRef.current += (targetRotation - rotationRef.current) * 0.1;
      groupRef.current.rotation.y = rotationRef.current;
    }
    
    // Update game state
    const pos = groupRef.current.position;
    setPlayerPosition({ x: pos.x, z: pos.z });
    
    // Check interactions
    const nearDoor = getNearDoor(pos.x, pos.z);
    setNearDoor(nearDoor);
    setNearChair(isNearCEOChair(pos.x, pos.z));
    
    // Handle interaction key
    if (interact) {
      keys.current.interact = false; // Prevent multiple triggers
      
      if (nearDoor) {
        const employee = employees.find(e => e.id === nearDoor);
        if (employee) {
          enterVideoCall(employee);
        }
      } else if (isNearCEOChair(pos.x, pos.z)) {
        enterCEODesk();
      }
    }
  });

  // Low-poly person character
  return (
    <group ref={groupRef} position={[0, 0, 5]}>
      {/* Body */}
      <mesh position={[0, 0.75, 0]} castShadow>
        <boxGeometry args={[0.5, 0.7, 0.3]} />
        <meshStandardMaterial color="#3d5a80" /> {/* Navy blazer */}
      </mesh>
      
      {/* Shirt collar visible */}
      <mesh position={[0, 0.95, 0.12]} castShadow>
        <boxGeometry args={[0.3, 0.15, 0.1]} />
        <meshStandardMaterial color="#f8f9fa" /> {/* White shirt */}
      </mesh>
      
      {/* Head */}
      <mesh position={[0, 1.35, 0]} castShadow>
        <boxGeometry args={[0.35, 0.4, 0.35]} />
        <meshStandardMaterial color="#e8c4a0" /> {/* Skin tone */}
      </mesh>
      
      {/* Hair */}
      <mesh position={[0, 1.55, -0.02]} castShadow>
        <boxGeometry args={[0.36, 0.15, 0.38]} />
        <meshStandardMaterial color="#4a3728" /> {/* Brown hair */}
      </mesh>
      
      {/* Left Leg */}
      <mesh position={[-0.12, 0.25, 0]} castShadow>
        <boxGeometry args={[0.15, 0.5, 0.2]} />
        <meshStandardMaterial color="#2d3436" /> {/* Dark pants */}
      </mesh>
      
      {/* Right Leg */}
      <mesh position={[0.12, 0.25, 0]} castShadow>
        <boxGeometry args={[0.15, 0.5, 0.2]} />
        <meshStandardMaterial color="#2d3436" /> {/* Dark pants */}
      </mesh>
      
      {/* Left Arm */}
      <mesh position={[-0.35, 0.75, 0]} castShadow>
        <boxGeometry args={[0.15, 0.5, 0.15]} />
        <meshStandardMaterial color="#3d5a80" /> {/* Navy blazer */}
      </mesh>
      
      {/* Right Arm */}
      <mesh position={[0.35, 0.75, 0]} castShadow>
        <boxGeometry args={[0.15, 0.5, 0.15]} />
        <meshStandardMaterial color="#3d5a80" /> {/* Navy blazer */}
      </mesh>
    </group>
  );
}
