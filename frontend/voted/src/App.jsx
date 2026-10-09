import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './Home'
import Search from './Search'
import Votering from './Votering'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/search/:votering_id" element={<Votering />} />
      </Routes>
    </Router>
  )
}

export default App