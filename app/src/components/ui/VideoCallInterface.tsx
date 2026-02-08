import { useEffect, useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChatPanel } from '@/components/ui/ChatPanel';
import { useGameState } from '@/hooks/useGameState';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { agentsApi } from '@/lib/agents';
import { toast } from 'sonner';
import { 
  PhoneOff, 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Monitor, 
  MoreVertical,
  Users,
  ArrowLeft,
  Loader2,
  Radio
} from 'lucide-react';

interface VideoCallInterfaceProps {
  onBackToInterface: () => void;
}

export function VideoCallInterface({ onBackToInterface }: VideoCallInterfaceProps) {
  const { currentEmployee } = useGameState();
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isLoadingPrompt, setIsLoadingPrompt] = useState(true);
  const [systemPrompt, setSystemPrompt] = useState<string | null>(null);
  const [voiceStatus, setVoiceStatus] = useState('Initializing...');
  const [callStarted, setCallStarted] = useState(false); // Track if call has started

  // Fetch system prompt when component mounts
  useEffect(() => {
    const fetchSystemPrompt = async () => {
      if (!currentEmployee) return;
      
      setIsLoadingPrompt(true);
      try {
        console.log(`Fetching prompt builder for ${currentEmployee.agentType}...`);
        const response = await agentsApi.getPromptBuilder(currentEmployee.agentType);
        console.log('Prompt builder response:', response);
        console.log('System prompt fetched, length:', response.text.length);
        setSystemPrompt(response.text);
        toast.success('Voice chat initialized');
      } catch (error) {
        console.error('Failed to fetch system prompt:', error);
        toast.error('Failed to initialize voice chat');
        setSystemPrompt('You are a helpful assistant.'); // Fallback
      } finally {
        setIsLoadingPrompt(false);
      }
    };

    fetchSystemPrompt();
  }, [currentEmployee]);

  // Initialize voice chat ONLY after prompt is loaded AND call is started
  const voiceChat = useVoiceChat({
    agentType: currentEmployee?.agentType || 'team_lead',
    systemPrompt: systemPrompt || 'You are a helpful assistant.',
    onStatusChange: setVoiceStatus,
    enabled: !isLoadingPrompt && systemPrompt !== null && callStarted, // Only when ready AND started
  });

  // Only initialize voice chat after prompt is loaded and call started
  const isVoiceChatReady = !isLoadingPrompt && systemPrompt && voiceChat.isConnected && callStarted;

  // Handle escape key to go back
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        voiceChat.disconnect();
        onBackToInterface();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onBackToInterface, voiceChat]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      voiceChat.disconnect();
    };
  }, []);

  const handleEndCall = () => {
    voiceChat.disconnect();
    setCallStarted(false);
    toast.info('Call ended');
  };

  const handleStartCall = () => {
    setCallStarted(true);
    toast.success('Starting call...');
  };

  if (!currentEmployee) return null;

  // Show loading overlay while fetching system prompt or connecting
  if (isLoadingPrompt || voiceChat.isConnecting) {
    return (
      <div className="fixed inset-0 bg-background z-50 flex items-center justify-center animate-fade-in">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
          <div>
            <p className="text-lg font-semibold text-foreground">
              {isLoadingPrompt ? 'Initializing Voice Chat' : 'Connecting to Gemini Live'}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              {isLoadingPrompt 
                ? `Preparing conversation with ${currentEmployee.name}...`
                : 'Establishing voice connection...'
              }
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onBackToInterface}
            className="mt-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-background z-50 flex animate-fade-in">
      {/* Main video area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 bg-card border-b border-border flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={onBackToInterface}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            
            <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
              <Video className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h2 className="font-semibold text-sm text-foreground">
                {callStarted ? 'Live Call with' : 'Ready to call'} {currentEmployee.name}
              </h2>
              <p className="text-xs text-muted-foreground">
                {currentEmployee.department}
                {callStarted && isVoiceChatReady && (
                  <span className="ml-2 text-green-500">● Connected</span>
                )}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-muted-foreground">
              <Users className="h-4 w-4 mr-1" />
              2
            </Button>
            <Button variant="ghost" size="icon" className="text-muted-foreground">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Video content */}
        <div className="flex-1 bg-muted/30 p-4 flex items-center justify-center relative">
          {/* Main video - Employee */}
          <Card className="w-full max-w-3xl aspect-video bg-gradient-to-br from-muted to-muted/50 relative overflow-hidden">
            {/* Office background simulation */}
            <div className="absolute inset-0 bg-gradient-to-b from-amber-50/20 to-amber-100/30" />
            <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-amber-200/20 to-transparent" />
            
            {/* Bookshelf background element */}
            <div className="absolute top-4 right-4 w-16 h-24 bg-amber-800/20 rounded" />
            <div className="absolute top-4 right-6 w-3 h-5 bg-red-400/40 rounded-sm" />
            <div className="absolute top-10 right-8 w-4 h-6 bg-blue-400/40 rounded-sm" />
            
            {/* Plant background element */}
            <div className="absolute bottom-0 left-4 w-8 h-16">
              <div className="absolute bottom-0 w-6 h-6 bg-amber-700/30 rounded-t" />
              <div className="absolute bottom-4 left-1 w-4 h-8 bg-green-600/40 rounded-full" />
            </div>
            
            {/* Avatar centered */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center">
                <div className="relative">
                  <Avatar className="w-32 h-32 border-4 border-background shadow-xl">
                    <AvatarImage src={currentEmployee.avatar} alt={currentEmployee.name} />
                    <AvatarFallback className="text-3xl">
                      {currentEmployee.name[0]}
                    </AvatarFallback>
                  </Avatar>
                  {/* Voice activity indicator */}
                  {voiceChat.isRecording && (
                    <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
                      <Radio className="h-5 w-5 text-white" />
                    </div>
                  )}
                  {voiceStatus === 'Speaking...' && (
                    <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                      <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                    </div>
                  )}
                </div>
                <div className="mt-4 text-center">
                  <h3 className="font-semibold text-lg text-foreground">
                    {currentEmployee.name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {currentEmployee.role}
                  </p>
                  {/* Voice status */}
                  <p className="text-xs text-muted-foreground mt-2">
                    {voiceStatus}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Name tag */}
            <div className="absolute bottom-4 left-4 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded">
              <p className="text-sm font-medium text-foreground">
                {currentEmployee.name}
              </p>
            </div>
          </Card>
          
          {/* Self view - small pip */}
          <div className="absolute bottom-8 right-8 w-40 aspect-video bg-card rounded-lg border border-border shadow-lg overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-muted to-muted/80 flex items-center justify-center">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-lg font-semibold text-primary">You</span>
              </div>
            </div>
            {!isVideoOn && (
              <div className="absolute inset-0 bg-muted flex items-center justify-center">
                <VideoOff className="h-6 w-6 text-muted-foreground" />
              </div>
            )}
          </div>
        </div>

        {/* Controls bar */}
        <div className="h-20 bg-card border-t border-border flex items-center justify-center gap-3">
          {!callStarted ? (
            // Before call starts - show Start Call button
            <>
              <Button
                variant="default"
                size="lg"
                className="rounded-full px-8 h-12 bg-green-600 hover:bg-green-700"
                onClick={handleStartCall}
                disabled={!systemPrompt || isLoadingPrompt}
              >
                <Radio className="h-5 w-5 mr-2" />
                Start Call
              </Button>
              
              {systemPrompt && !isLoadingPrompt && (
                <div className="ml-4 flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-muted-foreground">Ready to start</span>
                </div>
              )}
              
              {(!systemPrompt || isLoadingPrompt) && (
                <div className="ml-4 flex items-center gap-2 text-xs">
                  <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                  <span className="text-muted-foreground">Preparing...</span>
                </div>
              )}
            </>
          ) : (
            // During call - show call controls
            <>
              <Button
                variant={voiceChat.isRecording ? "destructive" : "secondary"}
                size="lg"
                className="rounded-full w-12 h-12 relative"
                onClick={voiceChat.toggleRecording}
                disabled={!isVoiceChatReady}
              >
                {voiceChat.isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                {voiceChat.isRecording && (
                  <span className="absolute inset-0 rounded-full border-2 border-red-500 animate-ping" />
                )}
              </Button>
              
              <Button
                variant={!isVideoOn ? "destructive" : "secondary"}
                size="lg"
                className="rounded-full w-12 h-12"
                onClick={() => setIsVideoOn(!isVideoOn)}
                disabled={!isVoiceChatReady}
              >
                {isVideoOn ? <Video className="h-5 w-5" /> : <VideoOff className="h-5 w-5" />}
              </Button>
              
              <Button
                variant="secondary"
                size="lg"
                className="rounded-full w-12 h-12"
                disabled={!isVoiceChatReady}
              >
                <Monitor className="h-5 w-5" />
              </Button>
              
              <Button
                variant="destructive"
                size="lg"
                className="rounded-full px-6 h-12"
                onClick={handleEndCall}
              >
                <PhoneOff className="h-5 w-5 mr-2" />
                End Call
              </Button>
              
              {isVoiceChatReady && (
                <div className="ml-4 flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-muted-foreground">
                    {voiceChat.isRecording ? 'Recording' : 'Voice Ready'}
                  </span>
                </div>
              )}
              
              {!isVoiceChatReady && callStarted && (
                <div className="ml-4 flex items-center gap-2 text-xs">
                  <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                  <span className="text-muted-foreground">Connecting...</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Chat sidebar */}
      <div className="w-80 hidden lg:block">
        <ChatPanel />
      </div>
    </div>
  );
}
