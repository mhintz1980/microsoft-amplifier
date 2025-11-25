import React, { useState, useEffect } from 'react';
import { X, Settings, Users, Clock, TrendingUp } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { settingsManager, type SettingsFormData } from '../../lib/settings';
import type { DepartmentSettings } from '../../types/settings';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [formData, setFormData] = useState<SettingsFormData>({ departments: {} });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  // Load current settings when modal opens
  useEffect(() => {
    if (isOpen) {
      const currentSettings = settingsManager.getSettingsFormData();
      setFormData(currentSettings);
      setErrors([]);
    }
  }, [isOpen]);

  const handleInputChange = (departmentId: string, field: 'employeeCount' | 'efficiency', value: string) => {
    const numValue = parseInt(value) || 0;

    setFormData(prev => ({
      departments: {
        ...prev.departments,
        [departmentId]: {
          ...prev.departments[departmentId],
          [field]: field === 'employeeCount' ? Math.max(0, numValue) : Math.max(0, Math.min(100, numValue))
        }
      }
    }));
  };

  const calculateManHours = (employeeCount: number, efficiency: number): number => {
    return settingsManager.calculateManHours(employeeCount, efficiency);
  };

  const handleSave = async () => {
    setIsLoading(true);
    setErrors([]);

    try {
      // Validate form data
      const validation = settingsManager.validateFormData(formData);
      if (!validation.isValid) {
        setErrors(validation.errors);
        setIsLoading(false);
        return;
      }

      // Save settings
      settingsManager.updateSettings(formData);
      onClose();
    } catch (error) {
      setErrors(['Failed to save settings. Please try again.']);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form to current settings
    const currentSettings = settingsManager.getSettingsFormData();
    setFormData(currentSettings);
    setErrors([]);
    onClose();
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
      settingsManager.resetToDefaults();
      const defaultSettings = settingsManager.getSettingsFormData();
      setFormData(defaultSettings);
      setErrors([]);
    }
  };

  const getCurrentDepartments = (): DepartmentSettings[] => {
    return settingsManager.getSettings().departments;
  };

  if (!isOpen) return null;

  const currentDepartments = getCurrentDepartments();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div className="flex items-center space-x-3">
            <Settings className="h-6 w-6 text-blue-600" />
            <div>
              <CardTitle className="text-2xl">Department Settings</CardTitle>
              <CardDescription>
                Configure employee counts and efficiency rates for man-hours calculations
              </CardDescription>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleCancel}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-6">
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <div className="text-sm text-red-800">
                <div className="font-medium mb-1">Please fix the following errors:</div>
                <ul className="list-disc list-inside space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {currentDepartments.map((department) => {
              const formDataDept = formData.departments[department.id] || { employeeCount: 0, efficiency: 85 };
              const manHours = calculateManHours(formDataDept.employeeCount, formDataDept.efficiency);

              return (
                <Card key={department.id} className="relative">
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: department.color }}
                      />
                      <CardTitle className="text-lg">{department.displayName}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-1">
                          <Users className="h-4 w-4" />
                          Employees
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={formDataDept.employeeCount}
                          onChange={(e) => handleInputChange(department.id, 'employeeCount', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-1">
                          <TrendingUp className="h-4 w-4" />
                          Efficiency (%)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={formDataDept.efficiency}
                          onChange={(e) => handleInputChange(department.id, 'efficiency', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="85"
                        />
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-md p-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                          <Clock className="h-4 w-4" />
                          Daily Man-Hours
                        </label>
                        <span className="text-lg font-semibold text-gray-900">
                          {manHours}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {formDataDept.employeeCount} employees × 8 hours × {formDataDept.efficiency}% efficiency
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-900">
                    {currentDepartments.reduce((sum, dept) => {
                      const formDataDept = formData.departments[dept.id] || { employeeCount: 0, efficiency: 85 };
                      return sum + formDataDept.employeeCount;
                    }, 0)}
                  </div>
                  <div className="text-sm text-blue-700">Total Employees</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-900">
                    {Math.round(
                      currentDepartments.reduce((sum, dept) => {
                        const formDataDept = formData.departments[dept.id] || { employeeCount: 0, efficiency: 85 };
                        return sum + formDataDept.efficiency;
                      }, 0) / currentDepartments.length
                    )}%
                  </div>
                  <div className="text-sm text-blue-700">Average Efficiency</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-900">
                    {currentDepartments.reduce((sum, dept) => {
                      const formDataDept = formData.departments[dept.id] || { employeeCount: 0, efficiency: 85 };
                      return sum + calculateManHours(formDataDept.employeeCount, formDataDept.efficiency);
                    }, 0)}
                  </div>
                  <div className="text-sm text-blue-700">Total Daily Man-Hours</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-between items-center pt-4 border-t">
            <div className="flex space-x-2">
              <Button
                variant="outline"
                onClick={handleReset}
                className="text-red-600 border-red-200 hover:bg-red-50"
              >
                Reset to Defaults
              </Button>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}