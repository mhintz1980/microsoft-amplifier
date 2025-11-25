import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

export function formatDate(date: Date | string): string {
  const d = new Date(date)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(d)
}

export function getStatusColor(status: string): string {
  const statusColors = {
    'ON_TRACK': 'text-green-600 bg-green-50',
    'DELAYED': 'text-red-600 bg-red-50',
    'COMPLETED': 'text-blue-600 bg-blue-50',
    'CANCELLED': 'text-gray-600 bg-gray-50'
  }
  return statusColors[status as keyof typeof statusColors] || 'text-gray-600 bg-gray-50'
}

export function getPriorityColor(priority: string): string {
  const priorityColors = {
    'HIGH': 'text-red-600 bg-red-50',
    'MEDIUM': 'text-yellow-600 bg-yellow-50',
    'LOW': 'text-green-600 bg-green-50'
  }
  return priorityColors[priority as keyof typeof priorityColors] || 'text-gray-600 bg-gray-50'
}

export function getStageColor(stage: string): string {
  const stageColors = {
    'NOT_STARTED': 'text-gray-600 bg-gray-50',
    'FABRICATION': 'text-purple-600 bg-purple-50',
    'POWDER_COAT': 'text-orange-600 bg-orange-50',
    'ASSEMBLY': 'text-cyan-600 bg-cyan-50',
    'TESTING': 'text-blue-600 bg-blue-50',
    'SHIPPING': 'text-indigo-600 bg-indigo-50',
    'QA_COMPLETE': 'text-green-600 bg-green-50',
    'SHIPPED': 'text-emerald-600 bg-emerald-50'
  }
  return stageColors[stage as keyof typeof stageColors] || 'text-gray-600 bg-gray-50'
}