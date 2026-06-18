import React, { useEffect, useState } from 'react';
import { Monitor, Wrench, Activity, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalComputadores: 0,
    totalManutencoes: 0,
    recentes: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/computadores/');
        const computadores = response.data;
        
        let todasManutencoes = [];
        computadores.forEach(pc => {
          if (pc.historico) {
            pc.historico.forEach(m => {
              todasManutencoes.push({
                ...m,
                computador: pc.hostname
              });
            });
          }
        });

        // Ordenar por data decrescente
        todasManutencoes.sort((a, b) => new Date(b.data) - new Date(a.data));
        
        setStats({
          totalComputadores: computadores.length,
          totalManutencoes: todasManutencoes.length,
          recentes: todasManutencoes.slice(0, 5) // Pegar as 5 mais recentes
        });
      } catch (error) {
        console.error("Erro ao carregar os dados do dashboard", error);
      }
    };
    
    fetchData();
  }, []);

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="glass-panel" style={{ padding: '1.5rem', flex: 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{title}</p>
          <h3 style={{ margin: '0.5rem 0 0 0', fontSize: '2rem' }}>{value}</h3>
        </div>
        <div style={{ 
          padding: '0.75rem', 
          backgroundColor: `${color}20`, 
          color: color, 
          borderRadius: '12px' 
        }}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Visão Geral</h1>
          <p>Resumo das atividades e equipamentos da rede.</p>
        </div>
        <Link to="/computadores" className="btn btn-primary">
          <Monitor size={18} /> Ver Equipamentos
        </Link>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <StatCard title="Total de Computadores" value={stats.totalComputadores} icon={Monitor} color="var(--accent-color)" />
        <StatCard title="Manutenções Realizadas" value={stats.totalManutencoes} icon={Wrench} color="#10b981" />
        <StatCard title="Status do Servidor DB" value="Online" icon={Activity} color="#8b5cf6" />
      </div>

      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <Clock size={20} color="var(--accent-color)" />
          <h3 style={{ margin: 0 }}>Últimas Manutenções</h3>
        </div>
        
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Computador</th>
                <th>Tipo</th>
                <th>Técnico</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {stats.recentes.map((m) => (
                <tr key={m.id}>
                  <td style={{ fontWeight: 500 }}>{m.computador}</td>
                  <td>
                    <span className={`badge ${m.tipo === 'Upgrade' ? 'badge-success' : 'badge-info'}`}>
                      {m.tipo}
                    </span>
                  </td>
                  <td>{m.tecnico}</td>
                  <td>{m.data}</td>
                </tr>
              ))}
              {stats.recentes.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                    Nenhuma manutenção recente.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
