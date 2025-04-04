import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Box,
  Typography,
  Tooltip,
  TablePagination,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import { InsuranceCalculationResponseData } from '../../types/insurance';
import { formatCurrency, formatPercentage } from '../../utils/formatters';
import LoadingIndicator from '../LoadingIndicator/LoadingIndicator';

interface CalculationsTableProps {
  calculations: InsuranceCalculationResponseData[];
  onEdit: (calculation: InsuranceCalculationResponseData) => void;
  onDelete: (id: string) => void;
  onViewDetails?: (calculation: InsuranceCalculationResponseData) => void;
  isLoading?: boolean;
  page: number;
  rowsPerPage: number;
  totalRows: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const CalculationsTableComponent: React.FC<CalculationsTableProps> = ({
  calculations,
  onEdit,
  onDelete,
  onViewDetails,
  isLoading,
  page,
  rowsPerPage,
  totalRows,
  onPageChange,
  onRowsPerPageChange,
}) => {

  return (
    <Paper sx={{ mt: 3, overflow: 'hidden' }}>
      <TableContainer>
        <Table sx={{ minWidth: 650 }} aria-label="tabela de cálculos de seguro">
          <TableHead sx={{ backgroundColor: 'blue.300' }}>
            <TableRow>
              <TableCell>Carro</TableCell>
              <TableCell align="right">Ano</TableCell>
              <TableCell align="right">Valor</TableCell>
              <TableCell align="right">Taxa Aplicada</TableCell>
              <TableCell align="right">Prêmio (Final)</TableCell>
              <TableCell align="right">Valor Franquia</TableCell>
              <TableCell align="right">Limite Apólice</TableCell>
              <TableCell align="center">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ border: 0 }}>
                  <LoadingIndicator />
                </TableCell>
              </TableRow>
            ) : calculations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ border: 0 }}>
                  <Typography>Nenhum cálculo encontrado.</Typography>
                </TableCell>
              </TableRow>
            ) : (
              calculations.map((calc) => (
                <TableRow
                  key={calc.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {calc.car_make} {calc.car_model}
                  </TableCell>
                  <TableCell align="right">{calc.car_year}</TableCell>
                  <TableCell align="right">{formatCurrency(calc.car_value)}</TableCell>
                  <TableCell align="right">{formatPercentage(calc.applied_rate)}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>{formatCurrency(calc.calculated_premium)}</TableCell>
                  <TableCell align="right">{formatCurrency(calc.deductible_value)}</TableCell>
                  <TableCell align="right">{formatCurrency(calc.policy_limit)}</TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                      {onViewDetails && (
                        <Tooltip title="Ver Detalhes">
                          <IconButton size="small" onClick={() => onViewDetails(calc)} color="info">
                            <InfoIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Editar">
                        <IconButton size="small" onClick={() => onEdit(calc)} color="primary">
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Deletar">
                        <IconButton size="small" onClick={() => onDelete(calc.id)} color="error">
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={totalRows}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={onPageChange}
        onRowsPerPageChange={onRowsPerPageChange}
        labelRowsPerPage="Itens por página:"
        labelDisplayedRows={({ from, to, count }) => `${from}–${to} de ${count !== -1 ? count : `mais de ${to}`}`}
      />
    </Paper>
  );
};

const CalculationsTable = React.memo(CalculationsTableComponent);

export default CalculationsTable; 