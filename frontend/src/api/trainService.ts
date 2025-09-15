import apiClient from './apiClient';
import { Train, TrainList, TrainResponse } from './types';

class TrainService {
  private baseUrl = '/api/trains';

  async getTrains(
    params: { skip?: number; limit?: number; train_id?: string; train_type?: string } = {}
  ): Promise<TrainList> {
    return apiClient.get<TrainList>(this.baseUrl, { params });
  }

  async getTrain(trainId: string): Promise<TrainResponse> {
    return apiClient.get<TrainResponse>(`${this.baseUrl}/${trainId}`);
  }

  async createTrain(train: Train): Promise<TrainResponse> {
    return apiClient.post<TrainResponse>(this.baseUrl, train);
  }

  async updateTrain(trainId: string, train: Partial<Train>): Promise<TrainResponse> {
    return apiClient.put<TrainResponse>(`${this.baseUrl}/${trainId}`, train);
  }

  async deleteTrain(trainId: string): Promise<void> {
    return apiClient.delete<void>(`${this.baseUrl}/${trainId}`);
  }
}

export const trainService = new TrainService();