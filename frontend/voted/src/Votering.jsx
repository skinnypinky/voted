import { useParams, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './Votering.css'

function Votering() {
    const { state } = useLocation()
    const result = state?.result
    const [summary, setSummary] = useState([])
    const [details, setDetails] = useState([])
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
                valkrets_id: result?.valkrets_id
            })
        })
        .then(res => res.json())
        .then(data => {
            setDetails(data.details)
            setSummary(data.summary)
        })
    }, [result])

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
        </div>
    )
}

export default Votering