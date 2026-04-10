import db from './db.demo.json';
import { STAGES, DEMO_ROLE } from '../../utils/constants';

let state = JSON.parse(JSON.stringify(db));

function roleOf(userId){ 
  const u=(state.users||[]).find(x=>x.id===userId); 
  return u?u.role:'manager'; 
}

const delay = (ms=250)=>new Promise(r=>setTimeout(r,ms));

export async function listChannels(){ await delay(); return state.channels; }

export async function listTasks(channelId){ await delay(); return state.tasks.filter(t=>t.channel_id===channelId); }

export async function getTask(taskId){
  await delay();
  return {
    task: state.tasks.find(t=>t.id===taskId),
    comments: state.comments[taskId]||[],
    attachments: state.attachments[taskId]||[],
    activity: state.activity[taskId]||[]
  };
}

export async function moveTask(taskId, toStage, currentUserId){
  await delay(200);
  const t = state.tasks.find(x=>x.id===taskId);
  if(!t) throw new Error('not_found');
  const from = t.status;
  const roles={admin:true,manager:true}; 
  const isBackward=STAGES.indexOf(toStage) < STAGES.indexOf(from); 
  const role=roleOf(currentUserId); 
  if(isBackward && !roles[role]) throw new Error('forbidden_backward');
  t.status = toStage;
  (state.activity[taskId]=state.activity[taskId]||[]).push({
    id: crypto.randomUUID(), user_id: currentUserId, action:'status_change',
    old_status: from, new_status: toStage, timestamp: new Date().toISOString()
  });
  return { ok:true, task:t };
}

export async function addComment(taskId, userId, body){
  await delay(120);
  (state.comments[taskId]=state.comments[taskId]||[]).push({
    id: crypto.randomUUID(), user_id:userId, body, created_at:new Date().toISOString()
  });
  return { ok:true };
}

export function __reset(){ state = JSON.parse(JSON.stringify(db)); return true; }

export async function updateTaskTitle(taskId, title){ const t = state.tasks.find(x=>x.id===taskId); if(!t) throw new Error("not_found"); t.title = title; (state.activity[taskId]=state.activity[taskId]||[]).push({ id: crypto.randomUUID(), user_id: "u_mgr", action:"title_change", old_title:"", new_title:title, timestamp:new Date().toISOString() }); return {ok:true, task:t}; }
