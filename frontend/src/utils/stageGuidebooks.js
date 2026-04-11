/**
 * Stage-Specific Guidebooks
 * 
 * Provides step-by-step guidance for VAs at each workflow stage.
 * Each guidebook includes instructions, tool links, and checklists.
 */

export const STAGE_GUIDEBOOKS = {
  research: {
    stage: 'research',
    title: 'Research (The Brain)',
    guide_md: `## Research Phase

Follow these steps to complete the research stage:

### 1. Trend Check
- **Tool:** [VidIQ Daily Ideas](https://www.vidiq.com/daily-ideas)
- **Action:** Review top trending ideas
- **Output:** Paste top 3 ideas in the inputs below

### 2. News Search
- **Tool:** [Perplexity](https://www.perplexity.ai/)
- **Action:** Search for "Latest F1 rumors [Driver Name]"
- **Output:** Document key findings

### 3. Keyword Gap Analysis
- **Tool:** [Semrush](https://www.semrush.com/)
- **Action:** Check search volume for:
  - "F1 2026"
  - "Red Bull Crisis"
  - Related trending keywords
- **Output:** Note keyword opportunities

### 4. Finalize Concept
- **Outcome:** Paste the *Final Video Title* and *Concept Note* in the fields below
- **Review:** Ensure concept is unique and has search potential`,
    
    tools: [
      { name: 'VidIQ Daily Ideas', url: 'https://www.vidiq.com/daily-ideas', type: 'external' },
      { name: 'Perplexity', url: 'https://www.perplexity.ai/', type: 'external' },
      { name: 'Semrush', url: 'https://www.semrush.com/', type: 'external' }
    ],
    
    checklist: [
      'Top 3 trending ideas identified',
      'News search completed',
      'Keyword gap analysis done',
      'Final video title determined',
      'Concept note written'
    ]
  },

  writing: {
    stage: 'writing',
    title: 'Writing (The Script)',
    guide_md: `## Scripting Phase

Follow these steps to generate the video script:

### 1. Generate Script
- **Tool:** [ChatGPT Plus](https://chat.openai.com/)
- **Action:** Open ChatGPT Plus

### 2. Use Template
- **Template:** "Grid Pulse 8min Template" (Embedded in Viewz)
- **Action:** Copy/Paste the template into ChatGPT
- **Input:** Drag the "Concept Note" from Stage 1 into the prompt

### 3. Quality Assurance
- **Hook Check:** Read the script against the *Hook Check* criteria
  - First 3 lines must shock/engage
  - Opening must hook within 5 seconds
- **Visual Cues:** Ensure script includes visual cue markers for B-roll

### 4. Finalize Script
- **Outcome:** Paste the full markdown script into the Viewz "Script" tab
- **Review:** Verify script length matches target duration (8-12 min)`,
    
    tools: [
      { name: 'ChatGPT Plus', url: 'https://chat.openai.com/', type: 'external' },
      { name: 'Grid Pulse Template', action: 'copy_clipboard', type: 'template' }
    ],
    
    checklist: [
      'Hook < 5 seconds',
      'Visual Cues included',
      'Script saved to Viewz',
      'Template applied correctly',
      'Concept note integrated'
    ]
  },

  design: {
    stage: 'design',
    title: 'Asset Generation (Design)',
    guide_md: `## Asset Generation Phase

Create all raw assets needed for video production:

### 1. Voiceover
- **Tool:** [ElevenLabs](https://elevenlabs.io/)
- **Action:** 
  - Copy script from Viewz
  - Generate "News Anchor" voice
  - Download MP3
- **Output:** Upload MP3 to Viewz Assets

### 2. Thumbnails
- **Tool:** [Ideogram](https://ideogram.ai/)
- **Prompt Example:** "Max Verstappen holding contract, dramatic lighting, text 'BETRAYAL'"
- **Action:** Generate 3 thumbnail variants
- **Output:** Upload all 3 variants to Viewz Assets

### 3. Music
- **Tool:** [Epidemic Sound](https://www.epidemicsound.com/)
- **Action:** Search for "Tension/Documentary" style tracks
- **Output:** Download 2 tracks
- **Upload:** Add to asset folder

### 4. Asset Confirmation
- **Outcome:** Confirm all "Raw Assets" are uploaded to the Google Drive link
- **Checklist:** VO, Thumbnails (3x), Music (2x)`,
    
    tools: [
      { name: 'ElevenLabs', url: 'https://elevenlabs.io/', type: 'external' },
      { name: 'Ideogram', url: 'https://ideogram.ai/', type: 'external' },
      { name: 'Epidemic Sound', url: 'https://www.epidemicsound.com/', type: 'external' }
    ],
    
    checklist: [
      'Voiceover generated and uploaded',
      '3 thumbnail variants created',
      '2 music tracks selected',
      'All assets in Google Drive folder',
      'Asset folder URL confirmed'
    ]
  },

  editing: {
    stage: 'editing',
    title: 'Editing (The Build)',
    guide_md: `## Editing Phase

Assemble the final video using all generated assets:

### 1. B-Roll Sourcing
- **Tool:** [InVideo](https://www.invideo.io/)
- **Action:** Generate generic filler B-roll if needed
- **Output:** Download relevant clips

### 2. Video Assembly
- **Tool:** [CapCut Pro](https://www.capcut.com/)
- **Process:**
  1. Import Voiceover & Music
  2. Match B-roll to "Visual Cues" in script
  3. Add overlays (Polls/CTAs) from **Canva** folder
  4. Sync audio levels
  5. Add captions

### 3. Review & Upload
- **Tool:** [Frame.io](https://frame.io/)
- **Action:** Upload Draft v1 to Frame.io
- **Output:** Paste Frame.io review link here
- **Status:** Wait for feedback before proceeding`,
    
    tools: [
      { name: 'InVideo', url: 'https://www.invideo.io/', type: 'external' },
      { name: 'CapCut Pro', url: 'https://www.capcut.com/', type: 'external' },
      { name: 'Canva', url: 'https://www.canva.com/', type: 'external' },
      { name: 'Frame.io', url: 'https://frame.io/', type: 'external' }
    ],
    
    checklist: [
      'B-roll sourced and imported',
      'VO and music synced',
      'Visual cues matched to script',
      'Overlays added (Polls/CTAs)',
      'Draft v1 uploaded to Frame.io',
      'Frame.io link shared'
    ]
  },

  scheduled: {
    stage: 'scheduled',
    title: 'Quality Assurance (Review)',
    guide_md: `## Quality Assurance Phase

Final review before scheduling:

### 1. Frame.io Review
- **Tool:** [Frame.io](https://frame.io/)
- **Check:** Have all comments been resolved?
- **Status:** Verify Frame.io status is "Approved"

### 2. Technical Check
- **Audio Levels:** Balanced and clear?
- **Captions:** Readable and accurate?
- **Visual Quality:** No glitches or artifacts?
- **Timing:** Matches target duration?

### 3. Content Review
- **Hook:** Still engaging in first 5 seconds?
- **Flow:** Narrative makes sense?
- **CTAs:** Properly placed and visible?

### 4. Approval
- **Outcome:** Mark as "Ready for Schedule" only if Frame.io status is "Approved"
- **Note:** Do not proceed if any critical issues remain`,
    
    tools: [
      { name: 'Frame.io', url: 'https://frame.io/', type: 'external' }
    ],
    
    checklist: [
      'All Frame.io comments resolved',
      'Audio levels balanced',
      'Captions readable',
      'No technical issues',
      'Frame.io status: Approved',
      'Ready for scheduling'
    ]
  },

  published: {
    stage: 'published',
    title: 'Schedule & Publish',
    guide_md: `## Schedule & Publish Phase

Final steps to publish and repurpose content:

### 1. YouTube Upload
- **Tool:** [YouTube Studio](https://studio.youtube.com/)
- **Action:** Upload final video
- **Metadata:** Copy Title/Desc/Tags from Viewz (generated by AI Assistant)

### 2. Optimization
- **Title:** Use AI-generated title from Viewz
- **Description:** Include full description with timestamps
- **Tags:** Apply all suggested tags
- **Thumbnail:** Select best-performing variant

### 3. Scheduling
- **Publish Date:** Set according to content calendar
- **Visibility:** Set to Public or Scheduled
- **Notifications:** Enable community notifications

### 4. Repurpose for Shorts
- **Tool:** [Minvo](https://minvo.io/) (or similar)
- **Action:** Upload long-form video
- **Output:** Generate 3 Shorts variants
- **Upload:** Schedule Shorts separately

### 5. Completion
- **Outcome:** Mark task as "Published"
- **Track:** Monitor initial performance metrics`,
    
    tools: [
      { name: 'YouTube Studio', url: 'https://studio.youtube.com/', type: 'external' },
      { name: 'Minvo', url: 'https://minvo.io/', type: 'external' }
    ],
    
    checklist: [
      'Video uploaded to YouTube',
      'Title/Desc/Tags optimized',
      'Thumbnail selected',
      'Video scheduled',
      '3 Shorts variants created',
      'Task marked as Published'
    ]
  }
};

