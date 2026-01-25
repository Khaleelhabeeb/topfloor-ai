import { useRef, useEffect, useCallback } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { CollisionSystem } from './CollisionSystem';

interface FirstPersonControlsProps {
  speed?: number;
  enabled?: boolean;
  onPositionChange?: (position: THREE.Vector3) => void;
  collisionSystem?: CollisionSystem;
}

export function FirstPersonControls({ 
  speed = 4, 
  enabled = true,
  onPositionChange,
  collisionSystem 
}: FirstPersonControlsProps) {
  const { camera, gl } = useThree();
  const moveState = useRef({
    forward: false,
    backward: false,
    left: false,
    right: false
  });
  const euler = useRef(new THREE.Euler(0, 0, 0, 'YXZ'));
  const isLocked = useRef(false);

  const onKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;
    switch (event.code) {
      case 'KeyW':
      case 'ArrowUp':
        moveState.current.forward = true;
        break;
      case 'KeyS':
      case 'ArrowDown':
        moveState.current.backward = true;
        break;
      case 'KeyA':
      case 'ArrowLeft':
        moveState.current.left = true;
        break;
      case 'KeyD':
      case 'ArrowRight':
        moveState.current.right = true;
        break;
    }
  }, [enabled]);

  const onKeyUp = useCallback((event: KeyboardEvent) => {
    switch (event.code) {
      case 'KeyW':
      case 'ArrowUp':
        moveState.current.forward = false;
        break;
      case 'KeyS':
      case 'ArrowDown':
        moveState.current.backward = false;
        break;
      case 'KeyA':
      case 'ArrowLeft':
        moveState.current.left = false;
        break;
      case 'KeyD':
      case 'ArrowRight':
        moveState.current.right = false;
        break;
    }
  }, []);

  const onMouseMove = useCallback((event: MouseEvent) => {
    if (!isLocked.current || !enabled) return;

    const movementX = event.movementX || 0;
    const movementY = event.movementY || 0;

    euler.current.setFromQuaternion(camera.quaternion);
    euler.current.y -= movementX * 0.002;
    euler.current.x -= movementY * 0.002;
    euler.current.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.current.x));
    
    camera.quaternion.setFromEuler(euler.current);
  }, [camera, enabled]);

  const onPointerLockChange = useCallback(() => {
    isLocked.current = document.pointerLockElement === gl.domElement;
  }, [gl]);

  const onClick = useCallback(() => {
    if (enabled && !isLocked.current) {
      gl.domElement.requestPointerLock();
    }
  }, [gl, enabled]);

  useEffect(() => {
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('pointerlockchange', onPointerLockChange);
    gl.domElement.addEventListener('click', onClick);

    // Set initial camera position
    camera.position.set(0, 1.7, 10);

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('keyup', onKeyUp);
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('pointerlockchange', onPointerLockChange);
      gl.domElement.removeEventListener('click', onClick);
      
      if (document.pointerLockElement === gl.domElement) {
        document.exitPointerLock();
      }
    };
  }, [onKeyDown, onKeyUp, onMouseMove, onPointerLockChange, onClick, gl, camera]);

  useFrame((_, delta) => {
    if (!enabled) return;

    const direction = new THREE.Vector3();
    const frontVector = new THREE.Vector3(0, 0, Number(moveState.current.backward) - Number(moveState.current.forward));
    const sideVector = new THREE.Vector3(Number(moveState.current.left) - Number(moveState.current.right), 0, 0);

    direction
      .subVectors(frontVector, sideVector)
      .normalize()
      .multiplyScalar(speed * delta)
      .applyEuler(new THREE.Euler(0, euler.current.y, 0));

    // Calculate new position
    const newPosition = camera.position.clone().add(direction);
    newPosition.y = 1.7; // Keep at eye level

    // Check collision if collision system is available
    if (collisionSystem) {
      if (!collisionSystem.checkCollision(newPosition)) {
        camera.position.copy(newPosition);
      } else {
        // Try moving only on X axis
        const newX = camera.position.clone();
        newX.x = newPosition.x;
        if (!collisionSystem.checkCollision(newX)) {
          camera.position.copy(newX);
        } else {
          // Try moving only on Z axis
          const newZ = camera.position.clone();
          newZ.z = newPosition.z;
          if (!collisionSystem.checkCollision(newZ)) {
            camera.position.copy(newZ);
          }
        }
      }
    } else {
      // Fallback to old boundary system
      const newX = camera.position.x + direction.x;
      const newZ = camera.position.z + direction.z;

      // Hallway boundaries
      if (Math.abs(newX) < 1.8 && Math.abs(newZ) < 14) {
        camera.position.x = newX;
        camera.position.z = newZ;
      }
      // Office entrance zones - allow wider movement when in office areas
      else if (newZ < -10 && newZ > -18 && Math.abs(newX) < 4) {
        // CEO office zone
        camera.position.x = newX;
        camera.position.z = newZ;
      } else if (Math.abs(newX) > 1.8 && Math.abs(newX) < 10) {
        // Side offices zone
        camera.position.x = newX;
        camera.position.z = newZ;
      }
    }

    camera.position.y = 1.7; // Keep at eye level

    if (onPositionChange) {
      onPositionChange(camera.position.clone());
    }
  });

  return null;
}
