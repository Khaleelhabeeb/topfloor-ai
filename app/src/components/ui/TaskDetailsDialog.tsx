import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useTasks } from '@/hooks/useTasks';
import { TaskStatus } from '@/lib/tasks';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import {
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle,
  Loader2,
  Trash2,
  Ban,
  ChevronDown,
  ChevronUp,
  FileText,
  Download,
} from 'lucide-react';

interface TaskDetailsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskId: number | null;
  onTaskUpdated?: () => void;
}

export function TaskDetailsDialog({
  open,
  onOpenChange,
  taskId,
  onTaskUpdated,
}: TaskDetailsDialogProps) {
  const { currentTask, fetchTask, updateTask, deleteTask, isLoading, clearCurrentTask } = useTasks();
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [isResultExpanded, setIsResultExpanded] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (open && taskId) {
      fetchTask(taskId).catch((error) => {
        console.error('Failed to fetch task:', error);
        toast.error('Failed to load task details');
      });
    }
  }, [open, taskId, fetchTask]);

  useEffect(() => {
    if (!open) {
      clearCurrentTask();
      setIsDescriptionExpanded(false);
      setIsResultExpanded(false);
    }
  }, [open, clearCurrentTask]);

  const handleDownloadPDF = async () => {
    if (!currentTask || !currentTask.result_data?.response) {
      toast.error('No results to download');
      return;
    }

    setIsDownloading(true);
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);
      let yPosition = margin;

      // Helper function to check if we need a new page
      const checkNewPage = (requiredSpace: number) => {
        if (yPosition + requiredSpace > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
          return true;
        }
        return false;
      };

      // Helper function to render text with markdown formatting (bold, italic, inline code)
      const renderTextWithFormatting = (text: string, x: number, y: number, maxWidth: number, fontSize: number = 10) => {
        // Parse markdown: **bold**, *italic*, `code`, [link](url)
        const segments: Array<{ text: string; bold: boolean; italic: boolean; code: boolean }> = [];
        let currentPos = 0;
        
        // Regex to match **bold**, *italic*, `code`, and [text](url)
        const markdownRegex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[([^\]]+)\]\(([^)]+)\))/g;
        let match;
        
        while ((match = markdownRegex.exec(text)) !== null) {
          // Add text before the match
          if (match.index > currentPos) {
            segments.push({
              text: text.substring(currentPos, match.index),
              bold: false,
              italic: false,
              code: false,
            });
          }
          
          const matched = match[0];
          if (matched.startsWith('**') && matched.endsWith('**')) {
            // Bold text
            segments.push({
              text: matched.slice(2, -2),
              bold: true,
              italic: false,
              code: false,
            });
          } else if (matched.startsWith('*') && matched.endsWith('*') && !matched.startsWith('**')) {
            // Italic text
            segments.push({
              text: matched.slice(1, -1),
              bold: false,
              italic: true,
              code: false,
            });
          } else if (matched.startsWith('`') && matched.endsWith('`')) {
            // Inline code
            segments.push({
              text: matched.slice(1, -1),
              bold: false,
              italic: false,
              code: true,
            });
          } else if (matched.startsWith('[')) {
            // Link - just show the text part
            segments.push({
              text: match[2] || matched,
              bold: false,
              italic: false,
              code: false,
            });
          }
          
          currentPos = match.index + matched.length;
        }
        
        // Add remaining text
        if (currentPos < text.length) {
          segments.push({
            text: text.substring(currentPos),
            bold: false,
            italic: false,
            code: false,
          });
        }
        
        // If no markdown found, add the whole text
        if (segments.length === 0) {
          segments.push({ text, bold: false, italic: false, code: false });
        }
        
        let currentX = x;
        let currentY = y;
        const lineHeight = fontSize * 0.5;
        
        segments.forEach(segment => {
          if (!segment.text) return;
          
          // Set font style
          if (segment.code) {
            pdf.setFont('courier', 'normal');
            pdf.setFontSize(fontSize - 1);
            // Add background for inline code
            const textWidth = pdf.getTextWidth(segment.text);
            pdf.setFillColor(240, 240, 240);
            pdf.rect(currentX - 1, currentY - fontSize * 0.7, textWidth + 2, fontSize * 0.9, 'F');
          } else {
            const fontStyle = segment.bold && segment.italic ? 'bolditalic' : 
                            segment.bold ? 'bold' : 
                            segment.italic ? 'italic' : 'normal';
            pdf.setFont('helvetica', fontStyle);
            pdf.setFontSize(fontSize);
          }
          
          // Word wrapping
          const words = segment.text.split(' ');
          words.forEach((word, idx) => {
            const wordWithSpace = word + (idx < words.length - 1 ? ' ' : '');
            const wordWidth = pdf.getTextWidth(wordWithSpace);
            
            // Check if we need to wrap to next line
            if (currentX + wordWidth > x + maxWidth && currentX > x) {
              currentX = x;
              currentY += lineHeight;
            }
            
            pdf.text(wordWithSpace, currentX, currentY);
            currentX += wordWidth;
          });
        });
        
        // Reset to normal font
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(fontSize);
        
        const totalLines = Math.ceil((currentY - y) / lineHeight) + 1;
        return totalLines;
      };

      // Add TopFloor AI branding header
      pdf.setFillColor(139, 92, 69); // Primary color #8B5C45
      pdf.rect(0, 0, pageWidth, 35, 'F');
      
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.text('TopFloor AI', margin, 20);
      
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text('Task Analysis Report', margin, 28);

      yPosition = 45;

      // Add metadata section with background
      pdf.setFillColor(245, 245, 245);
      pdf.rect(margin - 5, yPosition - 5, contentWidth + 10, 35, 'F');
      pdf.setDrawColor(139, 92, 69);
      pdf.setLineWidth(2);
      pdf.line(margin - 5, yPosition - 5, margin - 5, yPosition + 30);

      // Task title
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      const titleLines = pdf.splitTextToSize(currentTask.title, contentWidth - 10);
      pdf.text(titleLines, margin, yPosition);
      yPosition += (titleLines.length * 6) + 8;

      // Task metadata
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Task ID: ${currentTask.task_id}`, margin, yPosition);
      pdf.text(`Status: ${currentTask.status}`, margin + 90, yPosition);
      yPosition += 5;
      pdf.text(`Agent: ${currentTask.agent_type.replace('_', ' ')}`, margin, yPosition);
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, margin + 90, yPosition);
      yPosition += 15;

      // Separator line
      pdf.setDrawColor(200, 200, 200);
      pdf.setLineWidth(0.5);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 10;

      // Results section header
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(139, 92, 69);
      pdf.text('Analysis Results', margin, yPosition);
      yPosition += 8;

      // Process markdown content line by line
      pdf.setTextColor(0, 0, 0);
      const lines = currentTask.result_data.response.split('\n');
      let inTable = false;
      let tableData: string[][] = [];
      let tableHeaders: string[] = [];
      let inCodeBlock = false;
      let codeBlockContent: string[] = [];

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Handle code blocks
        if (line.trim().startsWith('```')) {
          if (!inCodeBlock) {
            inCodeBlock = true;
            codeBlockContent = [];
            continue;
          } else {
            // End of code block
            inCodeBlock = false;
            checkNewPage(codeBlockContent.length * 5 + 10);
            
            pdf.setFillColor(244, 244, 244);
            const blockHeight = codeBlockContent.length * 5 + 6;
            pdf.rect(margin, yPosition - 2, contentWidth, blockHeight, 'F');
            pdf.setDrawColor(139, 92, 69);
            pdf.setLineWidth(1);
            pdf.line(margin, yPosition - 2, margin, yPosition + blockHeight - 2);
            
            pdf.setFont('courier', 'normal');
            pdf.setFontSize(8);
            codeBlockContent.forEach(codeLine => {
              pdf.text(codeLine, margin + 3, yPosition);
              yPosition += 5;
            });
            pdf.setFont('helvetica', 'normal');
            yPosition += 5;
            continue;
          }
        }

        if (inCodeBlock) {
          codeBlockContent.push(line);
          continue;
        }

        // Handle tables
        if (line.trim().startsWith('|')) {
          const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
          
          if (!inTable) {
            inTable = true;
            tableHeaders = cells;
            tableData = [];
          } else if (line.includes('---')) {
            // Skip separator line
            continue;
          } else {
            tableData.push(cells);
          }
          continue;
        } else if (inTable) {
          // End of table, render it
          inTable = false;
          checkNewPage(30);
          
          // Process markdown in table cells (bold, italic, code)
          const processMarkdown = (text: string) => {
            // Remove markdown but preserve the text
            return text
              .replace(/\*\*([^*]+)\*\*/g, '$1')  // Bold
              .replace(/\*([^*]+)\*/g, '$1')      // Italic
              .replace(/`([^`]+)`/g, '$1')        // Code
              .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1'); // Links
          };
          
          const processedHeaders = tableHeaders.map(cell => processMarkdown(cell));
          const processedBody = tableData.map(row => row.map(cell => processMarkdown(cell)));
          
          autoTable(pdf, {
            head: [processedHeaders],
            body: processedBody,
            startY: yPosition,
            margin: { left: margin, right: margin },
            theme: 'grid',
            headStyles: {
              fillColor: [139, 92, 69],
              textColor: [255, 255, 255],
              fontStyle: 'bold',
              fontSize: 9,
            },
            bodyStyles: {
              fontSize: 8,
              textColor: [51, 51, 51],
            },
            alternateRowStyles: {
              fillColor: [249, 249, 249],
            },
            styles: {
              lineColor: [221, 221, 221],
              lineWidth: 0.1,
            },
            // Apply bold styling to cells that originally had bold markers
            didParseCell: function(data) {
              const cell = data.cell;
              const isHeader = data.row.section === 'head';
              const originalText = isHeader 
                ? tableHeaders[data.column.index] 
                : (data.row.index >= 0 ? tableData[data.row.index][data.column.index] : '');
              
              // Check for markdown formatting in original text
              if (originalText) {
                if (originalText.includes('**')) {
                  cell.styles.fontStyle = 'bold';
                }
                if (originalText.includes('`')) {
                  cell.styles.font = 'courier';
                  cell.styles.fillColor = [245, 245, 245];
                }
              }
            },
          });
          
          yPosition = (pdf as any).lastAutoTable.finalY + 10;
          tableData = [];
          tableHeaders = [];
        }

        // Handle headings - check for exact match at start (must check from largest to smallest)
        if (line.match(/^####\s+/)) {
          checkNewPage(12);
          pdf.setFontSize(10);
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(100, 100, 100);
          const text = line.replace(/^####\s+/, '');
          const textLines = pdf.splitTextToSize(text, contentWidth);
          pdf.text(textLines, margin, yPosition);
          yPosition += (textLines.length * 5) + 3;
          pdf.setFont('helvetica', 'normal');
          pdf.setTextColor(0, 0, 0);
          continue;
        } else if (line.match(/^###\s+/)) {
          checkNewPage(15);
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(85, 85, 85);
          const text = line.replace(/^###\s+/, '');
          const textLines = pdf.splitTextToSize(text, contentWidth);
          pdf.text(textLines, margin, yPosition);
          yPosition += (textLines.length * 6) + 4;
          pdf.setFont('helvetica', 'normal');
          pdf.setTextColor(0, 0, 0);
          continue;
        } else if (line.match(/^##\s+/)) {
          checkNewPage(18);
          pdf.setFontSize(12);
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(51, 51, 51);
          const text = line.replace(/^##\s+/, '');
          const textLines = pdf.splitTextToSize(text, contentWidth);
          pdf.text(textLines, margin, yPosition);
          yPosition += (textLines.length * 7) + 5;
          pdf.setFont('helvetica', 'normal');
          pdf.setTextColor(0, 0, 0);
          continue;
        } else if (line.match(/^#\s+/)) {
          checkNewPage(20);
          pdf.setFontSize(14);
          pdf.setFont('helvetica', 'bold');
          pdf.setTextColor(139, 92, 69);
          const text = line.replace(/^#\s+/, '');
          const textLines = pdf.splitTextToSize(text, contentWidth);
          pdf.text(textLines, margin, yPosition);
          yPosition += (textLines.length * 8) + 3;
          pdf.setDrawColor(139, 92, 69);
          pdf.setLineWidth(0.5);
          pdf.line(margin, yPosition, pageWidth - margin, yPosition);
          yPosition += 5;
          pdf.setFont('helvetica', 'normal');
          pdf.setTextColor(0, 0, 0);
          continue;
        }

        // Handle lists (including nested lists)
        const listMatch = line.match(/^(\s*)([\*\-]|\d+\.)\s+(.+)$/);
        if (listMatch) {
          checkNewPage(10);
          const indent = listMatch[1].length;
          const bullet = listMatch[2];
          const content = listMatch[3];
          
          const indentPixels = margin + 5 + (indent * 3);
          const bulletChar = bullet.match(/\d+\./) ? bullet : '•';
          
          pdf.setFontSize(10);
          pdf.setFont('helvetica', 'normal');
          pdf.text(bulletChar, indentPixels, yPosition);
          
          const linesRendered = renderTextWithFormatting(content, indentPixels + 5, yPosition, contentWidth - (indentPixels - margin) - 5, 10);
          yPosition += (linesRendered * 5) + 2;
          continue;
        }

        // Handle horizontal rules
        if (line.match(/^(\-{3,}|\*{3,}|_{3,})$/)) {
          checkNewPage(8);
          pdf.setDrawColor(200, 200, 200);
          pdf.setLineWidth(0.5);
          pdf.line(margin, yPosition, pageWidth - margin, yPosition);
          yPosition += 8;
          continue;
        }

        // Handle blockquotes
        if (line.match(/^>\s+/)) {
          checkNewPage(10);
          const text = line.replace(/^>\s+/, '');
          
          // Draw blockquote bar
          pdf.setDrawColor(139, 92, 69);
          pdf.setLineWidth(2);
          pdf.line(margin, yPosition - 3, margin, yPosition + 7);
          
          // Draw background
          pdf.setFillColor(250, 250, 250);
          const textWidth = contentWidth - 10;
          pdf.rect(margin + 5, yPosition - 3, textWidth, 10, 'F');
          
          pdf.setFontSize(10);
          pdf.setTextColor(80, 80, 80);
          const linesRendered = renderTextWithFormatting(text, margin + 10, yPosition, textWidth - 10, 10);
          pdf.setTextColor(0, 0, 0);
          yPosition += (linesRendered * 5) + 5;
          continue;
        }

        // Handle empty lines
        if (line.trim() === '') {
          yPosition += 4;
          continue;
        }

        // Handle regular paragraphs
        checkNewPage(10);
        pdf.setFontSize(10);
        pdf.setFont('helvetica', 'normal');
        const linesRendered = renderTextWithFormatting(line, margin, yPosition, contentWidth, 10);
        yPosition += (linesRendered * 5) + 3;
      }

      // Add footer on all pages
      const totalPages = pdf.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        pdf.setPage(i);
        const footerY = pageHeight - 15;
        pdf.setDrawColor(139, 92, 69);
        pdf.setLineWidth(0.5);
        pdf.line(margin, footerY - 5, pageWidth - margin, footerY - 5);
        pdf.setFontSize(8);
        pdf.setTextColor(100, 100, 100);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Generated by TopFloor AI', margin, footerY);
        pdf.setFont('helvetica', 'normal');
        pdf.text(`Page ${i} of ${totalPages}`, pageWidth - margin - 20, footerY);
      }

      // Save the PDF
      const fileName = `topfloor-ai-${currentTask.task_id}-${Date.now()}.pdf`;
      pdf.save(fileName);
      
      toast.success('PDF downloaded successfully');
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      toast.error('Failed to generate PDF. Check console for details.');
    } finally {
      setIsDownloading(false);
    }
  };

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-blue-500" />;
      case 'pending':
      case 'queued':
        return <AlertCircle className="h-5 w-5 text-orange-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <Ban className="h-5 w-5 text-gray-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: TaskStatus) => {
    const variants: Record<TaskStatus, { variant: 'default' | 'secondary' | 'outline' | 'destructive'; className?: string }> = {
      completed: { variant: 'default', className: 'bg-green-500 hover:bg-green-600 text-white' },
      in_progress: { variant: 'secondary', className: '' },
      pending: { variant: 'outline', className: '' },
      queued: { variant: 'outline', className: '' },
      failed: { variant: 'destructive', className: '' },
      cancelled: { variant: 'outline', className: '' },
    };

    const config = variants[status];

    return (
      <Badge variant={config.variant} className={`text-xs ${config.className}`}>
        {status.replace('_', ' ')}
      </Badge>
    );
  };

  const handleCancelTask = async () => {
    if (!currentTask) return;

    if (!confirm('Are you sure you want to cancel this task?')) return;

    try {
      await updateTask(currentTask.id, { status: 'cancelled' });
      toast.success('Task cancelled successfully');
      if (onTaskUpdated) onTaskUpdated();
    } catch (error) {
      console.error('Failed to cancel task:', error);
      toast.error('Failed to cancel task');
    }
  };

  const handleDeleteTask = async () => {
    if (!currentTask) return;

    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) return;

    try {
      await deleteTask(currentTask.id);
      toast.success('Task deleted successfully');
      onOpenChange(false);
      if (onTaskUpdated) onTaskUpdated();
    } catch (error) {
      console.error('Failed to delete task:', error);
      toast.error('Failed to delete task');
    }
  };

  if (!currentTask && !isLoading) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[1100px] max-h-[90vh]">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : currentTask ? (
          <>
            <DialogHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <DialogTitle className="text-xl">{currentTask.title}</DialogTitle>
                  <DialogDescription className="mt-2">
                    Task ID: {currentTask.task_id}
                  </DialogDescription>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(currentTask.status)}
                  {getStatusBadge(currentTask.status)}
                </div>
              </div>
            </DialogHeader>

            <ScrollArea className="max-h-[70vh]">
              <div className="space-y-4 pr-4">
                {/* Result Data - Moved to top */}
                {currentTask.result_data && (
                  <>
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-primary" />
                          <h4 className="text-sm font-semibold">Task Results</h4>
                        </div>
                        <div className="flex items-center gap-2">
                          {currentTask.result_data.response && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleDownloadPDF}
                                disabled={isDownloading}
                                className="h-8"
                              >
                                {isDownloading ? (
                                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                                ) : (
                                  <Download className="h-4 w-4 mr-1" />
                                )}
                                Download PDF
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setIsResultExpanded(!isResultExpanded)}
                                className="h-8"
                              >
                                {isResultExpanded ? (
                                  <>
                                    <ChevronUp className="h-4 w-4 mr-1" />
                                    Collapse
                                  </>
                                ) : (
                                  <>
                                    <ChevronDown className="h-4 w-4 mr-1" />
                                    Expand
                                  </>
                                )}
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                      
                      {/* Display LLM Response with Markdown Rendering */}
                      {currentTask.result_data.response && (
                        <div className={`border border-green-500 rounded-lg overflow-hidden transition-all ${
                          isResultExpanded ? 'max-h-[600px]' : 'max-h-[300px]'
                        }`}>
                          <ScrollArea className={isResultExpanded ? 'h-[580px] p-6' : 'h-[280px] p-6'}>
                            <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:font-semibold prose-h1:text-xl prose-h2:text-lg prose-h3:text-base prose-p:text-sm prose-p:leading-relaxed prose-li:text-sm prose-table:text-xs prose-pre:text-xs prose-code:text-xs">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {currentTask.result_data.response}
                              </ReactMarkdown>
                            </div>
                          </ScrollArea>
                        </div>
                      )}
                      
                      {/* Display Summary if available */}
                      {currentTask.result_data.summary && !currentTask.result_data.response && (
                        <div className="border rounded-lg p-4 bg-muted/50">
                          <p className="text-sm leading-relaxed">
                            {currentTask.result_data.summary}
                          </p>
                        </div>
                      )}
                      
                      {/* Display Render Payload if available and no response */}
                      {currentTask.result_data.render_payload && !currentTask.result_data.response && (
                        <div className={`border rounded-lg overflow-hidden transition-all ${
                          isResultExpanded ? 'max-h-[500px]' : 'max-h-[150px]'
                        }`}>
                          <ScrollArea className={isResultExpanded ? 'h-[450px] p-4' : 'h-[100px] p-4'}>
                            <pre className="text-xs overflow-auto">
                              {JSON.stringify(currentTask.result_data.render_payload, null, 2)}
                            </pre>
                          </ScrollArea>
                        </div>
                      )}
                      
                      {/* Display metadata if available */}
                      {(currentTask.result_data.session_id || currentTask.result_data.events_count !== undefined) && (
                        <div className="mt-3 pt-3 border-t">
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            {currentTask.result_data.session_id && (
                              <span>Session: {currentTask.result_data.session_id}</span>
                            )}
                            {currentTask.result_data.events_count !== undefined && (
                              <span>Events: {currentTask.result_data.events_count}</span>
                            )}
                            {currentTask.result_data.memories_used !== undefined && (
                              <span>Memories: {currentTask.result_data.memories_used}</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    <Separator />
                  </>
                )}

                {/* Description - Moved below results */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold">Description</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                      className="h-8"
                    >
                      {isDescriptionExpanded ? (
                        <>
                          <ChevronUp className="h-4 w-4 mr-1" />
                          Show Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-4 w-4 mr-1" />
                          Show More
                        </>
                      )}
                    </Button>
                  </div>
                  <div className={`text-sm text-muted-foreground ${
                    isDescriptionExpanded ? '' : 'line-clamp-2'
                  }`}>
                    {currentTask.description}
                  </div>
                </div>

                {/* Error Message */}
                {currentTask.error_message && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="text-sm font-semibold mb-2 text-destructive">Error</h4>
                      <p className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
                        {currentTask.error_message}
                      </p>
                    </div>
                  </>
                )}

                <Separator />

                {/* Task Details - Moved to bottom */}
                <div>
                  <h4 className="text-sm font-semibold mb-3">Task Details</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Priority</h5>
                      <Badge variant="outline" className="capitalize">
                        {currentTask.priority}
                      </Badge>
                    </div>
                    <div>
                      <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Type</h5>
                      <Badge variant="outline" className="capitalize">
                        {currentTask.task_type}
                      </Badge>
                    </div>
                    <div>
                      <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Agent</h5>
                      <p className="text-sm capitalize">
                        {currentTask.agent_type.replace('_', ' ')}
                      </p>
                    </div>
                    <div>
                      <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Created</h5>
                      <p className="text-sm">
                        {new Date(currentTask.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Timestamps */}
                {(currentTask.started_at || currentTask.completed_at) && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="text-sm font-semibold mb-3">Timeline</h4>
                      <div className="grid grid-cols-2 gap-4">
                        {currentTask.started_at && (
                          <div>
                            <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Started</h5>
                            <p className="text-sm">
                              {new Date(currentTask.started_at).toLocaleString()}
                            </p>
                          </div>
                        )}
                        {currentTask.completed_at && (
                          <div>
                            <h5 className="text-xs font-semibold mb-1 text-muted-foreground">Completed</h5>
                            <p className="text-sm">
                              {new Date(currentTask.completed_at).toLocaleString()}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </ScrollArea>

            <DialogFooter className="flex-col sm:flex-row gap-2">
              <div className="flex gap-2 flex-1">
                {currentTask.status === 'in_progress' && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancelTask}
                    disabled={isLoading}
                  >
                    <Ban className="h-4 w-4 mr-2" />
                    Cancel Task
                  </Button>
                )}
                {(currentTask.status === 'completed' || 
                  currentTask.status === 'failed' || 
                  currentTask.status === 'cancelled') && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleDeleteTask}
                    disabled={isLoading}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                )}
              </div>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Close
              </Button>
            </DialogFooter>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
