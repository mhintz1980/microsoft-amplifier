import React from 'react'
import { Routes, Route } from 'react-router-dom'

import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ResumeUploadPage from './pages/ResumeUploadPage'
import ProfilePage from './pages/ProfilePage'
import SkillsAnalysisPage from './pages/SkillsAnalysisPage'
import JobMatchesPage from './pages/JobMatchesPage'
import CareerAdvicePage from './pages/CareerAdvicePage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/resume" element={<ResumeUploadPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/skills" element={<SkillsAnalysisPage />} />
        <Route path="/jobs" element={<JobMatchesPage />} />
        <Route path="/advice" element={<CareerAdvicePage />} />
      </Routes>
    </Layout>
  )
}

export default App