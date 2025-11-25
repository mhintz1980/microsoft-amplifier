import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, AlertTriangle, CheckCircle, Clock, Users, TrendingUp } from 'lucide-react';
import { updatePumpsWithCapacityAwareScheduling, calculateRealisticSchedules, getCapacityStatus } from '@/lib/dataAdapter';
import type { Pump } from '@/types';

export function CapacitySchedulingDemo() {
  const [pumpData, setPumpData] = useState<any>(null);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [capacityStatus, setCapacityStatus] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const refreshData = () => {
    setLoading(true);
    try {
      const updatedPumpData = updatePumpsWithCapacityAwareScheduling();
      const calculatedSchedules = calculateRealisticSchedules();
      const currentCapacityStatus = getCapacityStatus();

      setPumpData(updatedPumpData);
      setSchedules(calculatedSchedules);
      setCapacityStatus(currentCapacityStatus);
    } catch (error) {
      console.error('Error refreshing scheduling data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  if (!pumpData) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Capacity-Aware Scheduling Demo</h2>
          <p className="text-gray-600 mt-1">
            Demonstrates realistic job timing based on department man-hour capacity
          </p>
        </div>
        <Button onClick={refreshData} disabled={loading} className="flex items-center gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      {/* Capacity Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Department Capacity Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {capacityStatus.map((dept) => (
              <div key={dept.departmentId} className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-green-800 capitalize">
                  {dept.departmentId.replace('_', ' ')}
                </div>
                <div className="text-lg font-bold text-green-900">
                  {dept.dailyManHours}
                </div>
                <div className="text-xs text-green-600">man-hours/day</div>
                <div className="text-xs text-gray-500 mt-1">
                  {dept.queuedJobs} jobs queued
                </div>
              </div>
            ))}
          </div>
          {pumpData.conflicts.length > 0 && (
            <div className="mt-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
              <div className="flex items-center gap-2 text-yellow-800">
                <AlertTriangle className="h-4 w-4" />
                <span className="font-medium">
                  {pumpData.conflicts.length} capacity conflicts detected
                </span>
              </div>
            </div>
          )}
          {pumpData.conflicts.length === 0 && (
            <div className="mt-4 p-3 bg-green-100 border border-green-300 rounded-lg">
              <div className="flex items-center gap-2 text-green-800">
                <CheckCircle className="h-4 w-4" />
                <span className="font-medium">No capacity conflicts - Schedule is optimized</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Problem Demonstration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Problem: 4 Jobs Completing Fabrication in 1 Day (Without Capacity Constraints)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <h4 className="font-medium text-red-800 mb-2">❌ Before (Unrealistic)</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Fabrication Jobs:</span>
                  <span className="font-medium">4 jobs</span>
                </div>
                <div className="flex justify-between">
                  <span>Time per Job:</span>
                  <span className="font-medium">15 days</span>
                </div>
                <div className="flex justify-between">
                  <span>Unrealistic Completion:</span>
                  <span className="font-bold text-red-600">All in 1 day!</span>
                </div>
              </div>
              <div className="mt-3 text-xs text-red-600">
                ⚠️ Ignores department capacity constraints
              </div>
            </div>

            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h4 className="font-medium text-green-800 mb-2">✅ After (Capacity-Aware)</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Fabrication Jobs:</span>
                  <span className="font-medium">{pumpData.pumps.filter((p: Pump) => p.stage === 'FABRICATION').length} jobs</span>
                </div>
                <div className="flex justify-between">
                  <span>Department Capacity:</span>
                  <span className="font-medium">54 man-hours/day</span>
                </div>
                <div className="flex justify-between">
                  <span>Realistic Duration:</span>
                  <span className="font-bold text-green-600">~1.5 days each</span>
                </div>
              </div>
              <div className="mt-3 text-xs text-green-600">
                ✅ Respects man-hour capacity constraints
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Pumps with Capacity-Aware Timing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Current Pumps with Capacity-Aware Timing
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {pumpData.pumps.map((pump: Pump) => (
              <div key={pump.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">{pump.model_id}</h4>
                  <span className={`text-xs px-2 py-1 rounded ${
                    pump.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                    pump.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {pump.priority}
                  </span>
                </div>
                <div className="text-xs text-gray-600 mb-2">{pump.customer}</div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span>Department:</span>
                    <span className="font-medium">{pump.currentDepartment || pump.stage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Original Build Time:</span>
                    <span className="font-medium">{pump.buildTime} days</span>
                  </div>
                  {pump.capacityInfo && (
                    <>
                      <div className="flex justify-between">
                        <span>Capacity Duration:</span>
                        <span className="font-bold text-blue-600">
                          {pump.capacityInfo.duration.toFixed(1)} days
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Required Hours:</span>
                        <span className="font-medium">{pump.capacityInfo.estimatedHours}h</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Est. Completion:</span>
                        <span className="font-medium">
                          {new Date(pump.capacityInfo.completionDate).toLocaleDateString()}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Schedule Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Realistic Production Schedule
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {schedules.map((schedule: any) => {
              const pump = pumpData.pumps.find((p: Pump) => p.id === schedule.jobId);
              return (
                <div key={schedule.jobId} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{pump?.model_id || schedule.jobId}</h4>
                    <span className="text-sm text-gray-500">
                      {pump?.customer}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Start Date</div>
                      <div className="font-medium">
                        {schedule.startDate.toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">End Date</div>
                      <div className="font-medium">
                        {schedule.endDate.toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">Total Duration</div>
                      <div className="font-medium text-blue-600">
                        {schedule.totalDuration} days
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    {schedule.stages.length} production stages with capacity constraints
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}