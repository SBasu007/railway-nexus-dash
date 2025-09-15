import apiClient from './apiClient';
import { Scenario, ScenarioList, ScenarioResponse } from './types';

class ScenarioService {
  private baseUrl = '/api/scenarios';

  async getScenarios(
    params: { skip?: number; limit?: number; status?: string } = {}
  ): Promise<ScenarioList> {
    return apiClient.get<ScenarioList>(this.baseUrl, { params });
  }

  async getScenario(scenarioId: string): Promise<ScenarioResponse> {
    return apiClient.get<ScenarioResponse>(`${this.baseUrl}/${scenarioId}`);
  }

  async createScenario(scenario: Scenario): Promise<ScenarioResponse> {
    return apiClient.post<ScenarioResponse>(this.baseUrl, scenario);
  }

  async updateScenario(scenarioId: string, scenario: Partial<Scenario>): Promise<ScenarioResponse> {
    return apiClient.put<ScenarioResponse>(`${this.baseUrl}/${scenarioId}`, scenario);
  }

  async deleteScenario(scenarioId: string): Promise<void> {
    return apiClient.delete<void>(`${this.baseUrl}/${scenarioId}`);
  }
}

export const scenarioService = new ScenarioService();