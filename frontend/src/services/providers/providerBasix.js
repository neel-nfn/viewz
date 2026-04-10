const BASIX_API = import.meta.env.VITE_BASIX_API_URL || '/basix';

async function req(path, method='GET', body){
  const r = await fetch(`${BASIX_API}${path}`, {
    method,
    headers: {'Content-Type':'application/json'},
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'include'
  });
  if(!r.ok){
    let msg='request_failed';
    try{ const j=await r.json(); msg=j.error||j.message||msg; }catch(_){}
    throw new Error(msg);
  }
  return r.json();
}

export async function listChannels(){
  return req('/clients/list'); // [{id,name,brand_color}] expected
}

export async function listTasks(clientId){
  return req(`/tasks/list?client_id=${encodeURIComponent(clientId)}`);
}

export async function getTask(taskId){
  return req(`/tasks/detail?task_id=${encodeURIComponent(taskId)}`);
}

export async function moveTask(taskId, toStage, currentUserId){
  return req('/tasks/update','PUT',{task_id:taskId, stage:toStage, actor_id:currentUserId});
}

export async function addComment(taskId, userId, body){
  return req('/comments/add','POST',{task_id:taskId, user_id:userId, comment:body});
}

export async function health(){
  try{ await req('/health'); return {ok:true}; }catch(e){ return {ok:false, error:e.message}; }
}

