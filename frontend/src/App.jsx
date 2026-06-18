import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Computadores from './pages/Computadores';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="computadores" element={<Computadores />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
