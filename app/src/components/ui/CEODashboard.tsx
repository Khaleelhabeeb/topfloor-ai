import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useGameState } from '@/hooks/useGameState';
import { useCEO } from '@/hooks/useCEO';
import { employees } from '@/data/employees';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
  Activity,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: string;
  senderId: string;
  text: string;
  time: string;
  mentionedAgent?: string;
  isFromCEO?: boolean;
}

export function CEODashboard() {
  const { mode, exitCEODesk } = useGameState();
  const { 
    dashboard, 
    isLoadingDashboard, 
    fetchDashboard,
    activities,
    isLoadingActivity,
    fetchActivity,
    chatMessages: apiChatMessages,
    sendChatMessage,
    isSendingMessage,
  } = useCEO();
  
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [expandedAgents, setExpandedAgents] = useState<Record<string, boolean>>({});
  const [localChatMessages, setLocalChatMessages] = useState<ChatMessage[]>([
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

  // Fetch dashboard data on mount
  useEffect(() => {
    if (mode === 'ceo-desk') {
      fetchDashboard();
      fetchActivity();
    }
  }, [mode, fetchDashboard, fetchActivity]);

  // Sync API chat messages with local state
  useEffect(() => {
    if (apiChatMessages.length > 0) {
      const newMessages: ChatMessage[] = [];
      
      apiChatMessages.forEach((apiMsg) => {
        // Add CEO message
        newMessages.push({
          id: apiMsg.message_id,
          sender: 'You (CEO)',
          senderId: 'ceo',
          text: apiMsg.message,
          time: new Date(apiMsg.timestamp).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          }),
          isFromCEO: true,
        });

        // Add agent responses
        if (apiMsg.agent_responses) {
          apiMsg.agent_responses.forEach((response) => {
            const employee = employees.find(e => e.agentType === response.agent_id);
            newMessages.push({
              id: `${apiMsg.message_id}_${response.agent_id}`,
              sender: employee?.name || response.agent_name,
              senderId: response.agent_id,
              text: response.response,
              time: new Date(response.timestamp).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
              }),
              isFromCEO: false,
            });
          });
        }
      });

      setLocalChatMessages((prev) => {
        // Keep system message and remove temp messages
        const systemMsg = prev.find(m => m.senderId === 'system');
        const nonTempMessages = prev.filter(m => !m.id.startsWith('temp_'));
        
        // Merge with new messages, avoiding duplicates
        const existingIds = new Set(nonTempMessages.map(m => m.id));
        const uniqueNewMessages = newMessages.filter(m => !existingIds.has(m.id));
        
        return systemMsg 
          ? [systemMsg, ...nonTempMessages, ...uniqueNewMessages] 
          : [...nonTempMessages, ...uniqueNewMessages];
      });
    }
  }, [apiChatMessages]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [localChatMessages]);

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

  // Show loading state
  if (isLoadingDashboard && !dashboard) {
    return (
      <div className="fixed inset-0 bg-background z-50 flex items-center justify-center animate-fade-in">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-sm text-muted-foreground">
            Loading CEO Dashboard...
          </p>
        </div>
      </div>
    );
  }

  const stats = dashboard?.overview || {
    totalTasks: 0,
    completed: 0,
    inProgress: 0,
    pending: 0,
    avgProgress: 0,
  };

  const tasksByEmployee = dashboard?.tasks_by_agent || [];
  const recentActivity = dashboard?.recent_activity || [];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'pending':
      case 'queued':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'outline'> = {
      completed: 'default',
      in_progress: 'secondary',
      pending: 'outline',
      queued: 'outline',
    };
    
    return (
      <Badge variant={variants[status] || 'outline'} className="text-xs">
        {status.replace('_', ' ')}
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
    const newValue = inputValue.substring(0, lastAtIndex) + `@${employee.role} `;
    setInputValue(newValue);
    setShowMentionMenu(false);
    inputRef.current?.focus();
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSendingMessage) return;

    const messageText = inputValue;
    
    // Clear input immediately
    setInputValue('');

    // Check if message mentions someone
    const mentionMatch = messageText.match(/@(\w+)/g);
    const mentionedAgents: string[] = [];
    
    if (mentionMatch) {
      mentionMatch.forEach((mention) => {
        const name = mention.substring(1);
        const employee = employees.find(e => 
          e.name.toLowerCase() === name.toLowerCase() ||
          e.role.toLowerCase() === name.toLowerCase()
        );
        if (employee) {
          mentionedAgents.push(employee.agentType);
        }
      });
    }

    // Add optimistic CEO message to chat
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });

    const optimisticMessage: ChatMessage = {
      id: `temp_${Date.now()}`,
      sender: 'You (CEO)',
      senderId: 'ceo',
      text: messageText,
      time: timeString,
      isFromCEO: true,
    };

    setLocalChatMessages(prev => [...prev, optimisticMessage]);

    // Send message via API
    await sendChatMessage(messageText, mentionedAgents);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !showMentionMenu) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const filteredEmployees = employees.filter(emp => 
    emp.name.toLowerCase().includes(mentionFilter) ||
    emp.role.toLowerCase().includes(mentionFilter)
  );

  const toggleAgentExpanded = (agentId: string) => {
    setExpandedAgents(prev => ({
      ...prev,
      [agentId]: !prev[agentId]
    }));
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
                {isLoadingActivity ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  </div>
                ) : activities.length > 0 ? (
                  activities.map((item) => (
                    <div
                      key={item.id}
                      className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                    >
                      <p className="text-xs text-muted-foreground mb-1">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </p>
                      <p className="text-sm font-medium text-foreground">
                        {item.action}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {item.details}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No activity history yet
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
                          {stats.total_tasks || 0}
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
                          {stats.completed_tasks || 0}
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
                          {stats.in_progress_tasks || 0}
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
                          {stats.pending_tasks || 0}
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
                          {stats.average_progress || 0}%
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
                      {tasksByEmployee.length} Agents
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {tasksByEmployee.map((agentData) => {
                      const employee = employees.find(e => e.agentType === agentData.agent_id);
                      if (!employee) return null;

                      return (
                        <div key={agentData.agent_id} className="space-y-3">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={employee.avatar} alt={employee.name} />
                              <AvatarFallback>
                                {employee.name[0]}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <p className="font-medium text-sm text-foreground">
                                {employee.name}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {employee.role} • {agentData.task_count} tasks
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setInputValue(`@${employee.role} `)}
                            >
                              <AtSign className="h-3 w-3 mr-1" />
                              Message
                            </Button>
                          </div>
                          
                          {agentData.tasks.length > 0 && (
                            <div className="ml-11 space-y-2">
                              {agentData.tasks
                                .slice(0, expandedAgents[agentData.agent_id] ? undefined : 3)
                                .map((task) => (
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
                                              Due: {new Date(task.due_date).toLocaleDateString()}
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
                              
                              {agentData.tasks.length > 3 && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="w-full"
                                  onClick={() => toggleAgentExpanded(agentData.agent_id)}
                                >
                                  {expandedAgents[agentData.agent_id] ? (
                                    <>
                                      <ChevronUp className="h-4 w-4 mr-2" />
                                      Show Less
                                    </>
                                  ) : (
                                    <>
                                      <ChevronDown className="h-4 w-4 mr-2" />
                                      View More ({agentData.tasks.length - 3} more)
                                    </>
                                  )}
                                </Button>
                              )}
                            </div>
                          )}
                          
                          {agentData.tasks.length === 0 && (
                            <p className="ml-11 text-sm text-muted-foreground">
                              No active tasks
                            </p>
                          )}
                        </div>
                      );
                    })}
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
                {localChatMessages.map((message) => (
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
                      {message.isFromCEO || message.senderId === 'system' ? (
                        <p className="text-sm">{message.text}</p>
                      ) : (
                        <div className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:leading-relaxed prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.text}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                    <span className="text-[10px] text-muted-foreground mt-1 px-1">
                      {message.sender} • {message.time}
                    </span>
                  </div>
                ))}
                {isSendingMessage && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Sending message...</span>
                  </div>
                )}
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
                            {emp.name[0]}
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
                <Button size="icon" onClick={handleSendMessage} disabled={!inputValue.trim() || isSendingMessage}>
                  {isSendingMessage ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
