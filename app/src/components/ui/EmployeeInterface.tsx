import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ChatPanel } from '@/components/ui/ChatPanel';
import { CreateTaskDialog } from '@/components/ui/CreateTaskDialog';
import { TaskDetailsDialog } from '@/components/ui/TaskDetailsDialog';
import { useGameState } from '@/hooks/useGameState';
import { useAgents } from '@/hooks/useAgents';
import { tasksApi } from '@/lib/tasks';
import { toast } from 'sonner';
import { 
  Video, 
  Settings, 
  History, 
  X,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Plus,
  RefreshCw,
} from 'lucide-react';

export function EmployeeInterface() {
  const { currentEmployee, exitVideoCall, mode, setVideoCallMode } = useGameState();
  const { fetchAgentOffice, agentOffices } = useAgents();
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loadingTaskId, setLoadingTaskId] = useState<string | null>(null);
  const hasFetchedRef = useRef(false);

  // Fetch agent office data when component mounts - only once
  useEffect(() => {
    if (currentEmployee && !hasFetchedRef.current) {
      hasFetchedRef.current = true;
      setIsLoading(true);
      console.log(`Fetching ${currentEmployee.agentType} office data...`);
      fetchAgentOffice(currentEmployee.agentType)
        .then(() => {
          console.log(`${currentEmployee.agentType} office data loaded`);
        })
        .catch((error) => {
          console.error(`Failed to fetch ${currentEmployee.agentType} office:`, error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [currentEmployee, fetchAgentOffice]);

  // Check if data is loaded from the store
  useEffect(() => {
    if (currentEmployee && agentOffices[currentEmployee.agentType]) {
      console.log('Agent office data available in store:', agentOffices[currentEmployee.agentType]);
      setIsLoading(false);
    }
  }, [currentEmployee, agentOffices]);

  // Reset ref when component unmounts
  useEffect(() => {
    return () => {
      hasFetchedRef.current = false;
    };
  }, []);

  // Handle refresh
  const handleRefresh = async () => {
    if (!currentEmployee) return;
    
    setIsRefreshing(true);
    try {
      await fetchAgentOffice(currentEmployee.agentType);
      console.log('Office data refreshed');
    } catch (error) {
      console.error('Failed to refresh:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle task clicked - need to find numeric ID
  const handleTaskClick = async (taskStringId: string) => {
    if (!currentEmployee) return;
    
    setLoadingTaskId(taskStringId);
    try {
      console.log('Fetching task details for:', taskStringId);
      // Fetch agent tasks to get the full task object with numeric ID
      const response = await tasksApi.getAgentTasks(currentEmployee.agentType);
      console.log('Agent tasks response:', response);
      
      const task = response.tasks.find(t => t.task_id === taskStringId);
      console.log('Found task:', task);
      
      if (task) {
        setSelectedTaskId(task.id);
      } else {
        console.error('Task not found in response:', taskStringId);
        toast.error('Task not found');
      }
    } catch (error) {
      console.error('Failed to find task:', error);
      toast.error('Failed to load task');
    } finally {
      setLoadingTaskId(null);
    }
  };

  // Handle task created
  const handleTaskCreated = () => {
    handleRefresh();
  };

  // Handle task updated
  const handleTaskUpdated = () => {
    handleRefresh();
  };

  if (mode !== 'video-call' || !currentEmployee) return null;

  const agentOffice = agentOffices[currentEmployee.agentType];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'pending':
      case 'queued':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { variant: 'default' | 'secondary' | 'outline' | 'destructive'; label: string; className?: string }> = {
      completed: { variant: 'default', label: 'Completed', className: 'bg-green-500 hover:bg-green-600 text-white' },
      in_progress: { variant: 'secondary', label: 'In Progress' },
      pending: { variant: 'outline', label: 'Pending' },
      queued: { variant: 'outline', label: 'Queued' },
      failed: { variant: 'destructive', label: 'Failed' },
      cancelled: { variant: 'outline', label: 'Cancelled' },
    };
    
    const config = statusMap[status] || { variant: 'outline' as const, label: status };
    
    return (
      <Badge variant={config.variant} className={`text-xs ${config.className || ''}`}>
        {config.label}
      </Badge>
    );
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
      case 'critical':
        return 'border-l-red-500';
      case 'medium':
        return 'border-l-yellow-500';
      case 'low':
        return 'border-l-green-500';
      default:
        return 'border-l-gray-500';
    }
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-background z-50 flex items-center justify-center animate-fade-in">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-sm text-muted-foreground">
            Loading {currentEmployee.name}'s office...
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={exitVideoCall}
            className="mt-4"
          >
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  const recentTasks = agentOffice?.tasks.recent || [];
  const taskCounts = agentOffice?.tasks.counts || {
    completed: 0,
    in_progress: 0,
    pending: 0,
    queued: 0,
    failed: 0,
    cancelled: 0
  };
  const chatHistory = agentOffice?.chat_history.recent || [];
  const agentStatus = agentOffice?.status;

  // Debug logging
  console.log('Agent Office Data:', agentOffice);
  console.log('Recent Tasks:', recentTasks);
  console.log('Task Counts:', taskCounts);
  console.log('Agent Status:', agentStatus);

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
                  <h3 className="font-semibold text-foreground">Chat History</h3>
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
                {chatHistory.length > 0 ? (
                  chatHistory.map((item, index) => (
                    <div
                      key={index}
                      className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <p className="text-xs text-muted-foreground mb-1">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                      <p className="text-sm font-medium text-foreground">
                        {item.role === 'user' ? 'You' : currentEmployee.name}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {item.content}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No chat history yet
                  </p>
                )}
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
              <img 
                src={currentEmployee.avatar} 
                alt={currentEmployee.name}
                className="w-10 h-10 rounded-full object-cover border-2 border-primary/20"
              />
              <div>
                <h2 className="font-semibold text-foreground">
                  {currentEmployee.name}
                </h2>
                <p className="text-xs text-muted-foreground">
                  {currentEmployee.role}
                </p>
              </div>
              {agentStatus && (
                <div className="flex items-center gap-2 ml-2">
                  <div className={`w-2 h-2 rounded-full ${
                    agentStatus.status === 'available' ? 'bg-green-500' :
                    agentStatus.status === 'busy' ? 'bg-yellow-500' :
                    'bg-gray-500'
                  }`} />
                  <span className="text-xs text-muted-foreground capitalize">
                    {agentStatus.status}
                  </span>
                </div>
              )}
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
                    <CardTitle>Recent Tasks</CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">
                        {taskCounts.in_progress + taskCounts.pending + taskCounts.queued} Active
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                      >
                        <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => setShowCreateTask(true)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        New Task
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {recentTasks.length > 0 ? (
                    <div className="space-y-3">
                      {recentTasks.map((task) => (
                        <div
                          key={task.task_id}
                          className={`p-4 rounded-lg border-l-4 ${getPriorityColor(task.priority)} bg-muted/30 hover:bg-muted/50 transition-colors cursor-pointer relative`}
                          onClick={() => handleTaskClick(task.task_id)}
                        >
                          {loadingTaskId === task.task_id && (
                            <div className="absolute inset-0 bg-background/50 rounded-lg flex items-center justify-center">
                              <Loader2 className="h-5 w-5 animate-spin text-primary" />
                            </div>
                          )}
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
                                    Created: {new Date(task.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                            </div>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="shrink-0"
                              disabled={loadingTaskId === task.task_id}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleTaskClick(task.task_id);
                              }}
                            >
                              {loadingTaskId === task.task_id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                'View'
                              )}
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-sm text-muted-foreground mb-4">
                        No recent tasks
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowCreateTask(true)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Create First Task
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-500">
                        {taskCounts.completed}
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
                        {taskCounts.in_progress}
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
                        {taskCounts.pending + taskCounts.queued}
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

      {/* Task Creation Dialog */}
      {currentEmployee && (
        <CreateTaskDialog
          open={showCreateTask}
          onOpenChange={setShowCreateTask}
          agentType={currentEmployee.agentType}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {/* Task Details Dialog */}
      <TaskDetailsDialog
        open={selectedTaskId !== null}
        onOpenChange={(open) => !open && setSelectedTaskId(null)}
        taskId={selectedTaskId}
        onTaskUpdated={handleTaskUpdated}
      />
    </div>
  );
}
