import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useTasks } from '@/hooks/useTasks';
import { AgentType } from '@/lib/agents';
import { TaskPriority } from '@/lib/tasks';
import { toast } from 'sonner';
import { Loader2, Upload, X, FileText, File } from 'lucide-react';

interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agentType: AgentType;
  onTaskCreated?: () => void;
}

export function CreateTaskDialog({
  open,
  onOpenChange,
  agentType,
  onTaskCreated,
}: CreateTaskDialogProps) {
  const { createTask, isLoading } = useTasks();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_CHARS = 5000;

  // Calculate total character count
  const totalChars = description.length + fileContent.length;
  const remainingChars = MAX_CHARS - totalChars;

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a PDF or TXT file');
      return;
    }

    // Check file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setIsProcessingFile(true);
    setUploadedFile(file);

    try {
      let content = '';

      if (file.type === 'text/plain') {
        // Read text file
        content = await file.text();
      } else if (file.type === 'application/pdf') {
        // Extract text from PDF using pdfjs-dist
        toast.info('Extracting text from PDF...');
        
        // Import PDF.js dynamically
        const pdfjsLib = await import('pdfjs-dist');
        
        // Use local worker from node_modules
        const pdfjsWorker = await import('pdfjs-dist/build/pdf.worker.mjs?url');
        pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker.default;
        
        // Read file as array buffer
        const arrayBuffer = await file.arrayBuffer();
        
        // Load PDF document
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        
        // Extract text from all pages
        let fullText = '';
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const textContent = await page.getTextContent();
          const pageText = textContent.items
            .map((item: any) => item.str)
            .join(' ');
          fullText += pageText + '\n\n';
        }
        
        content = fullText.trim();
      }

      // Trim content if needed to fit within limit
      const availableSpace = MAX_CHARS - description.length;
      if (content.length > availableSpace) {
        content = content.substring(0, availableSpace);
        toast.warning(`File content truncated to fit ${MAX_CHARS} character limit`);
      }

      setFileContent(content);
      toast.success(`File uploaded successfully - ${content.length} characters extracted`);
    } catch (error) {
      console.error('Error processing file:', error);
      toast.error('Failed to process file. Please try again.');
      setUploadedFile(null);
      setFileContent('');
    } finally {
      setIsProcessingFile(false);
    }
  };

  // Remove uploaded file
  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFileContent('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle description change with character limit
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newDescription = e.target.value;
    const newTotal = newDescription.length + fileContent.length;
    
    if (newTotal <= MAX_CHARS) {
      setDescription(newDescription);
    } else {
      toast.error(`Total content cannot exceed ${MAX_CHARS} characters`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Please enter a task title');
      return;
    }

    if (!description.trim() && !fileContent.trim()) {
      toast.error('Please provide a description or upload a file');
      return;
    }

    // Combine description and file content
    let finalDescription = description.trim();
    if (fileContent.trim()) {
      if (finalDescription) {
        finalDescription += '\n\n--- Uploaded File Content ---\n\n';
      }
      finalDescription += fileContent.trim();
    }

    // Final check for character limit
    if (finalDescription.length > MAX_CHARS) {
      toast.error(`Total content exceeds ${MAX_CHARS} characters`);
      return;
    }

    try {
      await createTask({
        agent_type: agentType,
        title: title.trim(),
        description: finalDescription,
        priority,
        task_type: 'background',
      });

      toast.success('Task created successfully!');
      
      // Reset form
      setTitle('');
      setDescription('');
      setPriority('medium');
      handleRemoveFile();
      
      // Close dialog
      onOpenChange(false);
      
      // Callback
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (error) {
      console.error('Failed to create task:', error);
      toast.error('Failed to create task. Please try again.');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
            <DialogDescription>
              Assign a new task to this agent. The task will be queued and processed automatically.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">
                Task Title <span className="text-destructive">*</span>
              </Label>
              <Input
                id="title"
                placeholder="e.g., Q4 Financial Analysis"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isLoading || isProcessingFile}
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">
                Description
              </Label>
              <Textarea
                id="description"
                placeholder="Provide detailed instructions for the task..."
                value={description}
                onChange={handleDescriptionChange}
                disabled={isLoading || isProcessingFile}
                rows={4}
              />
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">
                  {description.length} characters
                </span>
                <span className={remainingChars < 500 ? 'text-orange-500' : 'text-muted-foreground'}>
                  {remainingChars} remaining
                </span>
              </div>
            </div>
            
            {/* File Upload Section */}
            <div className="grid gap-2">
              <Label htmlFor="file-upload">
                Attach File (Optional)
              </Label>
              <div className="flex flex-col gap-2">
                {!uploadedFile ? (
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isLoading || isProcessingFile}
                    >
                      {isProcessingFile ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Upload PDF or TXT
                        </>
                      )}
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.txt"
                      onChange={handleFileUpload}
                      className="hidden"
                      disabled={isLoading || isProcessingFile}
                    />
                  </div>
                ) : (
                  <div className="flex items-center gap-2 p-3 border rounded-lg bg-muted/50">
                    <div className="flex-1 flex items-center gap-2">
                      {uploadedFile.type === 'application/pdf' ? (
                        <FileText className="h-4 w-4 text-red-500" />
                      ) : (
                        <File className="h-4 w-4 text-blue-500" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {uploadedFile.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {fileContent.length} characters extracted
                        </p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={handleRemoveFile}
                      disabled={isLoading}
                      className="h-8 w-8"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  Supported formats: PDF, TXT (Max 5MB). Content will be added to description.
                </p>
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={priority}
                onValueChange={(value) => setPriority(value as TaskPriority)}
                disabled={isLoading || isProcessingFile}
              >
                <SelectTrigger id="priority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Character count warning */}
            {totalChars > 0 && (
              <div className={`p-3 rounded-lg text-sm ${
                remainingChars < 0 
                  ? 'bg-destructive/10 text-destructive' 
                  : remainingChars < 500 
                  ? 'bg-orange-500/10 text-orange-600' 
                  : 'bg-muted'
              }`}>
                <p className="font-medium">
                  Total: {totalChars} / {MAX_CHARS} characters
                </p>
                {fileContent && (
                  <p className="text-xs mt-1">
                    Description: {description.length} | File: {fileContent.length}
                  </p>
                )}
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading || isProcessingFile}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading || isProcessingFile || remainingChars < 0}
            >
              {(isLoading || isProcessingFile) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create Task
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
