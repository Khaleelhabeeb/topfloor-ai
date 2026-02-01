# Virtual Office - Feature Overview

## 🎮 Game Mechanics

### Movement & Navigation
- **WASD / Arrow Keys**: Move character around the office
- **Walk-through doors**: Automatically enter offices by walking through open doorways
- **Collision detection**: Realistic boundaries with walls and furniture
- **Isometric camera**: Smooth follow camera with lag effect
- **Minimap**: Real-time position tracking with office labels

### Interactions
- **E Key**: Interact with objects/people when inside offices or near CEO chair
- **Escape Key**: Exit current interface/mode

---

## 👥 Employee Office Interface

When you walk into an employee's office and press **E**, you get a comprehensive dashboard:

### Main Interface (Default)
- **Left Sidebar (Toggleable)**
  - Interaction history with timestamps
  - Past meeting durations
  - Activity log

- **Center Content**
  - **Active Tasks**: Task list with status, priority, and due dates
  - **Quick Stats**: Visual cards showing completed/in-progress/pending counts
  - **Settings Panel**: Configure notifications, auto-save, privacy

- **Right Sidebar**
  - Real-time chat with the employee
  - Message history
  - Send messages with Enter key

- **Header Actions**
  - **"Go Live" Button**: Switch to video call interface
  - Settings toggle
  - Close button

### Video Call Mode (Click "Go Live")
- Full-screen video interface
- Employee avatar display
- Video controls (mute, camera, screen share)
- End call button
- Back arrow to return to main interface
- Chat sidebar remains available

---

## 🎯 CEO Dashboard

When you sit at the CEO's desk and press **E**, you get an executive command center:

### Overview
- **Left Sidebar (Toggleable)**
  - Activity history
  - Recent actions and decisions
  - Timestamped events

- **Main Dashboard**
  - **Stats Overview**: 5 key metrics cards
    - Total Tasks
    - Completed Tasks
    - In Progress Tasks
    - Pending Tasks
    - Average Progress %
  
  - **Tasks by Agent**: Organized view showing:
    - Each employee with their avatar
    - All tasks assigned to them
    - Task status, priority, and progress bars
    - Quick "@mention" button to message them
    - Visual progress indicators

  - **Settings Panel**: Configure dashboard preferences
    - Task notifications
    - Auto-assign tasks
    - Report generation scheduling

- **Right Sidebar (Team Chat)**
  - **@Mention System**: Type @ to mention team members
  - Auto-complete dropdown when typing @
  - Send messages to specific agents
  - Simulated agent responses
  - Real-time chat history
  - System messages

### Key Features
- **Agent Assignment Tracking**: See who's working on what
- **Progress Monitoring**: Visual progress bars for each task
- **Priority Management**: Color-coded task priorities (red/yellow/green)
- **Status Indicators**: Icons for completed/in-progress/pending
- **Direct Communication**: @mention any agent to send them a message
- **Quick Actions**: Message button next to each agent

---

## 🎨 Visual Design

### Theme
- Warm corporate aesthetic
- Soft shadows (reduced darkness)
- Professional color palette
- Smooth animations and transitions

### UI Components
- Modern card-based layouts
- Responsive design
- Accessible components (Radix UI)
- Tailwind CSS styling
- Smooth hover effects

### 3D Environment
- Low-poly office design
- Warm wood floors and carpet
- Cream-colored walls
- Open doorways with visible frames
- Office furniture (desks, chairs, plants)
- Premium CEO desk area

---

## 🔧 Technical Stack

- **React 18** + TypeScript
- **Three.js** + React Three Fiber (3D rendering)
- **Zustand** (state management)
- **shadcn/ui** + Radix UI (components)
- **Tailwind CSS** (styling)
- **Vite** (build tool)

---

## 📊 Data Management

### State Structure
- Game mode tracking (exploring/video-call/ceo-desk)
- Video call mode (interface/live-call)
- Player position and proximity detection
- Chat message history per employee
- Task assignments and progress
- Employee data and avatars

### Mock Data
- 4 employees (Sarah, James, Alex, Peter)
- 7 CEO tasks with assignments
- Activity history
- Chat messages
- Task progress tracking

---

## 🚀 Future Enhancements

Potential features to add:
- Real-time task updates
- File attachments in chat
- Video recording/playback
- Calendar integration
- Performance analytics
- Team collaboration tools
- Document management
- Meeting scheduler
