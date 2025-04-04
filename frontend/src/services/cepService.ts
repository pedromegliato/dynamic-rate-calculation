import { AddressFormData } from "../validation/insuranceSchema";

/**
 * Busca dados de endereço a partir de um CEP usando a API ViaCEP.
 * @param cep - O CEP (com ou sem máscara).
 * @returns Um objeto AddressFormData ou null se não encontrado/erro.
 */
export const fetchAddressFromCEP = async (cep: string): Promise<AddressFormData | null> => {
  const cleanedCep = cep.replace(/\D/g, '');
  if (cleanedCep.length !== 8) return null;

  try {
    const response = await fetch(`https://viacep.com.br/ws/${cleanedCep}/json/`);
    if (!response.ok) {
      console.error(`Erro na API ViaCEP: ${response.status}`);
      return null;
    }
    const data = await response.json();
    if (data.erro) {
      return null;
    }
    return {
      street: data.logradouro || '',
      number: '', 
      complement: data.complemento || '',
      neighborhood: data.bairro || '',
      city: data.localidade || '',
      state: data.uf || '',
      postal_code: cep,
      country: 'BR',
    };
  } catch (error) {
    console.error("Erro ao buscar CEP:", error);
    return null;
  }
}; 