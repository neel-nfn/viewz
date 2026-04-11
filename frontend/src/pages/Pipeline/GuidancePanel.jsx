import { useState } from 'react';
import { getGuidebookForStage } from '../../utils/stageGuidebooks';

/**
 * GuidancePanel - Displays stage-specific guidebooks for VA workflow
 * 
 * Shows step-by-step instructions, tool links, and checklists based on the task's current stage.
 */
export default function GuidancePanel({ task, taskData, onChecklistUpdate }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [checkedItems, setCheckedItems] = useState(
    taskData?.stage_checklist?.map(item => 
      typeof item === 'string' ? { text: item, checked: false } : item
    ) || []
  );

  if (!task?.status) return null;

  const guidebook = getGuidebookForStage(task.status);
  if (!guidebook) {
    return (
      <section className="mb-6">
        <div className="font-semibold mb-2">Guidance</div>
        <div className="text-sm opacity-60 p-3 bg-base-200 rounded">
          No guidance available for stage: <code>{task.status}</code>
        </div>
      </section>
    );
  }

  // Merge task-specific checklist with default checklist
  const taskChecklist = taskData?.stage_checklist || [];
  const defaultChecklist = guidebook.checklist || [];
  
  // Combine checklists, prioritizing task-specific items
  const combinedChecklist = taskChecklist.length > 0 
    ? taskChecklist.map(item => typeof item === 'string' ? { text: item, checked: false } : item)
    : defaultChecklist.map(item => typeof item === 'string' ? { text: item, checked: false } : item);

  // Use task-specific tool links if available, otherwise use defaults
  const toolLinks = taskData?.tool_links?.length > 0 
    ? taskData.tool_links 
    : guidebook.tools || [];

  const handleCheckboxChange = (index) => {
    const updated = [...checkedItems];
    updated[index] = {
      ...updated[index],
      checked: !updated[index]?.checked
    };
    setCheckedItems(updated);
    
    // Notify parent component of checklist update
    if (onChecklistUpdate) {
      onChecklistUpdate(updated);
    }
  };

  return (
    <section className="mb-6 border-t border-base-300 pt-4">
      <div 
        className="flex justify-between items-center mb-3 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="font-semibold flex items-center gap-2">
          <span>📖</span>
          <span>{guidebook.title} - Guidance</span>
        </div>
        <button className="btn btn-ghost btn-xs">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-4">
          {/* Guide Content */}
          <div className="rounded-lg bg-base-200 p-4 text-sm leading-6 whitespace-pre-wrap">
            {guidebook.guide_md}
          </div>

          {/* Tool Links */}
          {toolLinks.length > 0 && (
            <div>
              <div className="font-medium text-sm mb-2">Quick Links</div>
              <div className="flex flex-wrap gap-2">
                {toolLinks.map((tool, idx) => (
                  <a
                    key={idx}
                    href={tool.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-sm btn-outline"
                    onClick={(e) => {
                      if (tool.action === 'copy_clipboard') {
                        e.preventDefault();
                        // Handle template copy action
                        navigator.clipboard.writeText('Grid Pulse 8min Template').then(() => {
                          alert('Template copied to clipboard!');
                        });
                      }
                    }}
                  >
                    {tool.name}
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Checklist */}
          {combinedChecklist.length > 0 && (
            <div>
              <div className="font-medium text-sm mb-2">Stage Checklist</div>
              <div className="space-y-2">
                {combinedChecklist.map((item, idx) => {
                  const text = typeof item === 'string' ? item : item.text;
                  const checked = typeof item === 'string' 
                    ? (checkedItems[idx]?.checked || false)
                    : (item.checked || false);
                  
                  return (
                    <label key={idx} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => handleCheckboxChange(idx)}
                        className="checkbox checkbox-sm"
                      />
                      <span className={`text-sm ${checked ? 'line-through opacity-60' : ''}`}>
                        {text}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {/* Asset Folder Link */}
          {taskData?.asset_folder_url && (
            <div>
              <div className="font-medium text-sm mb-2">Asset Folder</div>
              <a
                href={taskData.asset_folder_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-sm btn-link"
              >
                Open Google Drive Folder
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
