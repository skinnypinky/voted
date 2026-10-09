  import { useLocation, useNavigate } from 'react-router-dom'
  import './Search.css'

  function Search() {
    const { state } = useLocation()
    const results = state?.results ?? []
    const navigate = useNavigate()

    return (
        <div className="search-page">
            <h2>Sökresultat</h2>
            <p>{results[0]?.utskott || 'okänd'} i {results[3]?.valkrets_name || 'okänd'} | {results.length} voteringar hittades</p>
            <div className="results-list">
                {results.map((result, index) => (
                    <div key={index} className="result-card">
                        <div className="result-info">
                            <h3>{result.votering_id}</h3>
                            <p>{result.date}</p>
                        </div>
                        <button className="visa-btn" onClick={() => navigate(`/search/${result.votering_id}`, { state: { result }})}>Visa votering</button>
                    </div>
                ))}
            </div>
        </div>
    )
  }

  export default Search