import * as THREE from 'three';

export interface CollisionBox {
  min: THREE.Vector3;
  max: THREE.Vector3;
  type: 'wall' | 'door' | 'furniture';
  id?: string;
}

export interface DoorState {
  id: string;
  isOpen: boolean;
  position: THREE.Vector3;
  rotation: number;
}

export class CollisionSystem {
  private collisionBoxes: CollisionBox[] = [];
  private doorStates: Map<string, DoorState> = new Map();

  constructor() {
    this.initializeCollisionBoxes();
    this.initializeDoors();
  }

  private initializeCollisionBoxes() {
    const hallwayWidth = 4;
    const hallwayLength = 30;
    const hallwayHeight = 3.5;
    const wallThickness = 0.2;

    // Hallway walls
    this.collisionBoxes.push(
      // Left wall (with door openings)
      { min: new THREE.Vector3(-hallwayWidth/2 - wallThickness, 0, -hallwayLength/2), max: new THREE.Vector3(-hallwayWidth/2, hallwayHeight, -8), type: 'wall' },
      { min: new THREE.Vector3(-hallwayWidth/2 - wallThickness, 0, -2), max: new THREE.Vector3(-hallwayWidth/2, hallwayHeight, 2), type: 'wall' },
      { min: new THREE.Vector3(-hallwayWidth/2 - wallThickness, 0, 8), max: new THREE.Vector3(-hallwayWidth/2, hallwayHeight, hallwayLength/2), type: 'wall' },
      
      // Right wall (with door opening)
      { min: new THREE.Vector3(hallwayWidth/2, 0, -hallwayLength/2), max: new THREE.Vector3(hallwayWidth/2 + wallThickness, hallwayHeight, -3), type: 'wall' },
      { min: new THREE.Vector3(hallwayWidth/2, 0, 3), max: new THREE.Vector3(hallwayWidth/2 + wallThickness, hallwayHeight, hallwayLength/2), type: 'wall' },
      
      // End walls
      { min: new THREE.Vector3(-hallwayWidth/2, 0, hallwayLength/2), max: new THREE.Vector3(hallwayWidth/2, hallwayHeight, hallwayLength/2 + wallThickness), type: 'wall' },
      { min: new THREE.Vector3(-hallwayWidth/2, 0, -hallwayLength/2 - wallThickness), max: new THREE.Vector3(hallwayWidth/2, hallwayHeight, -hallwayLength/2), type: 'wall' }
    );

    // Office room walls
    const officeSize = 6;
    const officeHeight = 3;
    
    // Developer office (-6, 0, -5)
    this.addOfficeWalls([-6, 0, -5], officeSize, officeHeight, 'dev-office');
    
    // Designer office (-6, 0, 5)
    this.addOfficeWalls([-6, 0, 5], officeSize, officeHeight, 'designer-office');
    
    // Marketing office (6, 0, 0)
    this.addOfficeWalls([6, 0, 0], officeSize, officeHeight, 'marketing-office');
    
    // CEO office (0, 0, -18)
    this.addOfficeWalls([0, 0, -18], 8, 3.5, 'ceo-office');
  }

