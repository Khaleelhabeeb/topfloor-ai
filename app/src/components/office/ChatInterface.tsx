import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { TeamMember } from './types';

interface ChatInterfaceProps {
  member: TeamMember;
  onClose: () => void;
}

export function ChatInterface({ member, onClose }: ChatInterfaceProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <Card className="w-full max-w-2xl mx-4 bg-card/95 border-border shadow-2xl">
        <CardHeader className="relative border-b border-border">
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute right-4 top-4"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center gap-4">
            <div className="text-5xl">{member.avatar}</div>
            <div>
              <CardTitle className="text-2xl">{member.name}</CardTitle>
              <CardDescription className="text-lg">{member.role}</CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Bio Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              About
            </h3>
            <p className="text-foreground leading-relaxed">{member.bio}</p>
          </div>

          {/* Projects Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Current Projects
            </h3>
            <ul className="space-y-2">
              {member.projects.map((project, index) => (
                <li 
                  key={index} 
                  className="flex items-start gap-2 text-foreground"
                >
                  <span className="text-primary mt-1">•</span>
                  <span>{project}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Contact
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-muted rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Email</p>
                <p className="text-sm text-foreground font-medium">{member.contact.email}</p>
              </div>
              <div className="bg-muted rounded-lg p-3">
                <p className="text-xs text-muted-foreground">Slack</p>
                <p className="text-sm text-foreground font-medium">{member.contact.slack}</p>
              </div>
            </div>
          </div>

          {/* Exit hint */}
          <div className="text-center pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Press <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">ESC</kbd> or click X to return to office
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
