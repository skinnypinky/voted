import './App.css'
import alex from './assets/alex.png'
import { useState, useEffect } from 'react'

function App() {                
  const [constituencies, setConstituencies] = useState([])

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/constituency')
      .then(response => response.json())
      .then(data => setConstituencies(data))
  }, [])
  
  return (
    <div>
      <main>
        <h1>VOTED</h1>
        <img src={alex} />
        <div className="filter-bar">
          <div className="filter-group">
            <label>Valkrets</label>
            <select>
              <option value="">Alla län</option>
              {constituencies.map(c => (<option key={c} value={c}>{c}</option>))}
            </select>
          </div>
          <div className="filter-group">
            <label>Utskott / Kategori</label>
            <select>
              <option>Alla utskott</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Sök efter fråga</label>
            <div className="search-row">
              <input type="" placeholder="Sök..." />
              <button>Sök</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App