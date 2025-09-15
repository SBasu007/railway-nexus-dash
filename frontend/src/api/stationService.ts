import apiClient from './apiClient';
import { Station, StationList, StationResponse } from './types';

class StationService {
  private baseUrl = '/api/stations';

  async getStations(
    params: { skip?: number; limit?: number; name?: string } = {}
  ): Promise<StationList> {
    return apiClient.get<StationList>(this.baseUrl, { params });
  }

  async getStation(stationId: string): Promise<StationResponse> {
    return apiClient.get<StationResponse>(`${this.baseUrl}/${stationId}`);
  }

  async createStation(station: Station): Promise<StationResponse> {
    return apiClient.post<StationResponse>(this.baseUrl, station);
  }

  async updateStation(stationId: string, station: Partial<Station>): Promise<StationResponse> {
    return apiClient.put<StationResponse>(`${this.baseUrl}/${stationId}`, station);
  }

  async deleteStation(stationId: string): Promise<void> {
    return apiClient.delete<void>(`${this.baseUrl}/${stationId}`);
  }
}

export const stationService = new StationService();