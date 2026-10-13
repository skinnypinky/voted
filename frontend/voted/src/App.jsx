import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './Navbar'
import Home from './Home'
import Search from './Search'
import Votering from './Votering'
import Ledamoter from './Ledamoter'


function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/search/:votering_id" element={<Votering />} />
        <Route path="/ledamoter" element={<Ledamoter />} />
      </Routes>
    </Router>
  )
}

export default App