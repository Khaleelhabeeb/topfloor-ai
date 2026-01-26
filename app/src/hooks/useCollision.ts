import { useMemo } from 'react';

export interface CollisionBox {
  id: string;
  minX: number;
  maxX: number;
  minZ: number;
  maxZ: number;
  isDoor?: boolean;
  isCEOChair?: boolean;
}

// Office layout collision boundaries
export function useCollision() {
  const collisionBoxes = useMemo<CollisionBox[]>(() => [
    // Outer walls
    { id: 'wall-north', minX: -15, maxX: 15, minZ: -12, maxZ: -11 },
    { id: 'wall-south', minX: -15, maxX: 15, minZ: 11, maxZ: 12 },
    { id: 'wall-west', minX: -15, maxX: -14, minZ: -12, maxZ: 12 },
    { id: 'wall-east', minX: 14, maxX: 15, minZ: -12, maxZ: 12 },
    
    // Sarah's office walls (top-left)
    { id: 'sarah-wall-south', minX: -14, maxX: -5, minZ: -1.5, maxZ: -0.5 },
    { id: 'sarah-wall-east', minX: -5.5, maxX: -4.5, minZ: -11, maxZ: -3 },
    
    // James's office walls (bottom-left)
    { id: 'james-wall-north', minX: -14, maxX: -5, minZ: 0.5, maxZ: 1.5 },
    { id: 'james-wall-east', minX: -5.5, maxX: -4.5, minZ: 3, maxZ: 11 },
    
    // Alex's office walls (top-right)
    { id: 'alex-wall-south', minX: 5, maxX: 14, minZ: -1.5, maxZ: -0.5 },
    { id: 'alex-wall-west', minX: 4.5, maxX: 5.5, minZ: -11, maxZ: -3 },
    
    // Peter's office walls (bottom-right)
    { id: 'peter-wall-north', minX: 5, maxX: 14, minZ: 0.5, maxZ: 1.5 },
    { id: 'peter-wall-west', minX: 4.5, maxX: 5.5, minZ: 3, maxZ: 11 },
    
    // Office furniture (simplified)
    { id: 'sarah-desk', minX: -12, maxX: -9, minZ: -9, maxZ: -7 },
    { id: 'james-desk', minX: -12, maxX: -9, minZ: 7, maxZ: 9 },
    { id: 'alex-desk', minX: 9, maxX: 12, minZ: -9, maxZ: -7 },
    { id: 'peter-desk', minX: 9, maxX: 12, minZ: 7, maxZ: 9 },
    
    // CEO office area
    { id: 'ceo-desk', minX: -2, maxX: 2, minZ: -10, maxZ: -8 },
  ], []);

  const doorZones = useMemo<CollisionBox[]>(() => [
    { id: 'sarah', minX: -5.5, maxX: -4.5, minZ: -3, maxZ: -1.5, isDoor: true },
    { id: 'james', minX: -5.5, maxX: -4.5, minZ: 1.5, maxZ: 3, isDoor: true },
    { id: 'alex', minX: 4.5, maxX: 5.5, minZ: -3, maxZ: -1.5, isDoor: true },
    { id: 'peter', minX: 4.5, maxX: 5.5, minZ: 1.5, maxZ: 3, isDoor: true },
  ], []);

  const ceoChairZone = useMemo<CollisionBox>(() => ({
    id: 'ceo-chair',
    minX: -1,
    maxX: 1,
    minZ: -7.5,
    maxZ: -6,
    isCEOChair: true,
  }), []);

  const checkCollision = (x: number, z: number, radius: number = 0.4): boolean => {
    for (const box of collisionBoxes) {
      if (
        x + radius > box.minX &&
        x - radius < box.maxX &&
        z + radius > box.minZ &&
        z - radius < box.maxZ
      ) {
        return true;
      }
    }
    return false;
  };

  const getNearDoor = (x: number, z: number): string | null => {
    for (const door of doorZones) {
      if (
        x > door.minX - 1 &&
        x < door.maxX + 1 &&
        z > door.minZ - 1 &&
        z < door.maxZ + 1
      ) {
        return door.id;
      }
    }
    return null;
  };

  const isNearCEOChair = (x: number, z: number): boolean => {
    return (
      x > ceoChairZone.minX - 1 &&
      x < ceoChairZone.maxX + 1 &&
      z > ceoChairZone.minZ - 1 &&
      z < ceoChairZone.maxZ + 1
    );
  };

  return {
    collisionBoxes,
    doorZones,
    ceoChairZone,
    checkCollision,
    getNearDoor,
    isNearCEOChair,
  };
}
