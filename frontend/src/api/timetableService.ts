import apiClient from './apiClient';
import { TimetableEntry, TimetableList, TimetableResponse } from './types';

class TimetableService {
  private baseUrl = '/api/timetable';

  async getTimetable(
    params: { skip?: number; limit?: number; train_id?: string; station_id?: string; date?: string } = {}
  ): Promise<TimetableList> {
    return apiClient.get<TimetableList>(this.baseUrl, { params });
  }

  async getTimetableEntry(entryId: string): Promise<TimetableResponse> {
    return apiClient.get<TimetableResponse>(`${this.baseUrl}/${entryId}`);
  }

  async createTimetableEntry(entry: TimetableEntry): Promise<TimetableResponse> {
    return apiClient.post<TimetableResponse>(this.baseUrl, entry);
  }

  async updateTimetableEntry(entryId: string, entry: Partial<TimetableEntry>): Promise<TimetableResponse> {
    return apiClient.put<TimetableResponse>(`${this.baseUrl}/${entryId}`, entry);
  }

  async deleteTimetableEntry(entryId: string): Promise<void> {
    return apiClient.delete<void>(`${this.baseUrl}/${entryId}`);
  }
}

export const timetableService = new TimetableService();