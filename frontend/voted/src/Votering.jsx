import { useParams, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './Votering.css'

function Votering() {
    const { state } = useLocation()
    const result = state?.result
    const [summary, setSummary] = useState([])
    const [details, setDetails] = useState([])
    const selectedValkrets = state?.selectedValkrets
    const partyColors = {
        "Socialdemokraterna": '#E8112D',
        'Moderaterna': '#52BDEC',
        'Sverigedemokraterna': '#DDDD00',
        'Centerpartiet': '#009933',
        'Vänsterpartiet': '#82170f',
        'Kristdemokraterna': '#005B99',
        'Liberalerna': '#006AB3',
        'Miljöpartiet': '#83CF39',
        'Övriga partier': '#808080'
    }

    function voteColor(rost) {
        if (rost === 'Ja') return '#00FF00'
        if (rost === 'Nej') return '#FF0000'
        if (rost === 'Avstår') return '#FFFF00'
        if (rost === 'Frånvarande') return '#808080'
        return '#FFFFFF'
    }

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/votering', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                votering_id: result?.votering_id,
                valkrets_id: selectedValkrets ? result?.valkrets_id : null
            })
        })
        .then(res => res.json())
        .then(data => {
            console.log(data)
            setDetails(data.details)
            setSummary(data.summary)
        })
    }, [result])

    const summaryItems = (result?.summary || '')
    .split(/<\/?p>/)
    .map(s => s.trim())
    .filter(Boolean);

    return (
        <div className="votering-page">
            <div className="votering-table">
                <h2>Ledamöter</h2>
                <div className="results-list">
                    {details.map((detail, index) => (
                        <div key={index} className="result-card">
                            <span>{detail.full_name}</span>
                            <span className="parti-badge" style={{ backgroundColor: partyColors[detail.parti_name] || '#999' }}>{detail.parti_name}</span>
                            <span className={voteColor(detail.rost)}>{detail.rost}</span>
                        </div>
                    ))}
                </div>
            </div>
            <div className="votering-table">
                <h2>Sammanfattning</h2>
                <div className="results-list">
                    {summary.map((sum, index) => (
                        <div key={index} className="result-card">
                            <span>{sum.rost}</span>
                            <span>{sum.count}</span>
                        </div>
                    ))}
                </div>
            </div>
            <div className="votering-info">
                <h2>{result?.votering_title || 'okänd'}</h2>
                <p>Valkrets: {result?.valkrets_name || 'Alla valkretsar'}</p>
                <p>Datum: {result?.date}</p>
                <p>Utskott: {result?.utskott || 'okänd'}</p>
                {summaryItems.length > 0 ? (
                    <ul className="summary-list">
                        {summaryItems.map((item, i) => (
                        <li key={i}>{item}</li>
                        ))}
                    </ul>
                    ) : (
                    <p>Ingen sammanfattning tillgänglig</p>
                )}
                <p>Dokument: <a href={result?.url} target="_blank" rel="noopener noreferrer">Öppna på riksdagen.se</a></p>
            </div>
        </div>
    )
}

export default Votering