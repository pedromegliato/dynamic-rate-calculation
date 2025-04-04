import { useState, useCallback } from 'react';
import { listCalculations, createCalculation, deleteCalculation, updateCalculation } from '../services/apiService';
import { InsuranceCalculationResponseData, InsuranceCalculationRequestData } from '../types/insurance';
import axios from 'axios';

interface UseCalculationsReturn {
  calculations: InsuranceCalculationResponseData[];
  isLoading: boolean;
  error: string | null;
  fetchCalculations: () => Promise<void>;
  addCalculation: (data: InsuranceCalculationRequestData) => Promise<InsuranceCalculationResponseData>; 
  editCalculation: (id: string, data: InsuranceCalculationRequestData) => Promise<InsuranceCalculationResponseData>;
  removeCalculation: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useCalculations = (): UseCalculationsReturn => {
  const [calculations, setCalculations] = useState<InsuranceCalculationResponseData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const fetchCalculations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listCalculations();
      setCalculations(data);
    } catch (err) {
      console.error("Erro no hook useCalculations (fetchCalculations):", err);
      setError('Falha ao carregar cálculos. Verifique a conexão com a API.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addCalculation = useCallback(async (data: InsuranceCalculationRequestData): Promise<InsuranceCalculationResponseData> => {
    setError(null);
    try {
      const newCalculation = await createCalculation(data);

      setCalculations(prev => [newCalculation, ...prev]); 

      return newCalculation;
    } catch (err: unknown) {
      console.error("Erro no hook useCalculations (addCalculation):", err);
      let errorMessage = 'Falha ao criar cálculo.';
       if (axios.isAxiosError(err) && err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const editCalculation = useCallback(async (id: string, data: InsuranceCalculationRequestData): Promise<InsuranceCalculationResponseData> => {
    setError(null);
    try {
      const updatedCalculation = await updateCalculation(id, data);
      // Atualiza o estado local substituindo o cálculo antigo pelo novo
      setCalculations(prev => prev.map(calc => calc.id === id ? updatedCalculation : calc));
      return updatedCalculation;
    } catch (err: unknown) {
       console.error("Erro no hook useCalculations (editCalculation):", err);
      let errorMessage = 'Falha ao atualizar cálculo.';
       if (axios.isAxiosError(err) && err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const removeCalculation = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true); 
    setError(null);
    try {
      await deleteCalculation(id);
      setCalculations(prev => prev.filter(calc => calc.id !== id));
    } catch (err) {
      console.error("Erro no hook useCalculations (removeCalculation):", err);
      setError('Falha ao deletar cálculo.');
    } finally {
        setIsLoading(false);
    }
  }, []); 

  return {
    calculations,
    isLoading,
    error,
    fetchCalculations,
    addCalculation,
    editCalculation,
    removeCalculation,
    clearError,
  };
}; 