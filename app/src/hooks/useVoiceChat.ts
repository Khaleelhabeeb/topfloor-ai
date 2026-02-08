import { useRef, useState, useCallback, useEffect } from 'react';
import { GoogleGenAI, LiveServerMessage, Modality, Session } from '@google/genai';
import { createBlob, decode, decodeAudioData } from '@/lib/voice-utils';
import { AgentType } from '@/lib/agents';

// Voice mapping for each agent
const VOICE_MAP: Record<AgentType, string> = {
  team_lead: 'Puck',      // Alex
  finance: 'Charon',      // Peter
  data_analyst: 'Fenrir', // James
  researcher: 'Leda',     // Sarah
};

interface UseVoiceChatProps {
  agentType: AgentType;
  systemPrompt: string;
  onStatusChange?: (status: string) => void;
  enabled?: boolean; // Only initialize when true
}

export function useVoiceChat({ agentType, systemPrompt, onStatusChange, enabled = true }: UseVoiceChatProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('Ready');
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  const sessionPromiseRef = useRef<Promise<Session> | null>(null);
  const audioContextRef = useRef<{
    input: AudioContext;
    output: AudioContext;
    inputNode: GainNode;
    outputNode: GainNode;
  } | null>(null);
  const nextStartTimeRef = useRef(0);
  const sourcesRef = useRef<Set<AudioBufferSourceNode>>(new Set());
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  // Initialize audio contexts
  useEffect(() => {
    const AudioContextClass = (window.AudioContext || (window as any).webkitAudioContext);
    const inputCtx = new AudioContextClass({ sampleRate: 16000 });
    const outputCtx = new AudioContextClass({ sampleRate: 24000 });
    
    const inputNode = inputCtx.createGain();
    const outputNode = outputCtx.createGain();
    outputNode.connect(outputCtx.destination);
    
    audioContextRef.current = {
      input: inputCtx,
      output: outputCtx,
      inputNode,
      outputNode,
    };

    return () => {
      inputCtx.close();
      outputCtx.close();
    };
  }, []);

  const updateStatus = useCallback((newStatus: string) => {
    setStatus(newStatus);
    onStatusChange?.(newStatus);
  }, [onStatusChange]);

  const initSession = useCallback(() => {
    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
    if (!apiKey) {
      updateStatus('Error: API key not configured');
      return;
    }

    setIsConnecting(true);
    updateStatus('Connecting...');

    const voice = VOICE_MAP[agentType];
    console.log('Initializing voice chat with:', {
      agentType,
      voice,
      systemPromptLength: systemPrompt.length,
      systemPromptPreview: systemPrompt.substring(0, 100) + '...',
    });

    const ai = new GoogleGenAI({ apiKey });

    const promise = ai.live.connect({
      model: 'gemini-2.5-flash-native-audio-preview-12-2025',
      config: {
        systemInstruction: {
          parts: [
            {
              text: systemPrompt,
            }
          ],
        },
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: { 
            prebuiltVoiceConfig: { 
              voiceName: voice as any 
            } 
          },
        },
      },
      callbacks: {
        onopen: () => {
          updateStatus('Connected');
          setIsConnecting(false);
          setIsConnected(true);
          console.log('Voice chat connected');
        },
        onmessage: async (message: LiveServerMessage) => {
          const audioData = message.serverContent?.modelTurn?.parts[0]?.inlineData?.data;
          
          if (audioData && audioContextRef.current) {
            const { output, outputNode } = audioContextRef.current;
            nextStartTimeRef.current = Math.max(nextStartTimeRef.current, output.currentTime);
            
            const buffer = await decodeAudioData(decode(audioData), output, 24000, 1);
            const source = output.createBufferSource();
            source.buffer = buffer;
            source.connect(outputNode);
            source.onended = () => sourcesRef.current.delete(source);
            source.start(nextStartTimeRef.current);
            nextStartTimeRef.current += buffer.duration;
            sourcesRef.current.add(source);
            
            updateStatus('Speaking...');
          }
          
          if (message.serverContent?.interrupted) {
            sourcesRef.current.forEach(s => s.stop());
            sourcesRef.current.clear();
            nextStartTimeRef.current = 0;
          }
          
          if (message.serverContent?.turnComplete) {
            updateStatus('Listening...');
          }
        },
        onerror: (e) => {
          console.error('Voice chat error:', e);
          updateStatus(`Error: ${e.message}`);
          setIsConnected(false);
        },
        onclose: () => {
          updateStatus('Disconnected');
          setIsConnected(false);
          console.log('Voice chat disconnected');
        },
      },
    });

    sessionPromiseRef.current = promise;
  }, [agentType, systemPrompt, updateStatus]);

  const toggleRecording = useCallback(async () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      updateStatus('Ready');
      processorRef.current?.disconnect();
      streamRef.current?.getTracks().forEach(t => t.stop());
    } else {
      // Start recording
      try {
        if (!audioContextRef.current) return;
        
        const { input } = audioContextRef.current;
        await input.resume();
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        
        const source = input.createMediaStreamSource(stream);
        const processor = input.createScriptProcessor(4096, 1, 1);
        
        processor.onaudioprocess = (e) => {
          const pcmData = e.inputBuffer.getChannelData(0);
          sessionPromiseRef.current?.then(session => {
            session.sendRealtimeInput({ media: createBlob(pcmData) });
          });
        };
        
        source.connect(processor);
        processor.connect(input.destination);
        processorRef.current = processor;
        
        setIsRecording(true);
        updateStatus('Listening...');
      } catch (err) {
        console.error('Microphone access error:', err);
        updateStatus('Mic access denied');
      }
    }
  }, [isRecording, updateStatus]);

  const disconnect = useCallback(() => {
    // Stop recording if active
    if (isRecording) {
      processorRef.current?.disconnect();
      streamRef.current?.getTracks().forEach(t => t.stop());
      setIsRecording(false);
    }
    
    // Close session
    sessionPromiseRef.current?.then(s => s.close());
    sessionPromiseRef.current = null;
    
    // Stop all audio sources
    sourcesRef.current.forEach(s => s.stop());
    sourcesRef.current.clear();
    nextStartTimeRef.current = 0;
    
    setIsConnected(false);
    updateStatus('Disconnected');
  }, [isRecording, updateStatus]);

  // Initialize session when component mounts and enabled is true
  useEffect(() => {
    if (!enabled) {
      console.log('Voice chat initialization skipped - not enabled yet');
      return;
    }

    console.log('Voice chat enabled, initializing session...');
    initSession();
    
    return () => {
      disconnect();
    };
  }, [enabled]); // Only re-initialize if enabled changes

  return {
    isRecording,
    status,
    isConnecting,
    isConnected,
    toggleRecording,
    disconnect,
  };
}
