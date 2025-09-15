import apiClient from './apiClient';
import { OptimizationRequest, OptimizationResult } from './types';

class OptimizationService {
  private baseUrl = '/api/optimizer';

  async optimizeRoute(request: {
    source_station: string;
    destination_station: string;
    departure_time?: string;
    arrival_time?: string;
    optimization_criteria?: string;
    constraints?: Record<string, any>;
  }): Promise<OptimizationResult> {
    return apiClient.post<OptimizationResult>(`${this.baseUrl}/optimize-route`, request);
  }

  async optimizeSchedule(request: OptimizationRequest): Promise<OptimizationResult> {
    return apiClient.post<OptimizationResult>(`${this.baseUrl}/optimize-schedule`, request);
  }

  async getOptimizationResult(optimizationId: string): Promise<OptimizationResult> {
    return apiClient.get<OptimizationResult>(`${this.baseUrl}/results/${optimizationId}`);
  }
}

export const optimizationService = new OptimizationService();