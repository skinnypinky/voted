  import { useLocation } from 'react-router-dom'
  import './Search.css'

  function Search() {
    const { state } = useLocation()
    const results = state?.results ?? []

    return (
        <div className="search-page">
            <h2>Sökresultat</h2>
            <p>{results.length} voteringar hittades</p>
            <div className="results-list">
                {results.map(id => (
                    <div key={id} className="result-card">
                        <div className="result-info">
                            <h3>{id}</h3>
                        </div>
                        <button className="visa-btn">Visa votering</button>
                    </div>
                ))}
            </div>
        </div>
    )
  }

  export default Search