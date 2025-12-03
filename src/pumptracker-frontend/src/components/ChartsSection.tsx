import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Treemap } from 'recharts'
import { getCustomerValueData, getStageDistribution, getLateOrdersData, getPriorityDistribution, getDepartmentName } from '@/lib/dataAdapter'

const RADIAN = Math.PI / 180

const renderCustomizedLabel = ({
  cx, cy, midAngle, innerRadius, outerRadius, percent
}: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      className="text-xs font-medium"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export function ChartsSection() {
  const [chartType, setChartType] = useState<'pie' | 'bar'>('pie')
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null)

  const customerData = getCustomerValueData()
  const stageData = getStageDistribution()
  const lateOrdersData = getLateOrdersData()
  const priorityData = getPriorityDistribution()

  // Treemap data for departments - fixed to show human-readable names
  const treemapData = stageData.map(item => ({
    name: item.name, // Already using getDepartmentName() in dataAdapter
    size: item.value,
    color: item.color
  }))

  const handleCustomerClick = (data: any) => {
    if (data && data.name) {
      setSelectedCustomer(data.name)
      console.log('Clicked customer:', data.name)
      // In a real app, this would drill down to customer details
    }
  }

  const handleStageClick = (data: any) => {
    if (data && data.name) {
      console.log('Clicked department:', data.name)
      // In a real app, this would drill down to department details
    }
  }

  return (
    <div className="space-y-6">
      {/* Chart Type Toggle */}
      <div className="flex justify-end">
        <div className="flex gap-2">
          <button
            onClick={() => setChartType('pie')}
            className={`px-3 py-1 rounded-md text-sm ${
              chartType === 'pie'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Pie Charts
          </button>
          <button
            onClick={() => setChartType('bar')}
            className={`px-3 py-1 rounded-md text-sm ${
              chartType === 'bar'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Bar Charts
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Production Overview → Late Orders - FIXED */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Late Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              {chartType === 'pie' ? (
                <PieChart>
                  <Pie
                    data={lateOrdersData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={70}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {lateOrdersData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} orders`, 'Count']} />
                  <Legend />
                </PieChart>
              ) : (
                <BarChart data={lateOrdersData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value} orders`, 'Count']} />
                  <Bar dataKey="value">
                    {lateOrdersData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Schedule & Lead Times → Late Orders - FIXED */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Order Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              {chartType === 'pie' ? (
                <PieChart>
                  <Pie
                    data={lateOrdersData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={70}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {lateOrdersData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} orders`, 'Count']} />
                  <Legend />
                </PieChart>
              ) : (
                <BarChart data={lateOrdersData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value} orders`, 'Count']} />
                  <Bar dataKey="value">
                    {lateOrdersData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Sales & Customers → Value By Customer - FIXED */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => handleCustomerClick(customerData[0])}
        >
          <CardHeader>
            <CardTitle className="text-lg">Value By Customer</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              {chartType === 'pie' ? (
                <PieChart>
                  <Pie
                    data={customerData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={70}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {customerData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`$${(value as number).toLocaleString()}`, 'Value']}
                  />
                  <Legend />
                </PieChart>
              ) : (
                <BarChart data={customerData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => [`$${(value as number).toLocaleString()}`, 'Value']}
                  />
                  <Bar dataKey="value">
                    {customerData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
            {selectedCustomer && (
              <p className="text-sm text-gray-600 mt-2 text-center">
                Selected: {selectedCustomer}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Bottlenecks → Priority Distribution - FIXED */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Priority Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              {chartType === 'pie' ? (
                <PieChart>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={70}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} pumps`, 'Count']} />
                  <Legend />
                </PieChart>
              ) : (
                <BarChart data={priorityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value} pumps`, 'Count']} />
                  <Bar dataKey="value">
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Department Tree Map - FIXED department names */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Department Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <Treemap
                data={[{ name: 'Departments', children: treemapData }]}
                dataKey="size"
                aspectRatio={4 / 3}
                stroke="#fff"
                fill="#8884d8"
                content={({ x, y, width, height, name, color }: any) => (
                  <g>
                    <rect
                      x={x}
                      y={y}
                      width={width}
                      height={height}
                      style={{
                        fill: color,
                        stroke: '#fff',
                        strokeWidth: 2,
                        strokeOpacity: 1,
                        cursor: 'pointer'
                      }}
                      onClick={() => handleStageClick({ name })}
                    />
                    {width > 50 && height > 30 && (
                      <text
                        x={x + width / 2}
                        y={y + height / 2}
                        fill="#fff"
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className="text-xs font-medium"
                      >
                        {name}
                      </text>
                    )}
                  </g>
                )}
              />
            </ResponsiveContainer>
            <p className="text-sm text-gray-600 mt-2 text-center">
              Click on departments to drill down
            </p>
          </CardContent>
        </Card>

        {/* Lead Time Trend - NEW CHART */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Production Stages</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stageData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={80} />
                <Tooltip formatter={(value) => [`${value} pumps`, 'Count']} />
                <Bar dataKey="value">
                  {stageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}