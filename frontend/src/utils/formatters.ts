/**
 * Formata um valor numérico como moeda brasileira (BRL).
 * Retorna '-' se o valor for undefined ou null.
 */
export const formatCurrency = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return '-';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

/**
 * Formata um valor numérico (0 a 1) como porcentagem.
 * Retorna '-' se o valor for undefined ou null.
 */
export const formatPercentage = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return '-';
  // Ajustado para mostrar 1 casa decimal na porcentagem
  return `${(value * 100).toFixed(1)}%`;
};

/**
 * Formata uma string de data/hora para o locale pt-BR.
 * Retorna a string original se a formatação falhar.
 */
export const formatDateTime = (dateTimeString: string | undefined | null): string => {
  if (!dateTimeString) return '-';
  try {
      return new Date(dateTimeString).toLocaleString('pt-BR');
  } catch {
      return dateTimeString;
  }
}; 

export const formatCep = (cep: string | undefined | null): string => {
  if (!cep) return '';
  return cep.replace(/\D/g, '')
            .replace(/^(\d{5})(\d)/, '$1-$2')
            .slice(0, 9);
};