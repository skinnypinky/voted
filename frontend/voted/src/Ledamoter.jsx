import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Ledamoter.css'


function Ledamoter() {
    const [ledamoter, setLedamoter] = useState([])
    const [search, setSearch] = useState("")
    const navigate = useNavigate()

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/ledamoter')
            .then(res => res.json())
            .then(data => setLedamoter(data))
    }, [])

    const filtered = ledamoter.filter(l =>
        l.full_name.toLowerCase().includes(search.toLowerCase()) ||
        l.parti_name.toLowerCase().includes(search.toLowerCase()) ||
        l.valkrets_name.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div className="ledamoter-page">
            <input
                className="ledamoter-search"
                type="text"
                placeholder="Sök på namn, parti eller valkrets..."
                value={search}
                onChange={e => setSearch(e.target.value)}
            />
            <div className="ledamoter-table">
                <div className="ledamoter-header">
                    <span>Namn</span>
                    <span>Parti</span>
                    <span>Valkrets</span>
                    <span>Profil</span>
                </div>
                {filtered.map((ledamot, index) => (
                    <div key={ledamot.intressent_id} className="ledamoter-row">
                        <span>{ledamot.full_name}</span>
                        <span>{ledamot.parti_name}</span>
                        <span>{ledamot.valkrets_name}</span>
                        <button className="visa-btn2" onClick={() => navigate(`/ledamoter/${ledamot.intressent_id}`)}>Visa profil</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default Ledamoter
