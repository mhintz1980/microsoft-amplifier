import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChevronDown, ChevronRight, Eye, Edit } from 'lucide-react'
import { formatDate, formatCurrency, getStatusColor } from '@/lib/utils'
import { mockPumps } from '@/lib/dataAdapter'

// Group pumps by PO
const pumpDataByPO = mockPumps.reduce((acc, pump) => {
  if (!acc[pump.po_id]) {
    acc[pump.po_id] = {
      id: pump.po_id,
      customer: pump.customer,
      pumps: [],
      isExpanded: false
    }
  }
  acc[pump.po_id].pumps.push(pump)
  return acc
}, {} as Record<string, any>)

export function OrderDetails() {
  const [poData, setPOData] = useState(pumpDataByPO)

  const toggleExpand = (poId: string) => {
    setPOData(prev => ({
      ...prev,
      [poId]: {
        ...prev[poId],
        isExpanded: !prev[poId].isExpanded
      }
    }))
  }

  const calculateTotalValue = (pumps: any[]) => {
    return pumps.reduce((total, pump) => total + pump.value, 0)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Order Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Object.values(poData).map((po: any) => (
            <div key={po.id} className="border rounded-lg overflow-hidden">
              {/* PO Header - Always Visible */}
              <div
                className="p-4 bg-gray-50 flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleExpand(po.id)}
              >
                <div className="flex items-center gap-4">
                  <button className="p-1 hover:bg-gray-200 rounded">
                    {po.isExpanded ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{po.id}</span>
                      <span className="text-sm text-gray-600 bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {po.pumps.length} pump{po.pumps.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {po.customer} • {formatCurrency(calculateTotalValue(po.pumps))}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 hover:bg-gray-200 rounded">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="p-2 hover:bg-gray-200 rounded">
                    <Edit className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Expandable PO Lines */}
              {po.isExpanded && (
                <div className="p-4 bg-white border-t">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-4">Pump ID</th>
                          <th className="text-left py-2 px-4">Model</th>
                          <th className="text-left py-2 px-4">Stage</th>
                          <th className="text-left py-2 px-4">Priority</th>
                          <th className="text-left py-2 px-4">Value</th>
                          <th className="text-left py-2 px-4">Color</th>
                          <th className="text-left py-2 px-4">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {po.pumps.map((pump: any) => (
                          <tr key={pump.id} className="border-b hover:bg-gray-50">
                            <td className="py-2 px-4 font-medium">{pump.id}</td>
                            <td className="py-2 px-4">{pump.model_id}</td>
                            <td className="py-2 px-4">
                              <span className={`text-xs px-2 py-1 rounded ${getStatusColor(pump.stage)}`}>
                                {pump.stage.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="py-2 px-4">
                              <span className={`text-xs px-2 py-1 rounded font-medium ${
                                pump.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                                pump.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {pump.priority}
                              </span>
                            </td>
                            <td className="py-2 px-4">{formatCurrency(pump.value)}</td>
                            <td className="py-2 px-4">{pump.powder_color}</td>
                            <td className="py-2 px-4">
                              <div className="flex gap-1">
                                <button className="p-1 hover:bg-gray-200 rounded">
                                  <Eye className="h-3 w-3" />
                                </button>
                                <button className="p-1 hover:bg-gray-200 rounded">
                                  <Edit className="h-3 w-3" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}