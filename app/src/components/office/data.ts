import { TeamMember, Folder } from './types';

export const teamMembers: TeamMember[] = [
  {
    id: 'dev',
    name: 'Alex Chen',
    role: 'Senior Developer',
    avatar: '👨‍💻',
    bio: 'Full-stack developer with 8 years of experience. Passionate about clean code and innovative solutions. Currently leading the platform modernization initiative.',
    projects: [
      'Platform API v3.0 - Complete backend overhaul',
      'Real-time Dashboard - WebSocket implementation',
      'Mobile App - React Native development'
    ],
    contact: {
      email: 'alex.chen@company.com',
      slack: '@alexchen'
    },
    officePosition: [-8, 0, -5]
  },
  {
    id: 'designer',
    name: 'Sarah Miller',
    role: 'Lead Designer',
    avatar: '👩‍🎨',
    bio: 'Creative director with a passion for user-centered design. Former agency creative lead, now building cohesive brand experiences for our products.',
    projects: [
      'Brand Refresh 2024 - Complete visual identity',
      'Mobile UX Redesign - User research & prototypes',
      'Design System v2 - Component library'
    ],
    contact: {
      email: 'sarah.miller@company.com',
      slack: '@sarahm'
    },
    officePosition: [-8, 0, 5]
  },
  {
    id: 'marketing',
    name: 'Jordan Park',
    role: 'Marketing Director',
    avatar: '📊',
    bio: 'Data-driven marketer focused on growth strategies. Previously at two unicorn startups. Specializes in B2B SaaS marketing and brand positioning.',
    projects: [
      'Q4 Campaign - Multi-channel launch strategy',
      'Content Strategy - SEO & thought leadership',
      'Analytics Dashboard - Marketing ROI tracking'
    ],
    contact: {
      email: 'jordan.park@company.com',
      slack: '@jordanp'
    },
    officePosition: [8, 0, 0]
  }
];

export const ceoFolders: Folder[] = [
  {
    id: 'financials',
    name: 'Financials Q4',
    color: '#3B82F6',
    documents: [
      {
        id: 'revenue',
        title: 'Q4 Revenue Report',
        type: 'chart',
        content: '📈 Q4 Revenue: $2.4M (+23% YoY)\n\nMonthly Breakdown:\n• October: $780K\n• November: $820K\n• December: $800K\n\nKey Metrics:\n• MRR: $200K\n• ARR: $2.4M\n• Churn Rate: 2.3%',
        description: 'Quarterly financial performance summary'
      },
      {
        id: 'expenses',
        title: 'Operating Expenses',
        type: 'report',
        content: '💰 Total OpEx: $1.8M\n\nBreakdown:\n• Salaries: $1.2M (67%)\n• Infrastructure: $280K (16%)\n• Marketing: $180K (10%)\n• Office & Admin: $140K (8%)\n\nBurn Rate: $150K/month\nRunway: 18 months',
        description: 'Detailed expense breakdown'
      }
    ]
  },
  {
    id: 'strategy',
    name: 'Strategy 2025',
    color: '#10B981',
    documents: [
      {
        id: 'roadmap',
        title: 'Product Roadmap',
        type: 'report',
        content: '🚀 2025 Product Vision\n\nQ1: Platform 3.0 Launch\n• New API architecture\n• Enhanced security features\n• Mobile app beta\n\nQ2: Enterprise Features\n• SSO integration\n• Advanced analytics\n• Custom workflows\n\nQ3: AI Integration\n• Smart automation\n• Predictive insights\n\nQ4: Global Expansion\n• Multi-region support\n• Localization',
        description: 'Annual product development plan'
      },
      {
        id: 'goals',
        title: 'Company OKRs',
        type: 'report',
        content: '🎯 2025 Objectives\n\nObjective 1: Scale Revenue\n• KR1: Achieve $5M ARR\n• KR2: 500 enterprise customers\n• KR3: <2% monthly churn\n\nObjective 2: Build World-Class Team\n• KR1: Grow to 50 employees\n• KR2: 90% retention rate\n• KR3: eNPS score >60\n\nObjective 3: Product Excellence\n• KR1: NPS >50\n• KR2: 99.9% uptime\n• KR3: <2hr support response',
        description: 'Annual company objectives and key results'
      }
    ]
  },
  {
    id: 'team',
    name: 'Team Updates',
    color: '#8B5CF6',
    documents: [
      {
        id: 'org',
        title: 'Organization Chart',
        type: 'image',
        content: '👥 Current Team Structure\n\n┌─────────────┐\n│     CEO     │\n└──────┬──────┘\n       │\n┌──────┴──────────────┐\n│                     │\n▼                     ▼\n┌─────────┐    ┌─────────┐\n│  Tech   │    │Business │\n│  Team   │    │  Team   │\n└────┬────┘    └────┬────┘\n     │              │\n  ┌──┴──┐       ┌──┴──┐\n  │Dev  │       │Sales│\n  │Team │       │Mktg │\n  └─────┘       └─────┘\n\nTotal Headcount: 24',
        description: 'Current organizational structure'
      },
      {
        id: 'hiring',
        title: 'Hiring Pipeline',
        type: 'report',
        content: '📋 Active Positions\n\n🟢 In Progress:\n• Senior Backend Engineer (3 candidates)\n• Product Designer (2 candidates)\n• Sales Manager (5 candidates)\n\n🟡 Open:\n• DevOps Engineer\n• Customer Success Manager\n• Content Writer\n\n🔵 Planned Q1:\n• Data Scientist\n• Mobile Developer\n• HR Manager',
        description: 'Current recruitment status'
      }
    ]
  },
  {
    id: 'projects',
    name: 'Active Projects',
    color: '#F59E0B',
    documents: [
      {
        id: 'status',
        title: 'Project Status',
        type: 'report',
        content: '📊 Project Health Dashboard\n\n✅ On Track:\n• Platform v3.0 - 78% complete\n• Mobile App - 45% complete\n• Design System - 90% complete\n\n⚠️ At Risk:\n• Enterprise Portal - Resource constraints\n• API Migration - Technical challenges\n\n🔄 In Planning:\n• AI Features\n• Analytics Dashboard\n• Partner Portal',
        description: 'Overview of all active projects'
      }
    ]
  }
];
