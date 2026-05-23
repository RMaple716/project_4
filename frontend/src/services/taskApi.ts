import apiClient from './api';

export interface Task {
  task_id: string;
  requirement_id: string;
  task_type: string;
  status: string;
  progress: number;
  result?: any;
  created_at?: string;
  updated_at?: string;
}

export interface SubTask {
  sub_task_id: string;
  parent_task_id: string;
  agent_type: string;
  status: string;
  result?: any;
}

export const taskApi = {
  // 任务分解
  decompose: (requirementId: string, structuredRequirement: any) => 
    apiClient.post('/task/decompose', {
      requirement_id: requirementId,
      structured_requirement: structuredRequirement,
    }),
  
  // 获取任务状态
  getById: (taskId: string) => 
    apiClient.get(`/task/${taskId}`),
  
  // 更新任务结果
  update: (taskId: string, data: any) => 
    apiClient.post(`/task/update/${taskId}`, data),
};
