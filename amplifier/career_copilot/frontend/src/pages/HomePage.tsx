import React from 'react'
import { Link } from 'react-router-dom'
import {
  DocumentTextIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  LightBulbIcon,
  ArrowRightIcon,
  ChartBarIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Resume Parsing',
    description: 'Upload your resume and get AI-powered analysis with structured data extraction',
    icon: DocumentTextIcon,
    href: '/resume',
    color: 'bg-blue-500',
  },
  {
    name: 'Skills Analysis',
    description: 'Identify skill gaps and get personalized learning recommendations',
    icon: AcademicCapIcon,
    href: '/skills',
    color: 'bg-green-500',
  },
  {
    name: 'Job Matching',
    description: 'Find matching job opportunities based on your profile and preferences',
    icon: BriefcaseIcon,
    href: '/jobs',
    color: 'bg-purple-500',
  },
  {
    name: 'Career Advice',
    description: 'Get personalized career coaching and development guidance',
    icon: LightBulbIcon,
    href: '/advice',
    color: 'bg-yellow-500',
  },
]

const stats = [
  { name: 'Skills Analyzed', value: '10,000+', icon: ChartBarIcon },
  { name: 'Career Advice Given', value: '5,000+', icon: LightBulbIcon },
  { name: 'Job Matches Found', value: '25,000+', icon: BriefcaseIcon },
  { name: 'Active Users', value: '2,000+', icon: UserGroupIcon },
]

function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          AI-Powered{' '}
          <span className="text-gradient">Career Development</span>
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
          Transform your career with intelligent resume analysis, skill gap identification, personalized learning paths, and smart job matching.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            to="/resume"
            className="btn btn-primary btn-lg"
          >
            Get Started
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/profile"
            className="btn btn-outline btn-lg"
          >
            View Demo
          </Link>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          Trusted by Career Professionals
        </h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.name} className="text-center">
              <div className="flex justify-center">
                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <p className="mt-4 text-3xl font-bold text-gray-900">{stat.value}</p>
              <p className="mt-1 text-sm text-gray-600">{stat.name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          Everything You Need for Career Success
        </h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <Link
              key={feature.name}
              to={feature.href}
              className="card card-hover p-6 text-center group cursor-pointer"
            >
              <div className="flex justify-center mb-4">
                <div className={`h-12 w-12 ${feature.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors duration-200">
                {feature.name}
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {feature.description}
              </p>
              <div className="mt-4 flex items-center justify-center text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <span className="text-sm font-medium">Learn more</span>
                <ArrowRightIcon className="ml-1 h-4 w-4" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-gray-50 rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
          How It Works
        </h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-primary-600">1</span>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Your Resume</h3>
            <p className="text-gray-600">
              Upload your resume in any format (PDF, DOCX, TXT) and let our AI parse and analyze your experience, skills, and achievements.
            </p>
          </div>
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 bg-secondary-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-secondary-600">2</span>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Get AI Analysis</h3>
            <p className="text-gray-600">
              Receive comprehensive skill gap analysis, career insights, and personalized recommendations tailored to your goals.
            </p>
          </div>
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="h-16 w-16 bg-accent-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-accent-600">3</span>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Find Your Dream Job</h3>
            <p className="text-gray-600">
              Get matched with relevant job opportunities and receive application strategies to help you land your next role.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-12 text-white">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Transform Your Career?
        </h2>
        <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
          Join thousands of professionals who have advanced their careers with AI-powered guidance.
        </p>
        <Link
          to="/resume"
          className="btn bg-white text-primary-600 hover:bg-gray-100 btn-lg font-semibold"
        >
          Start Your Journey
          <ArrowRightIcon className="ml-2 h-5 w-5" />
        </Link>
      </div>
    </div>
  )
}

export default HomePage