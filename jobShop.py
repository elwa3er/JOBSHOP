#imports
from __future__ import print_function
import collections
from ortools.sat.python import cp_model

class JobShop:
    def __init__(self):
        super().__init__()
        self.data=[]
    
    def read_data(self):
        pass
    def MinimalJobshopSat(self,jobs_data):
        """Minimal jobshop problem."""
        aff=[]
        # Create the model.
        model = cp_model.CpModel()

        """ jobs_data = [  # task = (machine_id, processing_time).
            [(0, 3), (1, 2), (2, 2)],  # Job0
            [(0, 2), (2, 1), (1, 4)],  # Job1
            [(1, 4), (2, 3)]  # Job2
        ] """

        #print(type(max(task[0] for job in jobs_data for task in job)),max(task[0] for job in jobs_data for task in job))
        machines_count = 1 + int(max(task[0] for job in jobs_data for task in job))
        all_machines = range(machines_count)

        # Computes horizon dynamically as the sum of all durations.
        horizon = sum(task[1] for job in jobs_data for task in job)

        # Named tuple to store information about created variables.
        task_type = collections.namedtuple('task_type', 'start end interval')
        # Named tuple to manipulate solution information.
        assigned_task_type = collections.namedtuple('assigned_task_type',
                                                    'start job index duration')

        # Creates job intervals and add to the corresponding machine lists.
        all_tasks = {}
        machine_to_intervals = collections.defaultdict(list)

        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                duration = task[1]
                suffix = '_%i_%i' % (job_id, task_id)
                start_var = model.NewIntVar(0, horizon, 'start' + suffix)
                end_var = model.NewIntVar(0, horizon, 'end' + suffix)
                interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                    'interval' + suffix)
                all_tasks[job_id, task_id] = task_type(
                    start=start_var, end=end_var, interval=interval_var)
                machine_to_intervals[machine].append(interval_var)

        # Create and add disjunctive constraints.
        for machine in all_machines:
            model.AddNoOverlap(machine_to_intervals[machine])

        # Precedences inside a job.
        for job_id, job in enumerate(jobs_data):
            for task_id in range(len(job) - 1):
                model.Add(all_tasks[job_id, task_id +
                                    1].start >= all_tasks[job_id, task_id].end)

        # Makespan objective.
        obj_var = model.NewIntVar(0, horizon, 'makespan')
        model.AddMaxEquality(obj_var, [
            all_tasks[job_id, len(job) - 1].end
            for job_id, job in enumerate(jobs_data)
        ])
        model.Minimize(obj_var)

        # Solve model.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            # Create one list of assigned tasks per machine.
            assigned_jobs = collections.defaultdict(list)
            for job_id, job in enumerate(jobs_data):
                for task_id, task in enumerate(job):
                    machine = task[0]
                    assigned_jobs[machine].append(
                        assigned_task_type(
                            start=solver.Value(all_tasks[job_id, task_id].start),
                            job=job_id,
                            index=task_id,
                            duration=task[1]))

            # Create per machine output lines.
            output = ''
            
            for machine in all_machines:
                
                # Sort by starting time.
                assigned_jobs[machine].sort()
                sol_line_tasks = 'Machine ' + str(machine) + ': '
                
                sol_line = '           '

                for assigned_task in assigned_jobs[machine]:
                    aff1=[]
                    #aff1.append(machine)
                    name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)
                    
                    # Add spaces to output to align columns.
                    sol_line_tasks += '%-10s' % name
                    aff1.append(assigned_task.job)
                    aff1.append("Mach"+str(machine))
                    #aff1.append(assigned_task.index)

                    start = assigned_task.start
                    duration = assigned_task.duration
                    aff1.append(assigned_task.start)
                    aff1.append(duration)
                    sol_tmp = '[%i,%i]' % (start, start + duration)
                    # Add spaces to output to align columns.
                    sol_line += '%-10s' % sol_tmp
                    
                    aff.append(aff1)
                    

                
                
                
                sol_line += '\n'
                sol_line_tasks += '\n'
                output += sol_line_tasks
                output += sol_line

            # Finally print the solution found.
            print('Optimal Schedule Length: %i' % solver.ObjectiveValue(),jobs_data)
            #print(output)
            
            nb_job=len(jobs_data)

            ou=[]
            for i in range(nb_job):
                o=[]
                for j in range(len(aff)):
                    if aff[j][0]==i:
                        o.append(aff[j])
                ou.append(o)
            
            print(ou)
            return ou,solver.ObjectiveValue()





