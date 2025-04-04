import axios from 'axios';
import { InsuranceCalculationRequestData, InsuranceCalculationResponseData } from '../types/insurance';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/insurance';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Busca todos os cálculos de seguro.
 */
export const listCalculations = async (): Promise<InsuranceCalculationResponseData[]> => {
  try {
    const response = await apiClient.get('/calculations');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar cálculos:", error);
    throw error;
  }
};

/**
 * Cria um novo cálculo de seguro.
 */
export const createCalculation = async (data: InsuranceCalculationRequestData): Promise<InsuranceCalculationResponseData> => {
  try {
    const response = await apiClient.post('/calculate', data);
    return response.data;
  } catch (error) {
    console.error("Erro ao criar cálculo:", error);
    throw error;
  }
};

/**
 * Busca um cálculo de seguro pelo ID.
 */
export const getCalculationById = async (id: string): Promise<InsuranceCalculationResponseData> => {
  try {
    const response = await apiClient.get(`/calculations/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Erro ao buscar cálculo ${id}:`, error);
    throw error;
  }
};

/**
 * Atualiza um cálculo de seguro existente.
 */
export const updateCalculation = async (id: string, data: InsuranceCalculationRequestData): Promise<InsuranceCalculationResponseData> => {
  try {
    const response = await apiClient.patch(`/calculations/${id}`, data);
    return response.data;
  } catch (error) {
    console.error(`Erro ao atualizar cálculo ${id}:`, error);
    throw error; 
  }
};

/**
 * Deleta um cálculo de seguro pelo ID.
 */
export const deleteCalculation = async (id: string): Promise<void> => {
  try {
    await apiClient.delete(`/calculations/${id}`);
  } catch (error) {
    console.error(`Erro ao deletar cálculo ${id}:`, error);
    throw error;
  }
};