import { Link } from 'react-router-dom'
import './Navbar.css'

function Navbar() {
    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">Hem</Link>
            <Link to="/ledamoter" className="navbar-link">Ledamöter</Link>
        </nav>
    )
}

export default Navbar