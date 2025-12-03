import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Clock, Package, Activity, Target } from 'lucide-react'
import { mockPumps, getLateOrdersData } from '@/lib/dataAdapter'

const calculateKPIData = () => {
  const totalOrders = mockPumps.length
  const lateOrdersData = getLateOrdersData()
  const onTimeOrders = lateOrdersData.find(d => d.name === 'On Time')?.value || 0
  const onTimeDeliveryRate = totalOrders > 0 ? (onTimeOrders / totalOrders * 100) : 0

  const avgBuildTime = mockPumps.reduce((sum, pump) => sum + pump.buildTime, 0) / mockPumps.length

  const activeJobs = mockPumps.filter(pump => pump.stage !== 'SHIPPED').length

  return [
    {
      title: 'Total Orders',
      value: totalOrders.toString(),
      change: '+12%',
      trend: 'up',
      icon: Package,
      status: 'primary',
      borderColor: 'border-primary/30',
      bgColor: 'bg-primary/5'
    },
    {
      title: 'On-Time Delivery',
      value: `${onTimeDeliveryRate.toFixed(1)}%`,
      change: '+3%',
      trend: 'up',
      icon: Target,
      status: 'success',
      borderColor: 'border-emerald-500/30',
      bgColor: 'bg-emerald-50 dark:bg-emerald-950/20'
    },
    {
      title: 'Avg Build Time',
      value: `${avgBuildTime.toFixed(0)} days`,
      change: '-2 days',
      trend: 'up',
      icon: Clock,
      status: 'warning',
      borderColor: 'border-industrial-safety-orange/30',
      bgColor: 'bg-industrial-safety-orange/5 dark:bg-industrial-safety-orange/10'
    },
    {
      title: 'Active Jobs',
      value: activeJobs.toString(),
      change: '+8%',
      trend: 'down',
      icon: Activity,
      status: 'info',
      borderColor: 'border-industrial-copper/30',
      bgColor: 'bg-industrial-copper/5 dark:bg-industrial-copper/10'
    }
  ]
}

export function KPICards() {
  const kpiData = calculateKPIData()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in">
      {kpiData.map((kpi, index) => (
        <Card
          key={index}
          className={`
            kpi-card hover:shadow-lg transition-all duration-300 hover:-translate-y-1
            border-l-4 ${kpi.borderColor} ${kpi.bgColor}
            animate-fade-in-delay-${index + 1}
          `}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-display font-medium text-muted-foreground uppercase tracking-wide">
                  {kpi.title}
                </p>
                <p className="text-3xl font-heading font-bold text-foreground mt-2 data-display">
                  {kpi.value}
                </p>
                <div className="flex items-center mt-3 space-x-2">
                  <div className={`
                    p-1 rounded-full
                    ${kpi.status === 'success' ? 'bg-emerald-100 dark:bg-emerald-900/30' : ''}
                    ${kpi.status === 'warning' ? 'bg-industrial-safety-orange/20 dark:bg-industrial-safety-orange/30' : ''}
                    ${kpi.status === 'info' ? 'bg-industrial-copper/20 dark:bg-industrial-copper/30' : ''}
                    ${kpi.status === 'primary' ? 'bg-primary/10 dark:bg-primary/20' : ''}
                  `}>
                    <kpi.icon className={`
                      h-4 w-4
                      ${kpi.status === 'success' ? 'text-emerald-600 dark:text-emerald-400' : ''}
                      ${kpi.status === 'warning' ? 'text-industrial-safety-orange' : ''}
                      ${kpi.status === 'info' ? 'text-industrial-copper' : ''}
                      ${kpi.status === 'primary' ? 'text-primary' : ''}
                    `} />
                  </div>
                  <span className={`
                    text-sm font-display font-medium
                    ${kpi.trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}
                  `}>
                    {kpi.change}
                  </span>
                  <span className="text-xs text-muted-foreground font-mono">vs last period</span>
                </div>
              </div>
              <div className={`
                h-14 w-14 rounded-xl flex items-center justify-center ml-4
                ${kpi.status === 'success' ? 'bg-gradient-to-br from-emerald-500 to-emerald-600' : ''}
                ${kpi.status === 'warning' ? 'bg-gradient-to-br from-industrial-safety-orange to-orange-600' : ''}
                ${kpi.status === 'info' ? 'bg-gradient-to-br from-industrial-copper to-copper-600' : ''}
                ${kpi.status === 'primary' ? 'bg-gradient-to-br from-primary to-primary/80' : ''}
              `}>
                <kpi.icon className="h-7 w-7 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}