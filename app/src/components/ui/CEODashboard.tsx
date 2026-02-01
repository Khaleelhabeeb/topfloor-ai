import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useGameState } from '@/hooks/useGameState';
import { employees } from '@/data/employees';
import { 
  X,
  Settings,
  History,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Clock,
  AlertCircle,
  Send,
  AtSign,
  TrendingUp,
  Users,
  Target,
  Activity
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  status: 'completed' | 'in-progress' | 'pending';
  priority: 'high' | 'medium' | 'low';
  assignedTo: string; // employee id
  dueDate: string;
  progress: number;
}

interface ChatMessage {
  id: string;
  sender: string;
  senderId: string;
  text: string;
  time: string;
  mentionedAgent?: string;
  isFromCEO?: boolean;
}

const ceoTasks: Task[] = [
  {
    id: '1',
    title: 'Q2 Marketing Campaign Strategy',
    status: 'in-progress',
    priority: 'high',
    assignedTo: 'sarah',
    dueDate: '2024-02-15',
    progress: 65
  },
  {
    id: '2',
    title: 'Mobile App Development Sprint',
    status: 'in-progress',
    priority: 'high',
    assignedTo: 'james',
    dueDate: '2024-02-20',
    progress: 45
  },
  {
    id: '3',
    title: 'Dashboard UI Redesign',
    status: 'in-progress',
    priority: 'medium',
    assignedTo: 'alex',
    dueDate: '2024-02-18',
    progress: 80
  },
  {
    id: '4',
    title: 'Employee Onboarding Process',
    status: 'completed',
    priority: 'medium',
    assignedTo: 'peter',
    dueDate: '2024-02-10',
    progress: 100
  },
  {
    id: '5',
    title: 'Brand Guidelines Update',
    status: 'pending',
    priority: 'low',
    assignedTo: 'sarah',
    dueDate: '2024-02-25',
    progress: 0
  },
  {
    id: '6',
    title: 'API Integration Testing',
    status: 'in-progress',
    priority: 'high',
    assignedTo: 'james',
    dueDate: '2024-02-16',
    progress: 55
  },
  {
    id: '7',
    title: 'Performance Review Templates',
    status: 'pending',
    priority: 'medium',
    assignedTo: 'peter',
    dueDate: '2024-02-22',
    progress: 0
  }
];

const mockHistory = [
  { date: '2024-02-01', action: 'Assigned new task to Sarah', details: 'Q2 Marketing Campaign' },
  { date: '2024-01-30', action: 'Completed quarterly review', details: 'All departments' },
  { date: '2024-01-28', action: 'Approved budget increase', details: 'Engineering team' },
  { date: '2024-01-25', action: 'Meeting with stakeholders', details: 'Product roadmap' },
  { date: '2024-01-22', action: 'Task reassignment', details: 'Mobile app development' },
];

