import { z } from 'zod';

const currentYear = new Date().getFullYear();

export const insuranceBaseSchema = z.object({
  make: z.string().min(1, 'Marca é obrigatória'),
  model: z.string().min(1, 'Modelo é obrigatório'),
  year: z.number({
    required_error: "Ano é obrigatório",
    invalid_type_error: "Ano deve ser um número",
  }).int('Ano deve ser um número inteiro')
    .min(1900, 'Ano deve ser 1900 ou posterior')
    .max(currentYear + 1, `Ano não pode ser maior que ${currentYear + 1}`),
  value: z.number({
    required_error: "Valor é obrigatório",
    invalid_type_error: "Valor deve ser um número",
  }).positive('Valor deve ser positivo'),
  deductible_percentage: z.number({
    required_error: "Percentual de franquia é obrigatório",
    invalid_type_error: "Percentual de franquia deve ser um número",
  }).min(0, 'Franquia não pode ser negativa').max(1, 'Franquia não pode ser maior que 1 (100%)'),
  broker_fee: z.number({
    required_error: "Taxa do corretor é obrigatória",
    invalid_type_error: "Taxa do corretor deve ser um número",
  }).min(0, 'Taxa do corretor não pode ser negativa'),
});

export const addressSchema = z.object({
  street: z.string().min(1, 'Rua é obrigatória'),
  number: z.string().min(1, 'Número é obrigatório'),
  complement: z.string().optional(),
  neighborhood: z.string().min(1, 'Bairro é obrigatório'),
  city: z.string().min(1, 'Cidade é obrigatória'),
  state: z.string().length(2, 'Estado deve ter 2 caracteres'),
  postal_code: z.string().min(8, 'CEP inválido').regex(/^\d{5}-?\d{3}$/, "Formato de CEP inválido (XXXXX-XXX ou XXXXXXXX)"),
  country: z.string().length(2, 'País deve ter 2 caracteres').default('BR'),
});

export type InsuranceBaseFormData = z.infer<typeof insuranceBaseSchema>;
export type AddressFormData = z.infer<typeof addressSchema>;

export type FullInsuranceFormData = InsuranceBaseFormData & {
    registration_location: AddressFormData | null;
}; 