/**
 * Get guidebook for a specific stage
 * @param {string} stage - The workflow stage
 * @returns {Object|null} The guidebook object or null if not found
 */
export function getGuidebookForStage(stage) {
  // Map different stage names to our guidebooks
  const stageMap = {
    'research': 'research',
    'writing': 'writing',
    'script': 'writing', // Alternative name
    'design': 'design',
    'asset_generation': 'design', // Alternative name
    'editing': 'editing',
    'edit': 'editing', // Alternative name
    'scheduled': 'scheduled',
    'review': 'scheduled', // QA/Review stage
    'qa': 'scheduled',
    'published': 'published',
    'publish': 'published' // Alternative name
  };

  const mappedStage = stageMap[stage?.toLowerCase()] || stage?.toLowerCase();
  return STAGE_GUIDEBOOKS[mappedStage] || null;
}

/**
 * Get default checklist for a stage
 * @param {string} stage - The workflow stage
 * @returns {Array} Array of checklist items
 */
export function getDefaultChecklist(stage) {
  const guidebook = getGuidebookForStage(stage);
  return guidebook?.checklist || [];
}

/**
 * Get default tool links for a stage
 * @param {string} stage - The workflow stage
 * @returns {Array} Array of tool link objects
 */
export function getDefaultToolLinks(stage) {
  const guidebook = getGuidebookForStage(stage);
  return guidebook?.tools || [];
}
