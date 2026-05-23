import apiClient from './api';

export interface Itinerary {
  itinerary_id?: string;
  user_id: string;
  requirement_id: string;
  city_name: string;
  travel_days: number;
  total_budget: number;
  schedule: ScheduleItem[];
  created_at?: string;
  updated_at?: string;
}

export interface ScheduleItem {
  day: number;
  time_slot: string;
  activity_type: string;
  name: string;
  location?: string;
  start_time?: string;
  end_time?: string;
  duration?: string;
  cost?: number;
  description?: string;
}

export const itineraryApi = {
  // 创建行程
  create: (data: Partial<Itinerary>) => 
    apiClient.post('/itinerary/create', data),
  
  // 获取行程详情
  getById: (id: string) => 
    apiClient.get(`/itinerary/${id}`),
  
  // 更新行程
  update: (id: string, data: Partial<Itinerary>) => 
    apiClient.put(`/itinerary/${id}`, data),
  
  // 删除行程
  delete: (id: string) => 
    apiClient.delete(`/itinerary/${id}`),
  
  // 获取用户所有行程
  getByUser: (userId: string) => 
    apiClient.get(`/itinerary/user/${userId}`),
};
