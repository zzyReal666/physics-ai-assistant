import { apiClient } from './client';
import type { TeachingPlanResponse } from '../../types';

export async function createTeachingPlan(topic: string, classInfo: string, requirements: string) {
  const { data } = await apiClient.post<TeachingPlanResponse>('/teaching/create-plan', {
    topic,
    class_info: classInfo,
    requirements
  });
  return data;
}
