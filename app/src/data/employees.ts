export interface Employee {
  id: string;
  name: string;
  role: string;
  department: string;
  avatar: string;
  officePosition: { x: number; z: number };
  initialMessages: { sender: string; text: string; time: string }[];
}

export const employees: Employee[] = [
  {
    id: 'sarah',
    name: 'Sarah Mitchell',
    role: 'Marketing Manager',
    department: 'Marketing',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: -8, z: -4 },
    initialMessages: [
      { sender: 'Sarah', text: 'Hi! Welcome to the marketing team office!', time: '9:00 AM' },
      { sender: 'Sarah', text: 'We\'re working on the Q2 campaign strategy.', time: '9:01 AM' },
      { sender: 'Sarah', text: 'Feel free to check out our latest brand materials.', time: '9:02 AM' },
    ],
  },
  {
    id: 'james',
    name: 'James Chen',
    role: 'Senior Developer',
    department: 'Engineering',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: -8, z: 4 },
    initialMessages: [
      { sender: 'James', text: 'Hey there! Welcome to my dev cave.', time: '9:15 AM' },
      { sender: 'James', text: 'Just pushed some updates to the main branch.', time: '9:16 AM' },
      { sender: 'James', text: 'Let me know if you need any technical help!', time: '9:17 AM' },
    ],
  },
  {
    id: 'alex',
    name: 'Alex Rivera',
    role: 'UI/UX Designer',
    department: 'Design',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: 8, z: -4 },
    initialMessages: [
      { sender: 'Alex', text: 'Hey! Great to see you.', time: '10:00 AM' },
      { sender: 'Alex', text: 'I\'m finalizing the new dashboard mockups.', time: '10:01 AM' },
      { sender: 'Alex', text: 'Want me to walk you through the design system?', time: '10:02 AM' },
    ],
  },
  {
    id: 'peter',
    name: 'Peter Williams',
    role: 'HR Specialist',
    department: 'Human Resources',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: 8, z: 4 },
    initialMessages: [
      { sender: 'Peter', text: 'Welcome! Happy to help with any HR questions.', time: '11:00 AM' },
      { sender: 'Peter', text: 'We just updated the employee handbook.', time: '11:01 AM' },
      { sender: 'Peter', text: 'Feel free to reach out anytime!', time: '11:02 AM' },
    ],
  },
];

export interface CEOFolder {
  id: string;
  name: string;
  icon: string;
  content: {
    title: string;
    description: string;
    items?: string[];
  };
  isConfidential?: boolean;
}

export const ceoFolders: CEOFolder[] = [
  {
    id: 'project-alpha',
    name: 'Project Alpha',
    icon: '📁',
    content: {
      title: 'Project Alpha - Timeline',
      description: 'Next-generation product launch initiative',
      items: [
        'Phase 1: Research & Discovery (Complete)',
        'Phase 2: Prototype Development (In Progress)',
        'Phase 3: Beta Testing (Q3 2024)',
        'Phase 4: Public Launch (Q4 2024)',
      ],
    },
  },
  {
    id: 'quarterly-reports',
    name: 'Quarterly Reports',
    icon: '📊',
    content: {
      title: 'Q1 2024 Financial Summary',
      description: 'Company performance metrics and analysis',
      items: [
        'Revenue: $2.4M (+15% YoY)',
        'Operating Margin: 22%',
        'Customer Growth: +340 new accounts',
        'Employee Satisfaction: 4.2/5',
      ],
    },
  },
  {
    id: 'team-reviews',
    name: 'Team Reviews',
    icon: '👥',
    content: {
      title: 'Annual Performance Reviews',
      description: 'Department-wide evaluation summaries',
      items: [
        'Engineering: Exceeds Expectations',
        'Marketing: Meets Expectations',
        'Design: Exceeds Expectations',
        'HR: Meets Expectations',
      ],
    },
  },
  {
    id: 'strategic-plans',
    name: 'Strategic Plans',
    icon: '🎯',
    content: {
      title: '2024 Strategic Roadmap',
      description: 'Company vision and key initiatives',
      items: [
        'Expand to European markets',
        'Launch mobile application',
        'Achieve SOC 2 compliance',
        'Grow team to 50 employees',
      ],
    },
  },
  {
    id: 'confidential',
    name: 'Confidential',
    icon: '🔒',
    content: {
      title: 'Access Denied',
      description: 'You do not have permission to view this folder.',
    },
    isConfidential: true,
  },
];
