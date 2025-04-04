export interface Address {
  street: string;
  number: string;
  complement?: string;
  neighborhood: string;
  city: string;
  state: string; 
  postal_code: string;
  country: string; 
}

export interface AddressFormData {
  street: string;
  number: string;
  complement?: string | null;
  neighborhood: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface InsuranceCalculationRequestData {
  make: string;
  model: string;
  year: number;
  value: number;
  deductible_percentage: number; 
  broker_fee: number;
  registration_location?: Address | null; 
}

export interface InsuranceCalculationResponseData {
  id: string;
  timestamp: string; 
  car_make: string;
  car_model: string;
  car_year: number;
  car_value: number;
  applied_rate: number;
  calculated_premium: number;
  deductible_value: number;
  policy_limit: number;
  gis_adjustment?: number | null;
  broker_fee: number;
  registration_location?: Address | null; 
} 