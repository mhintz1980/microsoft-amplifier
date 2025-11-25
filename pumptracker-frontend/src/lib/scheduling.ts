/**
 * Capacity-aware scheduling system for PumpTracker Lite
 * Handles job duration calculations based on department man-hour capacity
 */

import { settingsManager } from './settings';
import type { DepartmentSettings } from '../types/settings';

export interface JobStage {
  departmentId: string;
  estimatedHours: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface JobSchedule {
  jobId: string;
  stages: JobStage[];
  startDate: Date;
  endDate: Date;
  totalDuration: number; // in days
}

export interface DepartmentCapacity {
  departmentId: string;
  dailyManHours: number;
  currentLoad: number; // hours allocated today
  queuedJobs: number;
}

export interface SchedulingConflict {
  departmentId: string;
  date: Date;
  demand: number; // required man-hours
  capacity: number; // available man-hours
  overload: number; // excess hours
}

/**
 * Capacity-aware scheduler that respects department man-hour constraints
 */
export class CapacityAwareScheduler {
  private settings: DepartmentSettings[];

  constructor() {
    this.settings = settingsManager.getSettings().departments;
  }

  /**
   * Calculate job duration considering department capacity
   * Formula: max(1, job_estimated_hours / daily_man_hours) in days
   * When multiple jobs compete: they share the daily capacity
   */
  public calculateJobDuration(job: JobStage, competingJobs: JobStage[] = []): number {
    const department = this.getDepartment(job.departmentId);
    if (!department || department.manHours <= 0) {
      return 1; // Default to 1 day if no capacity info
    }

    const dailyManHours = department.manHours;

    // Calculate total demand for this department
    const totalDemand = job.estimatedHours + competingJobs
      .filter(j => j.departmentId === job.departmentId)
      .reduce((sum, j) => sum + j.estimatedHours, 0);

    // Calculate duration based on shared capacity
    const duration = Math.max(1, totalDemand / dailyManHours);

    return Math.ceil(duration * 10) / 10; // Round to 1 decimal place
  }

