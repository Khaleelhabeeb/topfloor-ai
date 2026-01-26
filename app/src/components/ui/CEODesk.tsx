import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useGameState } from '@/hooks/useGameState';
import { ceoFolders, CEOFolder } from '@/data/employees';
import { 
  X, 
  ArrowLeft, 
  FolderOpen,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

function FolderButton({ folder, onClick }: { folder: CEOFolder; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="group flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-card hover:bg-accent hover:border-primary/50 transition-all duration-200 hover:scale-105"
    >
      <span className="text-4xl group-hover:scale-110 transition-transform">
        {folder.icon}
      </span>
      <span className="text-sm font-medium text-foreground text-center">
        {folder.name}
      </span>
    </button>
  );
}

function FolderContent({ folder, onClose }: { folder: CEOFolder; onClose: () => void }) {
  const isConfidential = folder.isConfidential;

  return (
    <Card className="max-w-2xl w-full mx-auto animate-scale-in">
      <CardHeader className="relative">
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-4 right-4"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-3">
          <span className="text-3xl">{folder.icon}</span>
          <div>
            <CardTitle className={isConfidential ? 'text-destructive' : ''}>
              {folder.content.title}
            </CardTitle>
            <CardDescription>{folder.content.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isConfidential ? (
          <div className="flex flex-col items-center py-8 text-center">
            <AlertTriangle className="h-16 w-16 text-destructive mb-4" />
            <h3 className="text-lg font-semibold text-destructive mb-2">
              Access Denied
            </h3>
            <p className="text-muted-foreground max-w-sm">
              This folder contains confidential information. 
              You do not have the required clearance level.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {folder.content.items?.map((item, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
              >
                <CheckCircle className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                <span className="text-sm text-foreground">{item}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function CEODesk() {
  const { mode, currentFolder, openFolder, closeFolder, exitCEODesk } = useGameState();

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (currentFolder) {
          closeFolder();
        } else {
          exitCEODesk();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentFolder, closeFolder, exitCEODesk]);

  if (mode !== 'ceo-desk' && mode !== 'folder-view') return null;

  return (
    <div className="fixed inset-0 bg-background z-50 flex flex-col animate-fade-in">
      {/* Header */}
      <div className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => currentFolder ? closeFolder() : exitCEODesk()}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            {currentFolder ? 'Back to Desk' : 'Stand Up'}
          </Button>
          
          <div className="h-6 w-px bg-border" />
          
          <div className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5 text-primary" />
            <h1 className="font-semibold text-foreground">
              {currentFolder ? currentFolder.name : "CEO's Desk"}
            </h1>
          </div>
        </div>
        
        <p className="text-sm text-muted-foreground">
          Press <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Esc</kbd> to go back
        </p>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        <div className="p-8">
          {mode === 'folder-view' && currentFolder ? (
            <FolderContent folder={currentFolder} onClose={closeFolder} />
          ) : (
            <div className="max-w-4xl mx-auto">
              {/* Desk visualization */}
              <div className="mb-8 p-6 bg-gradient-to-b from-amber-900/20 to-amber-800/30 rounded-xl border border-amber-800/20">
                <div className="text-center mb-6">
                  <h2 className="text-xl font-semibold text-foreground mb-1">
                    Executive Desk
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Click on a folder to view its contents
                  </p>
                </div>
                
                {/* Folders grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                  {ceoFolders.map((folder) => (
                    <FolderButton
                      key={folder.id}
                      folder={folder}
                      onClick={() => openFolder(folder)}
                    />
                  ))}
                </div>
              </div>
              
              {/* Desk items decoration */}
              <div className="flex justify-center gap-8 text-muted-foreground">
                <div className="flex flex-col items-center gap-1">
                  <span className="text-2xl">🖊️</span>
                  <span className="text-xs">Pen Holder</span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <span className="text-2xl">📎</span>
                  <span className="text-xs">Paper Clips</span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <span className="text-2xl">☕</span>
                  <span className="text-xs">Coffee</span>
                </div>
                <div className="flex flex-col items-center gap-1">
                  <span className="text-2xl">🖼️</span>
                  <span className="text-xs">Photo Frame</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
