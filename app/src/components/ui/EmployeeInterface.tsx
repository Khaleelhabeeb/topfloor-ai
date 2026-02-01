import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ChatPanel } from '@/components/ui/ChatPanel';
import { useGameState } from '@/hooks/useGameState';
import { 
  Video, 
  Settings, 
  History, 
  X,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  status: 'completed' | 'in-progress' | 'pending';
  priority: 'high' | 'medium' | 'low';
  dueDate: string;
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Review Q2 Marketing Campaign',
    status: 'in-progress',
    priority: 'high',
    dueDate: '2024-02-15'
  },
  {
    id: '2',
    title: 'Update Brand Guidelines',
    status: 'completed',
    priority: 'medium',
    dueDate: '2024-02-10'
  },
  {
    id: '3',
    title: 'Prepare Presentation Slides',
    status: 'pending',
    priority: 'high',
    dueDate: '2024-02-20'
  },
  {
    id: '4',
    title: 'Team Performance Review',
    status: 'in-progress',
    priority: 'medium',
    dueDate: '2024-02-18'
  },
  {
    id: '5',
    title: 'Budget Planning Meeting',
    status: 'pending',
    priority: 'low',
    dueDate: '2024-02-25'
  }
];

const mockHistory = [
  { date: '2024-02-01', action: 'Started video call', duration: '45 min' },
  { date: '2024-01-28', action: 'Reviewed project proposal', duration: '30 min' },
  { date: '2024-01-25', action: 'Discussed marketing strategy', duration: '1 hr' },
  { date: '2024-01-22', action: 'Team sync meeting', duration: '25 min' },
  { date: '2024-01-20', action: 'Quarterly review', duration: '50 min' },
];

export function EmployeeInterface() {
  const { currentEmployee, exitVideoCall, mode, setVideoCallMode } = useGameState();
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  if (mode !== 'video-call' || !currentEmployee) return null;

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

  return (
    <div className="fixed inset-0 bg-background z-50 flex animate-fade-in">
      {/* History Sidebar - Toggleable */}
      <div 
        className={`bg-card border-r border-border transition-all duration-300 ${
          showHistory ? 'w-64' : 'w-0'
        } overflow-hidden`}
      >
        {showHistory && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">History</h3>
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
                      Duration: {item.duration}
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
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                <span className="text-lg font-semibold text-primary">
                  {currentEmployee.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div>
                <h2 className="font-semibold text-foreground">
                  {currentEmployee.name}
                </h2>
                <p className="text-xs text-muted-foreground">
                  {currentEmployee.role} • {currentEmployee.department}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="default"
              size="sm"
              className="gap-2"
              onClick={() => setVideoCallMode('live-call')}
            >
              <Video className="h-4 w-4" />
              Go Live
            </Button>
            
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
              onClick={exitVideoCall}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Tasks Section */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Settings Panel */}
              {showSettings && (
                <Card className="animate-scale-in">
                  <CardHeader>
                    <CardTitle className="text-lg">Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Notifications</p>
                        <p className="text-xs text-muted-foreground">
                          Receive updates about task changes
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Configure
                      </Button>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Auto-save</p>
                        <p className="text-xs text-muted-foreground">
                          Automatically save conversation history
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Enable
                      </Button>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">Privacy</p>
                        <p className="text-xs text-muted-foreground">
                          Manage data sharing preferences
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Manage
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Active Tasks */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Active Tasks</CardTitle>
                    <Badge variant="secondary">
                      {mockTasks.filter(t => t.status !== 'completed').length} Active
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockTasks.map((task) => (
                      <div
                        key={task.id}
                        className={`p-4 rounded-lg border-l-4 ${getPriorityColor(task.priority)} bg-muted/30 hover:bg-muted/50 transition-colors`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-start gap-3 flex-1">
                            {getStatusIcon(task.status)}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-sm text-foreground mb-1">
                                {task.title}
                              </h4>
                              <div className="flex items-center gap-2 flex-wrap">
                                {getStatusBadge(task.status)}
                                <Badge variant="outline" className="text-xs">
                                  {task.priority} priority
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  Due: {task.dueDate}
                                </span>
                              </div>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm" className="shrink-0">
                            View
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-500">
                        {mockTasks.filter(t => t.status === 'completed').length}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Completed
                      </p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-500">
                        {mockTasks.filter(t => t.status === 'in-progress').length}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        In Progress
                      </p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-orange-500">
                        {mockTasks.filter(t => t.status === 'pending').length}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Pending
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="w-80 border-l border-border">
            <ChatPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