export function CEODashboard() {
  const { mode, exitCEODesk } = useGameState();
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'System',
      senderId: 'system',
      text: 'Welcome to the CEO Dashboard. Use @ to mention team members.',
      time: '9:00 AM',
      isFromCEO: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [showMentionMenu, setShowMentionMenu] = useState(false);
  const [mentionFilter, setMentionFilter] = useState('');
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !showMentionMenu) {
        exitCEODesk();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [exitCEODesk, showMentionMenu]);

  if (mode !== 'ceo-desk') return null;

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'in-progress':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
    }
  };

  const getStatusBadge = (status: Task['status']) => {
    const variants = {
      completed: 'default',
      'in-progress': 'secondary',
      pending: 'outline'
    } as const;
    
    return (
      <Badge variant={variants[status]} className="text-xs">
        {status.replace('-', ' ')}
      </Badge>
    );
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-500';
      case 'medium':
        return 'border-l-yellow-500';
      case 'low':
        return 'border-l-green-500';
    }
  };

  const getAssignedEmployee = (employeeId: string) => {
    return employees.find(e => e.id === employeeId);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);

    // Check for @ mention
    const lastAtIndex = value.lastIndexOf('@');
    if (lastAtIndex !== -1 && lastAtIndex === value.length - 1) {
      setShowMentionMenu(true);
      setMentionFilter('');
    } else if (lastAtIndex !== -1 && showMentionMenu) {
      const filter = value.substring(lastAtIndex + 1);
      setMentionFilter(filter.toLowerCase());
    } else if (!value.includes('@')) {
      setShowMentionMenu(false);
    }
  };

  const handleMentionSelect = (employee: typeof employees[0]) => {
    const lastAtIndex = inputValue.lastIndexOf('@');
    const newValue = inputValue.substring(0, lastAtIndex) + `@${employee.name.split(' ')[0]} `;
    setInputValue(newValue);
    setShowMentionMenu(false);
    inputRef.current?.focus();
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });

    // Check if message mentions someone
    const mentionMatch = inputValue.match(/@(\w+)/);
    const mentionedName = mentionMatch ? mentionMatch[1] : undefined;
    const mentionedEmployee = employees.find(e => 
      e.name.toLowerCase().includes(mentionedName?.toLowerCase() || '')
    );

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'You (CEO)',
      senderId: 'ceo',
      text: inputValue,
      time: timeString,
      mentionedAgent: mentionedEmployee?.id,
      isFromCEO: true
    };

    setChatMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // Simulate response from mentioned agent
    if (mentionedEmployee) {
      setTimeout(() => {
        const responses = [
          `Got it! I'll look into that right away.`,
          `Thanks for reaching out. I'm on it!`,
          `Understood. I'll update you on the progress.`,
          `Perfect timing! I was just working on this.`,
          `I'll prioritize this and get back to you soon.`
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        setChatMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          sender: mentionedEmployee.name.split(' ')[0],
          senderId: mentionedEmployee.id,
          text: randomResponse,
          time: new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          }),
          isFromCEO: false
        }]);
      }, 1000 + Math.random() * 1500);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !showMentionMenu) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const filteredEmployees = employees.filter(emp => 
    emp.name.toLowerCase().includes(mentionFilter)
  );

  const tasksByEmployee = employees.map(emp => ({
    employee: emp,
    tasks: ceoTasks.filter(t => t.assignedTo === emp.id)
  }));

  const stats = {
    totalTasks: ceoTasks.length,
    completed: ceoTasks.filter(t => t.status === 'completed').length,
    inProgress: ceoTasks.filter(t => t.status === 'in-progress').length,
    pending: ceoTasks.filter(t => t.status === 'pending').length,
    avgProgress: Math.round(ceoTasks.reduce((acc, t) => acc + t.progress, 0) / ceoTasks.length)
  };

  return (
    <div className="fixed inset-0 bg-background z-50 flex animate-fade-in">
      {/* History Sidebar - Toggleable */}
      <div 
        className={`bg-card border-r border-border transition-all duration-300 ${
          showHistory ? 'w-72' : 'w-0'
        } overflow-hidden`}
      >
        {showHistory && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">Activity History</h3>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setShowHistory(false)}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-3">
                {mockHistory.map((item, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <p className="text-xs text-muted-foreground mb-1">
                      {item.date}
                    </p>
                    <p className="text-sm font-medium text-foreground">
                      {item.action}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {item.details}
                    </p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            {!showHistory && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistory(true)}
                className="h-9 w-9"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
            
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500/20 to-amber-600/10 flex items-center justify-center">
                <Target className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <h2 className="font-semibold text-foreground">CEO Dashboard</h2>
                <p className="text-xs text-muted-foreground">
                  Executive Command Center
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>
            
            <Separator orientation="vertical" className="h-6" />
            
            <Button
              variant="ghost"
              size="icon"
              onClick={exitCEODesk}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main Dashboard */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="max-w-6xl mx-auto space-y-6">
              {/* Settings Panel */}
              {showSettings && (
                <Card className="animate-scale-in">
                  <CardHeader>
                    <CardTitle className="text-lg">Dashboard Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Task Notifications</p>
                        <p className="text-xs text-muted-foreground">
                          Get notified when tasks are completed
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Configure
                      </Button>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Auto-assign Tasks</p>
                        <p className="text-xs text-muted-foreground">
                          Automatically distribute tasks based on workload
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Enable
                      </Button>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Report Generation</p>
                        <p className="text-xs text-muted-foreground">
                          Schedule automated performance reports
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Schedule
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Stats Overview */}
              <div className="grid grid-cols-5 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                        <Activity className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-foreground">
                          {stats.totalTasks}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Total Tasks
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-green-500">
                          {stats.completed}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Completed
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                        <Clock className="h-5 w-5 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-blue-500">
                          {stats.inProgress}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          In Progress
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-orange-500/10 flex items-center justify-center">
                        <AlertCircle className="h-5 w-5 text-orange-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-orange-500">
                          {stats.pending}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Pending
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-500/10 flex items-center justify-center">
                        <TrendingUp className="h-5 w-5 text-purple-500" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-purple-500">
                          {stats.avgProgress}%
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Avg Progress
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Tasks by Agent */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Tasks by Agent</CardTitle>
                    <Badge variant="secondary" className="gap-1">
                      <Users className="h-3 w-3" />
                      {employees.length} Agents
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {tasksByEmployee.map(({ employee, tasks }) => (
                      <div key={employee.id} className="space-y-3">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={employee.avatar} alt={employee.name} />
                            <AvatarFallback>
                              {employee.name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="font-medium text-sm text-foreground">
                              {employee.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {employee.role} • {tasks.length} tasks
                            </p>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setInputValue(`@${employee.name.split(' ')[0]} `)}
                          >
                            <AtSign className="h-3 w-3 mr-1" />
                            Message
                          </Button>
                        </div>
                        
                        {tasks.length > 0 && (
                          <div className="ml-11 space-y-2">
                            {tasks.map((task) => (
                              <div
                                key={task.id}
                                className={`p-3 rounded-lg border-l-4 ${getPriorityColor(task.priority)} bg-muted/30`}
                              >
                                <div className="flex items-start justify-between gap-4">
                                  <div className="flex items-start gap-3 flex-1">
                                    {getStatusIcon(task.status)}
                                    <div className="flex-1 min-w-0">
                                      <h4 className="font-medium text-sm text-foreground mb-1">
                                        {task.title}
                                      </h4>
                                      <div className="flex items-center gap-2 flex-wrap mb-2">
                                        {getStatusBadge(task.status)}
                                        <Badge variant="outline" className="text-xs">
                                          {task.priority}
                                        </Badge>
                                        <span className="text-xs text-muted-foreground">
                                          Due: {task.dueDate}
                                        </span>
                                      </div>
                                      {/* Progress bar */}
                                      <div className="w-full bg-muted rounded-full h-1.5">
                                        <div 
                                          className="bg-primary h-1.5 rounded-full transition-all"
                                          style={{ width: `${task.progress}%` }}
                                        />
                                      </div>
                                      <p className="text-xs text-muted-foreground mt-1">
                                        {task.progress}% complete
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {tasks.length === 0 && (
                          <p className="ml-11 text-sm text-muted-foreground">
                            No active tasks
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="w-96 border-l border-border flex flex-col bg-card">
            {/* Chat header */}
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-2">
                <AtSign className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="font-semibold text-sm text-foreground">Team Chat</h3>
                  <p className="text-xs text-muted-foreground">
                    Use @ to mention agents
                  </p>
                </div>
              </div>
            </div>

            {/* Messages area */}
            <ScrollArea className="flex-1 p-4" ref={chatScrollRef}>
              <div className="space-y-3">
                {chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex flex-col ${message.isFromCEO ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-lg px-3 py-2 ${
                        message.isFromCEO
                          ? 'bg-primary text-primary-foreground'
                          : message.senderId === 'system'
                          ? 'bg-muted/50 text-muted-foreground border border-border'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                    <span className="text-[10px] text-muted-foreground mt-1 px-1">
                      {message.sender} • {message.time}
                    </span>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Mention menu */}
            {showMentionMenu && (
              <div className="border-t border-border bg-card">
                <div className="p-2 max-h-48 overflow-auto">
                  {filteredEmployees.length > 0 ? (
                    filteredEmployees.map((emp) => (
                      <button
                        key={emp.id}
                        onClick={() => handleMentionSelect(emp)}
                        className="w-full flex items-center gap-2 p-2 rounded hover:bg-muted transition-colors"
                      >
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={emp.avatar} alt={emp.name} />
                          <AvatarFallback className="text-xs">
                            {emp.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div className="text-left">
                          <p className="text-sm font-medium">{emp.name}</p>
                          <p className="text-xs text-muted-foreground">{emp.role}</p>
                        </div>
                      </button>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground p-2">No agents found</p>
                  )}
                </div>
              </div>
            )}

            {/* Input area */}
            <div className="p-3 border-t border-border">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  placeholder="Type @ to mention an agent..."
                  className="flex-1 text-sm"
                />
                <Button size="icon" onClick={handleSendMessage} disabled={!inputValue.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
