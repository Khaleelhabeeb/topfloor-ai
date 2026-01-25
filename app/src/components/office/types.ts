export interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  bio: string;
  projects: string[];
  contact: {
    email: string;
    slack: string;
  };
  officePosition: [number, number, number];
}

export interface Folder {
  id: string;
  name: string;
  color: string;
  documents: Document[];
}

export interface Document {
  id: string;
  title: string;
  type: 'image' | 'report' | 'chart';
  content: string;
  description?: string;
}

export interface OfficeState {
  currentRoom: 'hallway' | 'office1' | 'office2' | 'office3' | 'ceo';
  isSeated: boolean;
  activeFolder: Folder | null;
  activeMember: TeamMember | null;
}
