// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}

// Resume Data Types
export interface PersonalInfo {
  name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  github?: string
}

export interface Skill {
  name: string
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  years_experience?: number
  last_used?: string
  context?: string
  certifications: string[]
}

export interface WorkExperience {
  company: string
  position: string
  location?: string
  start_date: string
  end_date?: string
  is_current: boolean
  description?: string
  achievements: string[]
  skills_used: Skill[]
  team_size?: number
  projects: string[]
}

export interface Education {
  institution: string
  degree: string
  field_of_study: string
  location?: string
  start_date?: string
  end_date?: string
  gpa?: number
  honors: string[]
  relevant_coursework: string[]
  thesis?: string
  activities: string[]
}

export interface ResumeData {
  personal_info: PersonalInfo
  summary?: string
  work_experience: WorkExperience[]
  education: Education[]
  skills: Skill[]
  certifications: any[]
  languages: any[]
  projects: any[]
  volunteer_work: any[]
  interests: string[]
  publications: any[]
  references_available: boolean
  last_updated: string
}

// User Preferences Types
export interface CareerGoals {
  target_roles: string[]
  target_industries: string[]
  target_companies: string[]
  career_level_target?: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'manager' | 'director' | 'executive'
  salary_range?: {
    min: number
    max: number
  }
  locations: string[]
  work_environment?: 'remote' | 'hybrid' | 'on_site' | 'flexible'
  company_size_preference?: 'startup' | 'small' | 'medium' | 'large' | 'enterprise'
  time_to_goal?: number
  priorities: string[]
  deal_breakers: string[]
}

export interface LearningPreferences {
  learning_style?: 'visual' | 'auditory' | 'kinesthetic' | 'reading' | 'mixed'
  preferred_formats: string[]
  time_commitment?: number
  budget?: any
  topics_of_interest: string[]
  certification_goals: string[]
  mentorship_interest: boolean
  group_learning: boolean
}

export interface CommunicationPreferences {
  language: string
  tone: string
  frequency: string
  channels: string[]
  response_time?: string
  feedback_style: string
}

export interface UserPreferences {
  user_id?: string
  created_at: string
  updated_at: string
  career_goals: CareerGoals
  learning_preferences: LearningPreferences
  communication_preferences: CommunicationPreferences
  data_sharing: boolean
  notifications: boolean
  public_profile: boolean
  work_life_balance?: number
  technical_vs_managerial?: number
  risk_tolerance?: number
  custom_preferences: any
}

// Skill Analysis Types
export interface SkillGap {
  skill_name: string
  current_level?: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  required_level: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  priority: 'high' | 'medium' | 'low'
  estimated_learning_time?: string
  recommended_resources: string[]
}

export interface CareerInsight {
  type: string
  title: string
  description: string
  confidence: number
  actionable: boolean
  priority: 'high' | 'medium' | 'low'
  category: string
  data_points: string[]
  created_at: string
}

export interface SkillMarketDemand {
  skill_demand_scores: Record<string, number>
  overall_market_readiness: number
  high_demand_skills: string[]
  assessment_date: string
}

// Job Matching Types
export interface JobMatch {
  job_id: string
  title: string
  company: string
  location: string
  match_score: number
  key_matches: string[]
  skill_gaps: SkillGap[]
  salary_range?: {
    min: number
    max: number
  }
  posted_date?: string
  application_deadline?: string
  status: string
  notes?: string
}

export interface JobMarketAnalysis {
  top_demanded_skills: { skill: string; demand: number }[]
  user_skill_market_value: { skill: string; demand: number }[]
  average_salary: number
  salary_range: { min: number; max: number }
  popular_locations: { location: string; count: number }[]
  total_jobs_analyzed: number
  analysis_date: string
}

export interface ApplicationStrategy {
  strategy: {
    priority: number
    category: string
    description: string
    jobs: any[]
    timeline: string
    actions: string[]
  }[]
  overall_strategy: {
    total_applications_planned: number
    focus_areas: string[]
    success_factors: string[]
  }
  summary: string
  created_at: string
}

// Master Profile Types
export interface MasterProfile {
  profile_id: string
  user_id?: string
  created_at: string
  updated_at: string
  last_analyzed?: string
  resume_data: ResumeData
  user_preferences: UserPreferences
  skill_gaps: SkillGap[]
  career_insights: CareerInsight[]
  job_matches: JobMatch[]
  career_trajectory?: any
  status: 'draft' | 'incomplete' | 'complete' | 'optimized'
  completion_percentage: number
  overall_score?: number
  market_readiness?: number
  profile_views: number
  job_applications: number
  skills_updated: string[]
  goals_achieved: string[]
}

// Learning Plan Types
export interface LearningPlan {
  plan: {
    skill_name: string
    start_month: number
    end_month: number
    priority: string
    required_level: string
    current_level: string
    resources: string[]
    weekly_hours: number
    milestones: string[]
  }[]
  summary: string
  total_skills: number
  time_horizon_months: number
  weekly_commitment: number
  created_at: string
}

// Form Types
export interface ResumeUploadForm {
  file?: File
  resume_text?: string
}

export interface UserPreferencesForm {
  career_goals: Partial<CareerGoals>
  learning_preferences: Partial<LearningPreferences>
  communication_preferences: Partial<CommunicationPreferences>
  work_life_balance?: number
  technical_vs_managerial?: number
  risk_tolerance?: number
}

// UI State Types
export interface LoadingState {
  isLoading: boolean
  message?: string
}

export interface ErrorState {
  hasError: boolean
  message?: string
}

export interface NotificationState {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  id: string
}

// Component Props Types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface CardProps extends BaseComponentProps {
  title?: string
  subtitle?: string
  actions?: React.ReactNode
  hover?: boolean
}

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export interface TabItem {
  id: string
  label: string
  content: React.ReactNode
  disabled?: boolean
}

export interface ProgressStep {
  id: string
  title: string
  description?: string
  status: 'pending' | 'current' | 'completed'
  icon?: React.ReactNode
}