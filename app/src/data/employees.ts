import { AgentType } from '@/lib/agents';

export interface Employee {
  id: string;
  name: string;
  role: string;
  department: string;
  avatar: string;
  officePosition: { x: number; z: number };
  agentType: AgentType;
  initialMessages: { sender: string; text: string; time: string }[];
}

// Static employee visual data (positions, avatars, names)
// This will be merged with API agent data
export const employeeVisuals: Record<string, Omit<Employee, 'agentType'>> = {
  sarah: {
    id: 'sarah',
    name: 'Sarah',
    role: 'Researcher',
    department: 'Research',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: -8, z: -4 },
    initialMessages: [
      { sender: 'Sarah', text: 'Hi! I can help you with web research and information synthesis. What would you like me to research?', time: '9:00 AM' },
    ],
  },
  james: {
    id: 'james',
    name: 'James',
    role: 'Data Analyst',
    department: 'Analytics',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: -8, z: 4 },
    initialMessages: [
      { sender: 'James', text: 'Hey! I specialize in data visualization and analysis. Let me know if you need any insights.', time: '9:15 AM' },
    ],
  },
  alex: {
    id: 'alex',
    name: 'Alex',
    role: 'Team Lead',
    department: 'Management',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: 8, z: -4 },
    initialMessages: [
      { sender: 'Alex', text: 'Hey! I coordinate tasks and manage team workload. Need help with task assignments?', time: '10:00 AM' },
    ],
  },
  peter: {
    id: 'peter',
    name: 'Peter',
    role: 'Finance',
    department: 'Finance',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
    officePosition: { x: 8, z: 4 },
    initialMessages: [
      { sender: 'Peter', text: 'Welcome! I can help with financial analysis and market research. What insights do you need?', time: '11:00 AM' },
    ],
  },
};

// Map agent types to employee IDs
export const agentToEmployeeMap: Record<AgentType, string> = {
  researcher: 'sarah',
  data_analyst: 'james',
  team_lead: 'alex',
  finance: 'peter',
};

// Helper function to get employee by agent type
export function getEmployeeByAgentType(agentType: AgentType): Employee | undefined {
  const employeeId = agentToEmployeeMap[agentType];
  const visual = employeeVisuals[employeeId];
  if (!visual) return undefined;
  
  return {
    ...visual,
    agentType,
  };
}

// Helper function to get all employees (will be populated from API)
export function getEmployeesFromAgents(agentTypes: AgentType[]): Employee[] {
  return agentTypes
    .map(getEmployeeByAgentType)
    .filter((emp): emp is Employee => emp !== undefined);
}

// Default employees array (for backwards compatibility)
export const employees: Employee[] = [
  { ...employeeVisuals.sarah, agentType: 'researcher' },
  { ...employeeVisuals.james, agentType: 'data_analyst' },
  { ...employeeVisuals.alex, agentType: 'team_lead' },
  { ...employeeVisuals.peter, agentType: 'finance' },
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
