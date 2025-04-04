import React from 'react';
import InsurancePage from './pages/InsurancePage/InsurancePage';
import { CustomThemeProvider } from './contexts/ThemeContext'; 

function App() {
  return (
    <CustomThemeProvider>
      <InsurancePage />
    </CustomThemeProvider>
  );
}

export default App;
