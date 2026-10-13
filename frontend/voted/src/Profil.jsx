import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './Profil.css'

function Profil() {
    const { intressent_id } = useParams()
    const [profil, setProfil] = useState(null)

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/api/ledamot/${intressent_id}`)
            .then(res => res.json())
            .then(data => setProfil(data))
    }, [intressent_id])

    if (!profil) return <p>Laddar...</p>

    return (
        <div className="profil-page">
            <div className="profil-header">
                {profil.info.image_url && (
                    <img className="profil-bild" src={profil.info.image_url} alt={profil.info.full_name} />
                )}
                <div>
                    <h2>{profil.info.full_name}</h2>
                    <p>{profil.info.parti_name}</p>
                    <p>{profil.info.valkrets_name}</p>
                    {profil.info.birth_year && <p>Född {profil.info.birth_year}</p>}
                </div>
            </div>

            <h3>Röstningsstatistik</h3>
            <div className="profil-stats">
                <div className="stat-box">
                    <span className="stat-value">{profil.stats.narvaro_procent} %</span>
                    <span className="stat-label">Närvaro</span>
                </div>
                <div className="stat-box">
                    <span className="stat-value">{profil.stats.ja}</span>
                    <span className="stat-label">Ja</span>
                </div>
                <div className="stat-box">
                    <span className="stat-value">{profil.stats.nej}</span>
                    <span className="stat-label">Nej</span>
                </div>
                <div className="stat-box">
                    <span className="stat-value">{profil.stats.avstar}</span>
                    <span className="stat-label">Avstår</span>
                </div>
            </div>

            <h3>Senaste voteringar</h3>
            <div className="profil-votes">
                {profil.votes.map(v => (
                    <div key={v.votering_id} className="vote-row">
                        <div>
                            <strong>{v.votering_title || v.notisrubrik}</strong>
                            <p className="vote-meta">{v.date} · {v.utskott || 'Inget utskott'}</p>
                        </div>
                        <span className={`vote-rost rost-${v.rost.toLowerCase()}`}>{v.rost}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default Profil