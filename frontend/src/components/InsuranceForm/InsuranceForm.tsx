import React, { useEffect, useState, useCallback } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Box,
  TextField,
  Button,
  Grid,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { 
    insuranceBaseSchema, 
    addressSchema,
    InsuranceBaseFormData, 
    AddressFormData,
} from '../../validation/insuranceSchema';
import { fetchAddressFromCEP } from '../../services/cepService';
import { Address, InsuranceCalculationRequestData } from '../../types/insurance';
import { formatCep } from '../../utils/formatters';

interface InsuranceFormProps {
  initialData?: InsuranceBaseFormData | null;
  initialAddressData?: Address | null;
  onSubmit: (data: InsuranceCalculationRequestData) => Promise<void>;
  isSubmitting: boolean;
  submitError: string | null;
  onCancel?: () => void;
}

const initialAddressState: AddressFormData = {
    street: '',
    number: '',
    complement: '',
    neighborhood: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'BR',
};

const InsuranceFormComponent: React.FC<InsuranceFormProps> = ({ initialData, initialAddressData, onSubmit, isSubmitting, submitError, onCancel }) => {
  const {
    control: baseControl,
    handleSubmit: handleBaseSubmit,
    reset: resetBaseForm,
    formState: { errors: baseErrors, isValid: isBaseValid, dirtyFields: baseDirtyFields },
  } = useForm<InsuranceBaseFormData>({
    resolver: zodResolver(insuranceBaseSchema),
    mode: 'onChange',
    defaultValues: initialData || { 
      make: '',
      model: '',
      year: new Date().getFullYear(),
      value: 0,
      deductible_percentage: 0.10,
      broker_fee: 0,
    },
  });

  const [includeAddress, setIncludeAddress] = useState<boolean>(false);
  const [addressData, setAddressData] = useState<Address | null>(null);
  const [addressErrors, setAddressErrors] = useState<Partial<Record<keyof AddressFormData, string>>>({});
  const [isCepLoading, setIsCepLoading] = useState<boolean>(false);
  const [cepError, setCepError] = useState<string | null>(null);
  const [addressDirtyFields, setAddressDirtyFields] = useState<Partial<Record<keyof AddressFormData, boolean>>>({});
  const [addressFieldsEnabled, setAddressFieldsEnabled] = useState<boolean>(false);
  const [cepDebounceTimeout, setCepDebounceTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleCepBlur = useCallback(async (cepValue?: string) => {
    const cepToSearch = cepValue || addressData?.postal_code;
    const currentAddressData = addressData; 

    setCepError(null);
    setAddressErrors({});

    if (!cepToSearch || cepToSearch.replace(/\D/g, '').length !== 8) {
        setAddressFieldsEnabled(false); 
        if (cepToSearch) {
             setCepError("Formato de CEP inválido.");
        }
        setAddressData(prev => prev ? { ...initialAddressState, postal_code: cepToSearch || '' } : null);
        return; 
    }
    
    if (cepDebounceTimeout) clearTimeout(cepDebounceTimeout);
    setIsCepLoading(true);
    const fetchedAddress: AddressFormData | null = await fetchAddressFromCEP(cepToSearch);
    setIsCepLoading(false);

    if (fetchedAddress) {
        const dirtiedFields = Object.keys(fetchedAddress).reduce((acc, key) => {
            if (key !== 'number' && key !== 'complement' && (fetchedAddress as any)[key] && 
                (!currentAddressData || (fetchedAddress as any)[key] !== (currentAddressData as any)[key])) {
                acc[key as keyof AddressFormData] = true;
            }
            return acc;
        }, {} as Partial<Record<keyof AddressFormData, boolean>>);

        setAddressData(prev => ({ 
            ...(fetchedAddress as Address),
            postal_code: cepToSearch, 
            number: currentAddressData?.number || '',
            complement: currentAddressData?.complement || '',
        }));
        setAddressDirtyFields(prev => ({...prev, ...dirtiedFields}));
        setAddressFieldsEnabled(true); 
    } else {
        setCepError("CEP não encontrado ou inválido.");
        setAddressFieldsEnabled(false); 
        setAddressData(prev => prev ? { ...initialAddressState, postal_code: cepToSearch } : null);
    }
    
  }, [addressData, cepDebounceTimeout]); 

  const handleAddressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    const fieldName = name as keyof AddressFormData;

    let formattedValue = value;
    let cepForDebounce: string | null = null;

    if (fieldName === 'postal_code') {
      formattedValue = formatCep(value); 
      
      if (cepDebounceTimeout) clearTimeout(cepDebounceTimeout);
      setCepError(null); 
      setAddressFieldsEnabled(false); 
      setAddressData(prev => ({ ...initialAddressState, postal_code: formattedValue }));

      const currentCepDigits = formattedValue.replace(/\D/g, '');
      if (currentCepDigits.length === 8) { 
          cepForDebounce = formattedValue;
      } else {
           setAddressErrors(prev => ({ postal_code: prev.postal_code })); 
      }
    } else {
         setAddressData(prev => ({
            ...(prev || initialAddressState), 
            [fieldName]: formattedValue,
        }));
        setAddressDirtyFields(prev => ({ ...prev, [fieldName]: true }));
        if (addressErrors[fieldName]) {
            setAddressErrors(prev => ({ ...prev, [fieldName]: undefined }));
        }
    }

    if (cepForDebounce) {
         const timeoutId = setTimeout(() => {
            handleCepBlur(cepForDebounce as string); 
         }, 1500); 
         setCepDebounceTimeout(timeoutId);
    }
  };

  useEffect(() => {
    const hasInitialAddress = !!initialAddressData;
    
    resetBaseForm(initialData || {
        make: '',
        model: '',
        year: new Date().getFullYear(),
        value: 0,
        deductible_percentage: 0.10,
        broker_fee: 0,
    });
    
    const formattedInitialAddress = initialAddressData 
        ? { ...initialAddressData, postal_code: formatCep(initialAddressData.postal_code) } 
        : null;

    setIncludeAddress(hasInitialAddress);
    setAddressData(formattedInitialAddress); 
    setAddressErrors({}); 
    setCepError(null);
    setAddressDirtyFields({});
    const initialAddressIsValid = hasInitialAddress && addressSchema.safeParse(initialAddressData).success;
    setAddressFieldsEnabled(initialAddressIsValid); 

  }, [initialData, initialAddressData, resetBaseForm]);

  const handleAccordionChange = (event: React.SyntheticEvent, isExpanded: boolean) => {
    setIncludeAddress(isExpanded);
    if (!isExpanded) {
      setAddressData(null);
      setAddressErrors({}); 
      setCepError(null);
      setAddressDirtyFields({});
      setAddressFieldsEnabled(false);
    } else {
       const currentAddress = addressData || initialAddressState;
       setAddressData(currentAddress); 
       const currentCepValid = addressSchema.pick({postal_code: true}).safeParse(currentAddress).success;
       setAddressFieldsEnabled(currentCepValid); 
       if (currentCepValid && currentAddress?.postal_code && !isCepLoading) {
            handleCepBlur(currentAddress.postal_code);
       }
    }
  };

  useEffect(() => {
    return () => {
      if (cepDebounceTimeout) clearTimeout(cepDebounceTimeout);
    };
  }, [cepDebounceTimeout]);

  const validateAddress = useCallback((): { isValid: boolean; errors: Partial<Record<keyof AddressFormData, string>> } => {
    const currentErrors: Partial<Record<keyof AddressFormData, string>> = {};
    if (!includeAddress) return { isValid: true, errors: currentErrors }; 
    if (!addressData) { 
        currentErrors.postal_code = "CEP é obrigatório";
        return { isValid: false, errors: currentErrors };
    } 

    const cepResult = addressSchema.pick({ postal_code: true }).safeParse(addressData);
    if (!cepResult.success) {
        currentErrors.postal_code = cepResult.error.errors[0]?.message || "CEP inválido";
        return { isValid: false, errors: currentErrors };
    }
    
    const fullAddressResult = addressSchema.safeParse(addressData);
    if (!fullAddressResult.success) {
      fullAddressResult.error.errors.forEach(err => {
        if (err.path.length > 0) {
          currentErrors[err.path[0] as keyof AddressFormData] = err.message;
        }
      });
      return { isValid: false, errors: currentErrors };
    }

    return { isValid: true, errors: currentErrors };
  }, [includeAddress, addressData]); 


  const handlePrepareSubmit = (baseData: InsuranceBaseFormData) => {
    const validationResult = validateAddress(); 
    setAddressErrors(validationResult.errors);

    if (!validationResult.isValid) {
        return; 
    }
    
    let addressRequestData: Address | null = null;
    if (includeAddress && addressData) {
        addressRequestData = {
            street: addressData.street,
            number: addressData.number,
            complement: addressData.complement ? addressData.complement : undefined,
            neighborhood: addressData.neighborhood,
            city: addressData.city,
            state: addressData.state,
            postal_code: addressData.postal_code.replace(/\D/g, ''), 
            country: addressData.country,
        };
    }

    const finalData: InsuranceCalculationRequestData = {
      make: baseData.make,
      model: baseData.model,
      year: Number(baseData.year),
      value: Number(baseData.value), 
      deductible_percentage: Number(baseData.deductible_percentage),
      broker_fee: Number(baseData.broker_fee),
      registration_location: addressRequestData,
    };
    onSubmit(finalData);
  };

  const isFormDirty = Object.keys(baseDirtyFields).length > 0 || (includeAddress && Object.keys(addressDirtyFields).length > 0);
  const isAddressCurrentlyValid = !includeAddress || (includeAddress && Object.keys(addressErrors).length === 0 && !cepError);
  const isFormCurrentlyValid = isBaseValid && isAddressCurrentlyValid;
  const canSubmit = !isSubmitting && (isFormCurrentlyValid && (isFormDirty || !!initialData));

  const hasAddressError = (field: keyof AddressFormData): boolean => !!addressErrors[field];
  const getAddressError = (field: keyof AddressFormData): string | undefined => addressErrors[field];

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {initialData ? 'Editar Cálculo' : 'Novo Cálculo de Seguro'}
      </Typography>
      <Box component="form" onSubmit={handleBaseSubmit(handlePrepareSubmit)} noValidate sx={{ mt: 1 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Controller
              name="make"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Marca"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.make}
                  helperText={baseErrors.make?.message}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Controller
              name="model"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Modelo"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.model}
                  helperText={baseErrors.model?.message}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Controller
              name="year"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Ano"
                  type="number"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.year}
                  helperText={baseErrors.year?.message}
                  InputLabelProps={{ shrink: true }}
                  value={field.value ?? ''}
                  onChange={(e) => field.onChange(e.target.value === '' ? undefined : parseInt(e.target.value, 10))}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Controller
              name="value"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Valor (R$)"
                  type="number"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.value}
                  helperText={baseErrors.value?.message}
                  InputLabelProps={{ shrink: true }}
                  value={field.value ?? ''}
                  onChange={(e) => field.onChange(e.target.value === '' ? undefined : parseFloat(e.target.value))}
                  InputProps={{ inputProps: { step: 0.01, min: 0 } }}
                />
              )}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Controller
              name="deductible_percentage"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Franquia (%)"
                  type="number"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.deductible_percentage}
                  helperText={baseErrors.deductible_percentage?.message || "Ex: 0.10 para 10%"}
                  InputLabelProps={{ shrink: true }}
                  value={field.value ?? ''}
                  onChange={(e) => field.onChange(e.target.value === '' ? undefined : parseFloat(e.target.value))}
                  InputProps={{ inputProps: { step: 0.01, min: 0, max: 1 } }}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <Controller
              name="broker_fee"
              control={baseControl}
              render={({ field }) => (
                <TextField
                  {...field}
                  required
                  fullWidth
                  label="Taxa Corretor (R$)"
                  type="number"
                  size="small"
                  disabled={isSubmitting}
                  error={!!baseErrors.broker_fee}
                  helperText={baseErrors.broker_fee?.message}
                  InputLabelProps={{ shrink: true }}
                  value={field.value ?? ''}
                  onChange={(e) => field.onChange(e.target.value === '' ? undefined : parseFloat(e.target.value))}
                  InputProps={{ inputProps: { step: 0.01, min: 0 } }}
                />
              )}
            />
          </Grid>

          <Grid item xs={12}>
            <Accordion 
                expanded={includeAddress} 
                onChange={handleAccordionChange}
                sx={{ 
                    border: '1px solid', 
                    borderColor: 'divider',
                    '&:before': { display: 'none' },
                    bgcolor: 'transparent',
                    transition: (theme) => theme.transitions.create('margin', {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.leavingScreen,
                    }),
                    ...(!includeAddress && {
                        mb: 0,
                    }),
                    ...(includeAddress && {
                        mb: 2,
                    }),
                }}
                disableGutters
                elevation={0}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="address-content"
                id="address-header"
              >
                <Typography>Endereço de Registro (Opcional para GIS)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {includeAddress && (
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={3}>
                            <TextField 
                            name="postal_code"
                            fullWidth 
                            label="CEP" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading} 
                            error={hasAddressError('postal_code') || !!cepError}
                            helperText={getAddressError('postal_code') || cepError}
                            value={addressData?.postal_code ?? ''} 
                            onChange={handleAddressChange} 
                            onBlur={() => handleCepBlur()} 
                            InputProps={{ endAdornment: isCepLoading ? <CircularProgress size={20}/> : null }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={7}> 
                            <TextField 
                            name="street"
                            fullWidth 
                            label="Rua" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('street')} 
                            helperText={getAddressError('street')} 
                            value={addressData?.street ?? ''} 
                            onChange={handleAddressChange}
                            InputLabelProps={{ shrink: !!addressData?.street }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={2}>
                            <TextField 
                            name="number"
                            fullWidth 
                            label="Número" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('number')} 
                            helperText={getAddressError('number')} 
                            value={addressData?.number ?? ''} 
                            onChange={handleAddressChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <TextField 
                            name="complement"
                            fullWidth 
                            label="Complemento" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('complement')} 
                            helperText={getAddressError('complement')} 
                            value={addressData?.complement ?? ''} 
                            onChange={handleAddressChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={8}>
                            <TextField 
                            name="neighborhood"
                            fullWidth 
                            label="Bairro" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('neighborhood')} 
                            helperText={getAddressError('neighborhood')} 
                            value={addressData?.neighborhood ?? ''} 
                            onChange={handleAddressChange}
                            InputLabelProps={{ shrink: !!addressData?.neighborhood }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={8}>
                            <TextField 
                            name="city"
                            fullWidth 
                            label="Cidade" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('city')} 
                            helperText={getAddressError('city')} 
                            value={addressData?.city ?? ''} 
                            onChange={handleAddressChange}
                            InputLabelProps={{ shrink: !!addressData?.city }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <TextField 
                            name="state"
                            fullWidth 
                            label="Estado (UF)" 
                            size="small" 
                            disabled={isSubmitting || isCepLoading || !addressFieldsEnabled}
                            error={hasAddressError('state')} 
                            helperText={getAddressError('state')} 
                            value={addressData?.state ?? ''} 
                            onChange={handleAddressChange}
                            InputLabelProps={{ shrink: !!addressData?.state }}
                            inputProps={{ maxLength: 2 }}
                            />
                        </Grid>
                    </Grid>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>

        {submitError && (
          <Alert severity="error" sx={{ mt: 2 }}>{submitError}</Alert>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
          {onCancel && (
            <Button onClick={onCancel} sx={{ mr: 1 }} disabled={isSubmitting} color="inherit">
              Cancelar
            </Button>
          )}
          <Button
            type="submit"
            variant="contained"
            disabled={!canSubmit}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
          >
            {isSubmitting ? 'Calculando...' : (initialData ? 'Salvar Alterações' : 'Calcular Seguro')}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

const InsuranceForm = React.memo(InsuranceFormComponent);

export default InsuranceForm;