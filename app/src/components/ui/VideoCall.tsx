import { useState } from 'react';
import { useGameState } from '@/hooks/useGameState';
import { EmployeeInterface } from './EmployeeInterface';
import { VideoCallInterface } from './VideoCallInterface';

export function VideoCall() {
  const { mode, videoCallMode, setVideoCallMode } = useGameState();

  if (mode !== 'video-call') return null;

  if (videoCallMode === 'live-call') {
    return <VideoCallInterface onBackToInterface={() => setVideoCallMode('interface')} />;
  }

  return <EmployeeInterface />;
}
