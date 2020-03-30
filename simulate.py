import sys
import random
import queue
import util
import numpy as np
import pandas as pd

AGE_MULTIPLIER = 0.1
PRE_EXISTING_CONDITION_MULTIPLIER = 10
HIGH_SCORE = 100
HIGH_SCORE_PENALTY = 10
TROUBLE_BREATHING_MULTIPLIER = 10


class Patient(object):
    def __init__(self, patient_id, query_time, trouble_breathing, covid, age, pre_existing_condition, location):
        '''
        Constructor for the Voter class
        Input:
            arrival_time: (float) Time in minutes at which the voter arrives
            stay_duration: (float) Time in minutes the voter stays
            in the voting booth
        '''
        self.patient_id = patient_id
        self.query_time = query_time
        self.trouble_breathing = trouble_breathing
        self.covid = covid
        self.age = age
        self.pre_existing_condition = pre_existing_condition
        self.location = location

        # start_time and departure_time will be calculated later
        self.start_time = None
        self.departure_time = None
        self.assigned_bed = None
        self.stay_duration = None

        self.priority = None


def get_priority(patient_obj, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 trouble_breathing_multiplier=TROUBLE_BREATHING_MULTIPLIER):
    priority_score = age_multiplier * patient_obj.age + pre_existing_condition_multiplier * patient_obj.pre_existing_condition + \
                     trouble_breathing_multiplier * patient_obj.trouble_breathing
    if priority_score >= HIGH_SCORE:
        priority_score -= HIGH_SCORE_PENALTY
    return priority_score


def generate_patient_obj_list(patient_df):
    patient_lst = []
    for index, row in patient_df.iterrows():
        current_patient = Patient(row["patient_id"], row["query_time"], row["trouble_breathing"], row["covid"],
                                  row["age"],
                                  row["pre_existing_condition"], row["location"])
        current_patient.priority = get_priority(current_patient)
        patient_lst.append(current_patient)
    lst = sorted(patient_lst, key=lambda x: x.priority, reverse=True)
    return lst


class Hospital(object):
    def __init__(self, name, max_num_patients, stay_duration_rate):
        '''
        Constructor for the Precinct class
        Input:
            name: (str) Name of the precinct
            hours_open: (int) Hours the precinct will remain open
            max_num_patients: (int) number of voters in the precinct
            arrival_rate: (float) rate at which voters arrive
            stay_duration_rate: (float) lambda for voting duration
        '''

        self.name = name
        self.max_num_patients = max_num_patients
        self.stay_duration_rate = stay_duration_rate

    def generate_stay_duration(self):
        '''
        Generate the next voter as Voter object given the previous voter
        Inputs:
            prev_patient: the previous Voter object with arrival_time and
                        stay_duration attributes
        Return:
            next_patient: Voter object of next voter with new arrival_time
                        and stay_duration atrributes
        '''

        # Extract gap between arrival times and new voting duration
        # from poisson

        ### We need to find the average stay duration or choose some sort of probabalistic model for how lnog patients stay ###
        gap = util.gen_poisson_patient_parameters(self.stay_duration_rate)

        return gap

    def simulate(self, seed, patient_df, num_beds):

        ### Can change this to take in some pre randomized list of patients ###
        '''
        Simulate a day of voting
        Input:
            seed: (int) Random seed to use in the simulation
            num_beds: (int) Number of booths to use in the simulation
        Return:
            List of voters who voted in the precinct
        '''
        random.seed(seed)

        patient_list = generate_patient_obj_list(patient_df)
        final_patient_list = []

        # Initialize default base voter (not the first voter!)
        # as reference voter in self.next_patient
        current_time = 0

        # Create a single queue of VotingBooths class to hold
        # departure times of all people currently IN voting booths
        # Max queue size should be capped at num_beds
        all_beds = Bed(queue.PriorityQueue(num_beds))

        for patient_index in range(min(len(patient_list), self.max_num_patients)):
            new_patient = patient_list[patient_index]

            # When booths are full
            if all_beds.check_full():
                # min_departure_time is the earliest departure time among
                # all people currently in all_beds
                min_departure_time = all_beds.get_remove_patient_dep()
                current_time += min_departure_time
            if current_time <= new_patient.query_time:
                new_patient.start_time = new_patient.query_time
            else:
                new_patient.start_time = current_time
            new_patient.stay_duration = self.generate_stay_duration()
            new_patient.departure_time = new_patient.start_time + new_patient.stay_duration

            all_beds.add_patient_dep(new_patient.departure_time)
            final_patient_list.append(new_patient)

        return final_patient_list

