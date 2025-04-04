import { createTheme, ThemeOptions } from '@mui/material/styles';
import { ptBR } from '@mui/material/locale'; 

const commonThemeOptions: ThemeOptions = {
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  shape: {
    borderRadius: 8, 
  },

};

export const lightTheme = createTheme(
  {
    ...commonThemeOptions,
    palette: {
      mode: 'light',
      primary: {
        main: '#1976d2', 
      },
      secondary: {
        main: '#dc004e', 
      },
      background: {
        default: '#f4f6f8', 
        paper: '#ffffff',
      },
    },
  },
  ptBR 
);

export const darkTheme = createTheme(
  {
    ...commonThemeOptions,
    palette: {
      mode: 'dark',
      primary: {
        main: '#64b5f6', 
      },
      secondary: {
        main: '#f48fb1', 
      },
      background: {
        default: '#1f1f1f', 
        paper: '#2d2d2d',  
      },
      text: {
        primary: '#e0e0e0',
        secondary: '#a0a0a0',
      },
    },
  },
  ptBR
);