  private addOfficeWalls(position: [number, number, number], size: number, height: number, officeId: string) {
    const [x, y, z] = position;
    const halfSize = size / 2;
    const wallThickness = 0.15;

    // Only add walls that don't interfere with door access
    // Each office has different wall configurations based on door position

    if (officeId === 'dev-office') {
      // Developer office at (-6, 0, -5) - door faces hallway (positive Z direction)
      // Back wall (away from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize, y, z - halfSize - wallThickness),
        max: new THREE.Vector3(x + halfSize, y + height, z - halfSize),
        type: 'wall',
        id: `${officeId}-back`
      });
      // Left wall (extends from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize - wallThickness, y, z - halfSize),
        max: new THREE.Vector3(x - halfSize, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-left`
      });
      // Right wall (closes off the office)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x + halfSize, y, z - halfSize),
        max: new THREE.Vector3(x + halfSize + wallThickness, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-right`
      });
    } else if (officeId === 'designer-office') {
      // Designer office at (-6, 0, 5) - door faces hallway (negative Z direction)
      // Back wall (away from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize, y, z + halfSize),
        max: new THREE.Vector3(x + halfSize, y + height, z + halfSize + wallThickness),
        type: 'wall',
        id: `${officeId}-back`
      });
      // Left wall (extends from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize - wallThickness, y, z - halfSize),
        max: new THREE.Vector3(x - halfSize, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-left`
      });
      // Right wall (closes off the office)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x + halfSize, y, z - halfSize),
        max: new THREE.Vector3(x + halfSize + wallThickness, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-right`
      });
    } else if (officeId === 'marketing-office') {
      // Marketing office at (6, 0, 0) - door faces hallway (negative X direction)
      // Back wall (away from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x + halfSize, y, z - halfSize),
        max: new THREE.Vector3(x + halfSize + wallThickness, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-back`
      });
      // Left wall
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize, y, z - halfSize - wallThickness),
        max: new THREE.Vector3(x + halfSize, y + height, z - halfSize),
        type: 'wall',
        id: `${officeId}-left`
      });
      // Right wall
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize, y, z + halfSize),
        max: new THREE.Vector3(x + halfSize, y + height, z + halfSize + wallThickness),
        type: 'wall',
        id: `${officeId}-right`
      });
    } else if (officeId === 'ceo-office') {
      // CEO office at (0, 0, -18) - door faces hallway (positive Z direction)
      // Back wall (away from hallway)
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize, y, z - halfSize - wallThickness),
        max: new THREE.Vector3(x + halfSize, y + height, z - halfSize),
        type: 'wall',
        id: `${officeId}-back`
      });
      // Left wall
      this.collisionBoxes.push({
        min: new THREE.Vector3(x - halfSize - wallThickness, y, z - halfSize),
        max: new THREE.Vector3(x - halfSize, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-left`
      });
      // Right wall
      this.collisionBoxes.push({
        min: new THREE.Vector3(x + halfSize, y, z - halfSize),
        max: new THREE.Vector3(x + halfSize + wallThickness, y + height, z + halfSize),
        type: 'wall',
        id: `${officeId}-right`
      });
    }
  }

  private initializeDoors() {
    // Initialize door states
    this.doorStates.set('dev-office-door', {
      id: 'dev-office-door',
      isOpen: false,
      position: new THREE.Vector3(-2, 0, -5),
      rotation: Math.PI / 2
    });

    this.doorStates.set('designer-office-door', {
      id: 'designer-office-door',
      isOpen: false,
      position: new THREE.Vector3(-2, 0, 5),
      rotation: Math.PI / 2
    });

    this.doorStates.set('marketing-office-door', {
      id: 'marketing-office-door',
      isOpen: false,
      position: new THREE.Vector3(2, 0, 0),
      rotation: -Math.PI / 2
    });

    this.doorStates.set('ceo-office-door', {
      id: 'ceo-office-door',
      isOpen: false,
      position: new THREE.Vector3(0, 0, -13),
      rotation: 0
    });
  }

  checkCollision(newPosition: THREE.Vector3, playerRadius: number = 0.3): boolean {
    const playerBox = {
      min: new THREE.Vector3(
        newPosition.x - playerRadius,
        newPosition.y,
        newPosition.z - playerRadius
      ),
      max: new THREE.Vector3(
        newPosition.x + playerRadius,
        newPosition.y + 1.8, // Player height
        newPosition.z + playerRadius
      )
    };

    for (const box of this.collisionBoxes) {
      if (this.boxIntersects(playerBox, box)) {
        // Check if this is a door collision and if the door is open
        if (box.type === 'door' && box.id) {
          const doorState = this.doorStates.get(box.id);
          if (doorState && doorState.isOpen) {
            continue; // Allow passage through open doors
          }
        }
        return true; // Collision detected
      }
    }

    return false; // No collision
  }

  private boxIntersects(box1: { min: THREE.Vector3; max: THREE.Vector3 }, box2: CollisionBox): boolean {
    return (
      box1.min.x <= box2.max.x &&
      box1.max.x >= box2.min.x &&
      box1.min.y <= box2.max.y &&
      box1.max.y >= box2.min.y &&
      box1.min.z <= box2.max.z &&
      box1.max.z >= box2.min.z
    );
  }

  openDoor(doorId: string) {
    const door = this.doorStates.get(doorId);
    if (door) {
      door.isOpen = true;
      this.doorStates.set(doorId, door);
    }
  }

  closeDoor(doorId: string) {
    const door = this.doorStates.get(doorId);
    if (door) {
      door.isOpen = false;
      this.doorStates.set(doorId, door);
    }
  }

  isDoorOpen(doorId: string): boolean {
    const door = this.doorStates.get(doorId);
    return door ? door.isOpen : false;
  }

  getDoorState(doorId: string): DoorState | undefined {
    return this.doorStates.get(doorId);
  }

  getAllDoors(): DoorState[] {
    return Array.from(this.doorStates.values());
  }

  getPlayerRoom(position: THREE.Vector3): string {
    // Developer office - left side, behind door at (-2, 0, -5)
    if (position.x < -2.5 && position.z > -8 && position.z < -2) {
      return 'office1';
    }
    // Designer office - left side, behind door at (-2, 0, 5)
    if (position.x < -2.5 && position.z > 2 && position.z < 8) {
      return 'office2';
    }
    // Marketing office - right side, behind door at (2, 0, 0)
    if (position.x > 2.5 && position.z > -3 && position.z < 3) {
      return 'office3';
    }
    // CEO office - behind door at (0, 0, -13)
    if (position.z < -13.5) {
      return 'ceo';
    }
    // Hallway
    return 'hallway';
  }
}