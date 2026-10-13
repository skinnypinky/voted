  import { useLocation, useNavigate } from 'react-router-dom'
  import './Search.css'

  function Search() {
    const { state } = useLocation()
    const results = state?.results ?? []
    const selectedValkrets = state?.selectedValkrets
    const selectedUtskott = state?.selectedUtskott
    const navigate = useNavigate()

    return (
        <div className="search-page">
            <h2>Sökresultat</h2>
            <p>{selectedUtskott || 'Alla utskott'} i {selectedValkrets || 'Alla valkretsar'} | {results.length} voteringar hittades</p>
            <div className="search-results-list">
                {results.map((result, index) => (
                    <div key={index} className="search-result-card">
                        <div className="search-result-info">
                            <h3>{result.votering_title || 'okänd'}</h3>
                            <p>{result.rubrik || 'okänd'}</p>
                            <p>{result.date}</p>
                        </div>
                        <button className="visa-btn" onClick={() => navigate(`/search/${result.votering_id}`, { state: { result, selectedValkrets : state?.selectedValkrets }})}>Visa votering</button>
                    </div>
                ))}
            </div>
        </div>
    )
  }

  export default Search