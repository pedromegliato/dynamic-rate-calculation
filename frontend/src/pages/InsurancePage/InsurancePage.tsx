import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Modal,
  Snackbar,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import CalculationsTable from '../../components/CalculationsTable/CalculationsTable';
import InsuranceForm from '../../components/InsuranceForm/InsuranceForm';
import { InsuranceCalculationRequestData, InsuranceCalculationResponseData } from '../../types/insurance';
import { InsuranceBaseFormData } from '../../validation/insuranceSchema';
import { useThemeContext } from '../../contexts/ThemeContext';
import { useCalculations } from '../../hooks/useCalculations';

const modalStyle = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: { xs: '90%', sm: '80%', md: '70%', lg: '60%' },
  bgcolor: 'background.paper',
  border: '1px solid #ccc',
  boxShadow: 24,
  p: 4,
  maxHeight: '90vh',
  overflowY: 'auto',
};

const InsurancePage: React.FC = () => {
  const { 
    calculations: allCalculations,
    isLoading, 
    error: calculationError,
    fetchCalculations, 
    addCalculation, 
    editCalculation,
    removeCalculation, 
    clearError: clearCalculationError 
  } = useCalculations();
  
  const [editingDataBase, setEditingDataBase] = useState<InsuranceBaseFormData | null>(null);
  const [editingCalculationId, setEditingCalculationId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10); 

  const { mode, toggleTheme } = useThemeContext();

  useEffect(() => {
    fetchCalculations();
  }, [fetchCalculations]);

  useEffect(() => {
      if (!isModalOpen) {
          clearCalculationError();
          setSubmitError(null);
      }
  }, [isModalOpen, clearCalculationError]);

  const mapResponseToBaseFormData = (calc: InsuranceCalculationResponseData | null): InsuranceBaseFormData | null => {
    if (!calc) return null;
    const defaultDeductible = 0.10; 
    return {
      make: calc.car_make,
      model: calc.car_model,
      year: calc.car_year,
      value: calc.car_value,
      deductible_percentage: defaultDeductible,
      broker_fee: calc.broker_fee,
    };
  };

  const handleOpenModal = (calculation: InsuranceCalculationResponseData | null = null) => {
    setEditingDataBase(mapResponseToBaseFormData(calculation)); 
    setEditingCalculationId(calculation ? calculation.id : null);
    setSubmitError(null);
    clearCalculationError(); 
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingDataBase(null); 
    setEditingCalculationId(null);
  };

  const handleShowSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleCloseSnackbar = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const handleFormSubmit = async (data: InsuranceCalculationRequestData) => { 
    setIsSubmitting(true);
    setSubmitError(null);
    clearCalculationError();
    try {
      const requestData = data;

      if (editingCalculationId) { 
        await editCalculation(editingCalculationId, requestData); 
        handleShowSnackbar('Cálculo atualizado com sucesso!', 'success');
      } else {
        await addCalculation(requestData);
        handleShowSnackbar('Cálculo criado com sucesso!', 'success');
        setPage(0); 
      }
      handleCloseModal();
    } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao salvar.';
        setSubmitError(errorMessage);
        handleShowSnackbar(errorMessage, 'error'); 
        console.error("Erro no submit do formulário:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCalculation = async (id: string) => {
    if (window.confirm('Tem certeza que deseja deletar este cálculo?')) {
      await removeCalculation(id);
      const remainingOnPage = allCalculations.filter(c => c.id !== id).slice(page * rowsPerPage, (page * rowsPerPage) + rowsPerPage).length;
      const totalPagesAfterDelete = Math.ceil((allCalculations.length - 1) / rowsPerPage);
      if (remainingOnPage === 0 && page > 0 && page >= totalPagesAfterDelete) {
          setPage(page - 1);
      }
      if (calculationError) {
          handleShowSnackbar(calculationError, 'error');
      } else {
          handleShowSnackbar('Cálculo deletado com sucesso!', 'success');
      }
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const paginatedCalculations = allCalculations.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const currentEditingCalculation = editingCalculationId 
      ? allCalculations.find(calc => calc.id === editingCalculationId)
      : null;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cálculos de Seguro Automotivo
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenModal()}
            sx={{ mr: 1 }}
          >
            Novo Cálculo
          </Button>
          <Tooltip title={mode === 'light' ? "Mudar para modo escuro" : "Mudar para modo claro"}>
            <IconButton onClick={toggleTheme} color="inherit">
              {mode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {calculationError && !isModalOpen && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={clearCalculationError}> 
            {calculationError}
        </Alert>
      )}

      <CalculationsTable
        calculations={paginatedCalculations}
        onEdit={handleOpenModal}
        onDelete={handleDeleteCalculation}
        isLoading={isLoading}
        page={page}
        rowsPerPage={rowsPerPage}
        totalRows={allCalculations.length}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />

      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        aria-labelledby="insurance-modal-title"
        aria-describedby="insurance-modal-description"
      >
        <Box sx={modalStyle}>
          {isModalOpen && (
            <InsuranceForm
              initialData={editingDataBase} 
              initialAddressData={currentEditingCalculation?.registration_location ?? null}
              onSubmit={handleFormSubmit}
              isSubmitting={isSubmitting}
              submitError={submitError} 
              onCancel={handleCloseModal}
            />
          )}
        </Box>
      </Modal>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default InsurancePage; 