def get_patient_info(final_patient_list, patient_id):
    for patient in final_patient_list:
        if patient.patient_id == patient_id:
            return patient




class Bed(object):
    def __init__(self, bed_queue):
        '''
        Constructor for the VotingBooths class
        Inputs:
            booth_queue: PriorityQueue object to model peoples' departure
            times in booths. This is set to private attribute.
        '''

        self._bed_queue = bed_queue

    def add_patient_dep(self, patient_dep):
        '''
        Adds voters' departure time in minutes to _booth_queue attribute
        of VotingBooths object
        Inputs:
            patient_dep: (float) Departure time of a voter in minutes
        Return:
            Doesn't return anything new. Just modifies _booth_queue.
        '''

        self._bed_queue.put(patient_dep, block=False)

    def get_remove_patient_dep(self):
        '''
        Extracts and removes earliest (minimum) voter departure time
        from the _booth_queue attribute.
        Inputs:
            Nothing. Modifies VotingBooths object itself.
        Return:
            Minimum voter departure time (float) from _booth_queue.
        '''

        return self._bed_queue.get(block=False)

    def check_full(self):
        '''
        Checks whether the _booth_queue is full
        Inputs:
            Nothing. Checks VotingBooths object itself.
        Return:
            Boolean value for whether _booth_queue is full
        '''
        return self._bed_queue.full()


def find_avg_wait_time(hospital_object, df, num_beds, ntrials, initial_seed=0):
    '''
    Simulates a precinct multiple times with a given number of booths
    For each simulation, computes the average waiting time of the voters,
    and returns the median of those average waiting times.
    Input:
        precinct: (dictionary) A precinct dictionary
        num_beds: (int) The number of booths to simulate the precinct with
        ntrials: (int) The number of trials to run
        initial_seed: (int) initial seed for random number generator
    Output:
        The median of the average waiting times returned by simulating
        the precinct 'ntrials' times.
    '''

    # Use information in precinct dictionary to construct Precinct
    # object

    ### Need to get hospital data from the US list ###

    # Accumulate list of trial averages.
    trial_averages = []
    for trial in range(ntrials):
        final_patient_list = hospital_object.simulate(initial_seed, df, num_beds)
        average_one_trial = sum([v.start_time - v.query_time for v in final_patient_list]) / len(final_patient_list)
        trial_averages.append(average_one_trial)

        # Increments seed in random.seed() used in simulate method
        # of Precinct class
        initial_seed += 1

    trial_averages = sorted(trial_averages)

    return trial_averages[ntrials // 2]  # Median trial average


def find_number_of_beds(hospital, df, target_wait_time, max_num_beds,
                          ntrials, seed=0):
    '''
    Finds the number of booths a precinct needs to guarantee a bounded
    (average) waiting time.
    Input:
        precinct: (dictionary) A precinct dictionary
        target_wait_time: (float) The desired (maximum) waiting time
        max_num_beds: (int) The maximum number of booths this
                        precinct can support
        ntrials: (int) The number of trials to run when computing
                 the average waiting time
        seed: (int) A random seed
    Output:
        A tuple (num_beds, waiting_time) where:
        - num_beds: (int) The smallest number of booths that ensures
                      the average waiting time is below target_waiting_time
        - waiting_time: (float) The actual average waiting time with that
                        number of booths
        If the target waiting time is infeasible, returns (0, None)
    '''
    ### Can use this to find the optimal number of beds for different hospitals ###

    for num_beds in range(1, max_num_beds + 1):
        avg_wait_time = find_avg_wait_time(hospital, df, num_beds, ntrials, seed)
        if avg_wait_time < target_wait_time:
            return (num_beds, avg_wait_time)

    return (0, None)


header_list = ["patient_id", "query_time", "trouble_breathing", "covid", "age", "pre_existing_condition", "location"]
df = pd.read_csv("trial_priority_data.csv", names=header_list)

shitty_hospital = Hospital('Borja', 2, 2)
print('priority', 'start time', 'stay_duration','departure_time')
for i in shitty_hospital.simulate(1234, df,3):
    print(i.priority, i.start_time, i.stay_duration, i.departure_time)



