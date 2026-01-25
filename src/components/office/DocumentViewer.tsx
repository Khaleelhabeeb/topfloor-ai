import { useState } from 'react';
import { X, ChevronLeft, ChevronRight, FileText, BarChart2, Image } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Folder, Document } from './types';

interface DocumentViewerProps {
  folder: Folder;
  onClose: () => void;
}

export function DocumentViewer({ folder, onClose }: DocumentViewerProps) {
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const currentDoc = folder.documents[currentDocIndex];

  const goToPrevious = () => {
    setCurrentDocIndex((prev) => 
      prev > 0 ? prev - 1 : folder.documents.length - 1
    );
  };

  const goToNext = () => {
    setCurrentDocIndex((prev) => 
      prev < folder.documents.length - 1 ? prev + 1 : 0
    );
  };

  const getDocIcon = (type: Document['type']) => {
    switch (type) {
      case 'chart':
        return <BarChart2 className="h-5 w-5" />;
      case 'image':
        return <Image className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <Card className="w-full max-w-3xl mx-4 bg-card/95 border-border shadow-2xl">
        <CardHeader className="relative border-b border-border">
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute right-4 top-4"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center gap-3">
            <div 
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: folder.color }}
            >
              {getDocIcon(currentDoc.type)}
            </div>
            <div>
              <CardTitle className="text-xl">{folder.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                Document {currentDocIndex + 1} of {folder.documents.length}
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          {/* Document Title */}
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-foreground">{currentDoc.title}</h2>
            {currentDoc.description && (
              <p className="text-muted-foreground mt-1">{currentDoc.description}</p>
            )}
          </div>

          {/* Document Content */}
          <div className="bg-muted rounded-lg p-6 min-h-[300px] font-mono text-sm whitespace-pre-wrap text-foreground">
            {currentDoc.content}
          </div>

          {/* Navigation */}
          {folder.documents.length > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={goToPrevious}
                className="flex items-center gap-2"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>

              <div className="flex gap-2">
                {folder.documents.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentDocIndex(index)}
                    className={`w-2.5 h-2.5 rounded-full transition-colors ${
                      index === currentDocIndex 
                        ? 'bg-primary' 
                        : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                    }`}
                    aria-label={`Go to document ${index + 1}`}
                  />
                ))}
              </div>

              <Button 
                variant="outline" 
                onClick={goToNext}
                className="flex items-center gap-2"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Exit hint */}
          <div className="text-center mt-4">
            <p className="text-sm text-muted-foreground">
              Press <kbd className="px-2 py-1 bg-background rounded text-xs font-mono">ESC</kbd> to close
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
