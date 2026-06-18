import React, { useState, useEffect } from 'react';
import { Search, Plus, Monitor, Cpu, Database, HardDrive, Edit2, Trash2, Wrench, Clock } from 'lucide-react';
import Modal from '../components/Modal';
import api from '../api';

export default function Computadores() {
  const [computadores, setComputadores] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  
  const [modalState, setModalState] = useState({ type: null, data: null }); 
  const closeModal = () => setModalState({ type: null, data: null });
  const openModal = (type, data = null) => setModalState({ type, data });

  const [formData, setFormData] = useState({});

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const carregarComputadores = async () => {
    try {
      setLoading(true);
      const response = await api.get('/computadores/');
      setComputadores(response.data);
    } catch (error) {
      console.error("Erro ao carregar computadores", error);
      alert("Erro ao conectar com o backend. O servidor Django está rodando na porta 8000?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarComputadores();
  }, []);

  const handleCadastrar = async (e) => {
    e.preventDefault();
    if (computadores.find(c => c.hostname.toUpperCase() === formData.hostname.toUpperCase())) {
      alert('Computador já cadastrado!');
      return;
    }
    try {
      await api.post('/computadores/', {
        hostname: formData.hostname.toUpperCase(),
        modelo: formData.tipo === 'desktop' ? 'Desktop' : formData.modelo,
        setor: formData.setor,
        responsavel: formData.responsavel,
        specs: { ram: formData.ram, ssd: formData.ssd, processador: formData.processador }
      });
      await carregarComputadores();
      closeModal();
    } catch (error) {
      console.error("Erro ao cadastrar", error);
      alert("Falha ao cadastrar no backend.");
    }
  };

  const handleEditar = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/computadores/${modalState.data.id}/`, {
        hostname: formData.hostname.toUpperCase(),
        modelo: formData.tipo === 'desktop' ? 'Desktop' : formData.modelo,
        setor: formData.setor,
        responsavel: formData.responsavel,
        specs: { ram: formData.ram, ssd: formData.ssd, processador: formData.processador }
      });
      await carregarComputadores();
      closeModal();
    } catch (error) {
      console.error("Erro ao editar", error);
      alert("Falha ao editar no backend.");
    }
  };

  const handleExcluir = async (pc) => {
    if (window.confirm(`Tem certeza que deseja excluir '${pc.hostname}'?`)) {
      try {
        await api.delete(`/computadores/${pc.id}/`);
        await carregarComputadores();
      } catch (error) {
        console.error("Erro ao excluir", error);
        alert("Falha ao excluir no backend.");
      }
    }
  };

  const handleRegistrarManutencao = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/computadores/${modalState.data.id}/manutencoes/`, {
        tipo: formData.tipoManutencao,
        descricao: formData.descricao,
        tecnico: formData.tecnico
      });
      await carregarComputadores();
      closeModal();
    } catch (error) {
      console.error("Erro ao registrar manutenção", error);
      alert("Falha ao registrar manutenção no backend.");
    }
  };

  const handleOpenEdit = (pc) => {
    setFormData({
      hostname: pc.hostname,
      tipo: pc.modelo === 'Desktop' ? 'desktop' : 'notebook',
      modelo: pc.modelo === 'Desktop' ? '' : pc.modelo,
      setor: pc.setor,
      responsavel: pc.responsavel,
      ram: pc.specs.ram,
      ssd: pc.specs.ssd,
      processador: pc.specs.processador
    });
    openModal('EDICAO', pc);
  };

  const handleOpenManutencao = (pc) => {
    setFormData({ tipoManutencao: 'Manutenção', descricao: '', tecnico: '' });
    openModal('MANUTENCAO', pc);
  };

  const filtered = computadores.filter(c => 
    c.hostname.toLowerCase().includes(search.toLowerCase()) ||
    c.setor.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Gestão de Equipamentos</h1>
          <p>Cadastre, edite e acompanhe o histórico dos PCs.</p>
        </div>
        <button className="btn btn-primary" onClick={() => {
          setFormData({ tipo: 'desktop', modelo: '' });
          openModal('CADASTRO');
        }}>
          <Plus size={18} /> Cadastrar Computador
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '2rem' }}>
        
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="input-group" style={{ flex: 1, margin: 0 }}>
            <div style={{ position: 'relative' }}>
              <Search style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} size={18} />
              <input 
                type="text" 
                className="input-field" 
                placeholder="Buscar por hostname ou setor..." 
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ width: '100%', paddingLeft: '2.5rem', boxSizing: 'border-box' }}
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            Carregando do banco de dados...
          </div>
        ) : (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {filtered.map(pc => (
                <div key={pc.id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ padding: '0.5rem', backgroundColor: 'rgba(59, 130, 246, 0.2)', borderRadius: '8px' }}>
                        <Monitor size={20} color="var(--accent-color)" />
                      </div>
                      <div>
                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginRight: '0.5rem' }}>#{pc.id}</span>
                          {pc.hostname}
                        </h3>
                        <span className="badge badge-info" style={{ marginTop: '0.25rem', display: 'inline-block' }}>{pc.setor}</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-secondary" style={{ padding: '0.4rem' }} onClick={() => handleOpenEdit(pc)} title="Editar">
                        <Edit2 size={14} />
                      </button>
                      <button className="btn btn-secondary" style={{ padding: '0.4rem', color: 'var(--danger-color)' }} onClick={() => handleExcluir(pc)} title="Excluir">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Cpu size={16} /> {pc.specs?.processador}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Database size={16} /> {pc.specs?.ram}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <HardDrive size={16} /> {pc.specs?.ssd}
                    </div>
                  </div>

                  <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '0.85rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Resp: </span>
                      <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{pc.responsavel}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-secondary" style={{ padding: '0.4rem 0.6rem', fontSize: '0.8rem' }} onClick={() => openModal('HISTORICO', pc)}>
                        <Clock size={14} /> Histórico ({pc.historico ? pc.historico.length : 0})
                      </button>
                      <button className="btn btn-primary" style={{ padding: '0.4rem 0.6rem', fontSize: '0.8rem' }} onClick={() => handleOpenManutencao(pc)}>
                        <Wrench size={14} /> Manutenção
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                Nenhum computador cadastrado.
              </div>
            )}
          </>
        )}
      </div>

      <Modal isOpen={modalState.type === 'CADASTRO' || modalState.type === 'EDICAO'} 
             onClose={closeModal} 
             title={modalState.type === 'CADASTRO' ? 'Novo Computador' : `Editar ${modalState.data?.hostname}`}>
        <form onSubmit={modalState.type === 'CADASTRO' ? handleCadastrar : handleEditar}>
          <div className="input-group">
            <label>Hostname</label>
            <input type="text" className="input-field" name="hostname" required value={formData.hostname || ''} onChange={handleFormChange} disabled={modalState.type === 'EDICAO'} />
          </div>
          <div className="input-group">
            <label>Tipo</label>
            <select className="input-field" name="tipo" value={formData.tipo || 'desktop'} onChange={handleFormChange} style={{ backgroundColor: 'rgba(0,0,0,0.2)' }}>
              <option value="desktop">Desktop</option>
              <option value="notebook">Notebook</option>
            </select>
          </div>
          {formData.tipo === 'notebook' && (
            <div className="input-group">
              <label>Modelo do Notebook</label>
              <input type="text" className="input-field" name="modelo" required value={formData.modelo || ''} onChange={handleFormChange} />
            </div>
          )}
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="input-group" style={{ flex: 1 }}>
              <label>Setor</label>
              <input type="text" className="input-field" name="setor" required value={formData.setor || ''} onChange={handleFormChange} />
            </div>
            <div className="input-group" style={{ flex: 1 }}>
              <label>Responsável</label>
              <input type="text" className="input-field" name="responsavel" required value={formData.responsavel || ''} onChange={handleFormChange} />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="input-group" style={{ flex: 1 }}>
              <label>RAM</label>
              <input type="text" className="input-field" name="ram" placeholder="Ex: 16GB" required value={formData.ram || ''} onChange={handleFormChange} />
            </div>
            <div className="input-group" style={{ flex: 1 }}>
              <label>SSD/HD</label>
              <input type="text" className="input-field" name="ssd" placeholder="Ex: 512GB SSD" required value={formData.ssd || ''} onChange={handleFormChange} />
            </div>
          </div>
          <div className="input-group">
            <label>Processador</label>
            <input type="text" className="input-field" name="processador" placeholder="Ex: Intel i5-12400" required value={formData.processador || ''} onChange={handleFormChange} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
            <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancelar</button>
            <button type="submit" className="btn btn-primary">Salvar</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={modalState.type === 'MANUTENCAO'} onClose={closeModal} title={`Registrar Manutenção: ${modalState.data?.hostname}`}>
        <form onSubmit={handleRegistrarManutencao}>
          <div className="input-group">
            <label>Tipo de Registro</label>
            <select className="input-field" name="tipoManutencao" required value={formData.tipoManutencao || 'Manutenção'} onChange={handleFormChange} style={{ backgroundColor: 'rgba(0,0,0,0.2)' }}>
              <option value="Manutenção">Manutenção</option>
              <option value="Upgrade">Upgrade</option>
              <option value="Formatação">Formatação</option>
              <option value="Troca de peça">Troca de peça</option>
              <option value="Outro">Outro</option>
            </select>
          </div>
          <div className="input-group">
            <label>Descrição</label>
            <textarea className="input-field" name="descricao" rows={3} required value={formData.descricao || ''} onChange={handleFormChange}></textarea>
          </div>
          <div className="input-group">
            <label>Técnico Responsável</label>
            <input type="text" className="input-field" name="tecnico" required value={formData.tecnico || ''} onChange={handleFormChange} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
            <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancelar</button>
            <button type="submit" className="btn btn-primary">Salvar Registro</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={modalState.type === 'HISTORICO'} onClose={closeModal} title={`Histórico: ${modalState.data?.hostname}`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {modalState.data?.historico?.length === 0 && (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>Sem registros de manutenção.</p>
          )}
          {modalState.data?.historico?.map((reg, i) => (
            <div key={i} style={{ padding: '1rem', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px', borderLeft: '4px solid var(--accent-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <strong style={{ color: 'var(--text-primary)' }}>{reg.tipo}</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{reg.data}</span>
              </div>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{reg.descricao}</p>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Técnico: {reg.tecnico}</span>
            </div>
          ))}
        </div>
      </Modal>

    </div>
  );
}
