import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Monitor, Home } from 'lucide-react';

export default function Layout() {
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: Home },
    { name: 'Equipamentos', path: '/computadores', icon: Monitor },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
      
      <header className="glass-panel" style={{ 
        margin: '1rem 2rem', 
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'sticky',
        top: '1rem',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* O logo precisa estar dentro da pasta frontend/public/logo.png */}
          <img src="/logo.png" alt="Logo Ambev Disfonte" style={{ height: '40px', objectFit: 'contain' }} />
        </div>

        <nav style={{ display: 'flex', gap: '1.5rem' }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                  color: isActive ? 'var(--accent-color)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 600 : 500,
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={18} />
                {link.name}
              </Link>
            )
          })}
        </nav>
      </header>

      <main className="container main-content animate-fade-in">
        <Outlet />
      </main>

      <footer style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        borderTop: '1px solid var(--border-color)',
        color: 'var(--text-secondary)',
        fontSize: '0.85rem'
      }}>
        <p>&copy; {new Date().getFullYear()} Desenvolvido por <strong>Gabriel Nunes (TI)</strong>. Todos os direitos reservados.</p>
        <p style={{ opacity: 0.5 }}>Disfonte Distribuidora de Bebidas</p>
      </footer>
    </div>
  );
}