  /**
   * Schedule a complete job through all stages with capacity awareness
   */
  public scheduleJob(jobId: string, stages: JobStage[], startDate: Date = new Date()): JobSchedule {
    const currentDate = new Date(startDate);
    const scheduledStages: JobStage[] = [];

    // Track competing jobs by department for each day
    const departmentJobs: Record<string, JobStage[]> = {};

    stages.forEach((stage, index) => {
      if (!departmentJobs[stage.departmentId]) {
        departmentJobs[stage.departmentId] = [];
      }

      // Calculate duration considering competing jobs at this stage
      const competingJobs = departmentJobs[stage.departmentId] || [];
      const duration = this.calculateJobDuration(stage, competingJobs);

      // Add to scheduled stages
      scheduledStages.push({
        ...stage,
        estimatedHours: stage.estimatedHours
      });

      // Track this job for competition with subsequent jobs
      departmentJobs[stage.departmentId].push(stage);

      // Move to next stage (add buffer days between departments)
      currentDate.setDate(currentDate.getDate() + Math.ceil(duration) + 1);
    });

    const totalDuration = Math.ceil((currentDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    return {
      jobId,
      stages: scheduledStages,
      startDate,
      endDate: currentDate,
      totalDuration
    };
  }

  /**
   * Calculate capacity utilization for a department over a time period
   */
  public getDepartmentCapacity(departmentId: string, days: number = 7): DepartmentCapacity {
    const department = this.getDepartment(departmentId);
    if (!department) {
      return {
        departmentId,
        dailyManHours: 0,
        currentLoad: 0,
        queuedJobs: 0
      };
    }

    return {
      departmentId,
      dailyManHours: department.manHours,
      currentLoad: 0, // Would be calculated from actual scheduled jobs
      queuedJobs: 0   // Would be calculated from actual queued jobs
    };
  }

  /**
   * Detect scheduling conflicts where demand exceeds capacity
   */
  public detectConflicts(jobs: JobSchedule[], days: number = 7): SchedulingConflict[] {
    const conflicts: SchedulingConflict[] = [];
    const departmentDemand: Record<string, Record<string, number>> = {};

    // Calculate daily demand per department
    jobs.forEach(job => {
      job.stages.forEach(stage => {
        const department = this.getDepartment(stage.departmentId);
        if (!department) return;

        const dailyCapacity = department.manHours;
        const dailyDemand = stage.estimatedHours / Math.ceil(this.calculateJobDuration(stage));

        // For each day of this stage, add demand
        for (let day = 0; day < Math.ceil(this.calculateJobDuration(stage)); day++) {
          const dateKey = new Date(job.startDate.getTime() + day * 24 * 60 * 60 * 1000)
            .toISOString().split('T')[0];

          if (!departmentDemand[stage.departmentId]) {
            departmentDemand[stage.departmentId] = {};
          }
          departmentDemand[stage.departmentId][dateKey] =
            (departmentDemand[stage.departmentId][dateKey] || 0) + dailyDemand;

          // Check for conflicts
          if (departmentDemand[stage.departmentId][dateKey] > dailyCapacity) {
            conflicts.push({
              departmentId: stage.departmentId,
              date: new Date(dateKey),
              demand: departmentDemand[stage.departmentId][dateKey],
              capacity: dailyCapacity,
              overload: departmentDemand[stage.departmentId][dateKey] - dailyCapacity
            });
          }
        }
      });
    });

    return conflicts;
  }

  /**
   * Get optimal start date to minimize conflicts and delays
   */
  public getOptimalStartDate(job: JobStage[], preferredStartDate?: Date): Date {
    const startDate = preferredStartDate || new Date();
    let bestDate = new Date(startDate);
    let minConflicts = Infinity;

    // Look for best start date within next 14 days
    for (let days = 0; days < 14; days++) {
      const testDate = new Date(startDate.getTime() + days * 24 * 60 * 60 * 1000);
      const testSchedule = this.scheduleJob('test', job, testDate);
      const conflicts = this.detectConflicts([testSchedule]);

      if (conflicts.length < minConflicts) {
        minConflicts = conflicts.length;
        bestDate = new Date(testDate);
      }

      // Stop if we find a conflict-free date
      if (minConflicts === 0) break;
    }

    return bestDate;
  }

  /**
   * Simulate job completion dates for multiple jobs
   */
  public simulateMultipleJobs(jobs: Array<{ jobId: string; stages: JobStage[] }>): JobSchedule[] {
    const schedules: JobSchedule[] = [];

    // Sort jobs by priority (HIGH first)
    const sortedJobs = jobs.sort((a, b) => {
      const priorityOrder = { 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
      const aPriority = Math.max(...a.stages.map(s => priorityOrder[s.priority]));
      const bPriority = Math.max(...b.stages.map(s => priorityOrder[s.priority]));
      return bPriority - aPriority;
    });

    // Schedule each job
    sortedJobs.forEach((job, index) => {
      // Start next job after previous jobs have progressed
      const startDate = index === 0 ? new Date() :
        new Date(Date.now() + index * 2 * 24 * 60 * 60 * 1000); // 2-day buffer

      const schedule = this.scheduleJob(job.jobId, job.stages, startDate);
      schedules.push(schedule);
    });

    return schedules;
  }

  /**
   * Get current capacity status for all departments
   */
  public getCapacityStatus(): DepartmentCapacity[] {
    return this.settings.map(dept => ({
      departmentId: dept.id,
      dailyManHours: dept.manHours,
      currentLoad: 0, // Would be calculated from actual jobs
      queuedJobs: 0   // Would be calculated from actual queue
    }));
  }

  /**
   * Update settings (call when settings change)
   */
  public refreshSettings(): void {
    this.settings = settingsManager.getSettings().departments;
  }

  private getDepartment(departmentId: string): DepartmentSettings | undefined {
    return this.settings.find(dept =>
      dept.id.toLowerCase() === departmentId.toLowerCase() ||
      dept.name.toLowerCase() === departmentId.toLowerCase()
    );
  }
}

// Export singleton instance
export const scheduler = new CapacityAwareScheduler();

// Export convenience functions
export const calculateJobDuration = (job: JobStage, competingJobs?: JobStage[]) => {
  const instance = new CapacityAwareScheduler();
  return instance.calculateJobDuration(job, competingJobs);
};

export const scheduleJob = (jobId: string, stages: JobStage[], startDate?: Date) => {
  const instance = new CapacityAwareScheduler();
  return instance.scheduleJob(jobId, stages, startDate);
};

export const detectConflicts = (jobs: JobSchedule[], days?: number) => {
  const instance = new CapacityAwareScheduler();
  return instance.detectConflicts(jobs, days);
};

export const simulateMultipleJobs = (jobs: Array<{ jobId: string; stages: JobStage[] }>) => {
  const instance = new CapacityAwareScheduler();
  return instance.simulateMultipleJobs(jobs);
};