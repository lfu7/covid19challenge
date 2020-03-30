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
CORONA_SYMPTOM_MULTIPLIER = 10


class Patient(object):
    def __init__(self, patient_id, query_time, corona_symptom, covid, age, pre_existing_condition, stay_duration, location):
        '''
        Constructor for the Voter class
        Input:
            arrival_time: (float) Time in minutes at which the voter arrives
            stay_duration: (float) Time in minutes the voter stays
            in the voting booth
        '''
        self.patient_id = patient_id
        self.query_time = query_time
        self.corona_symptom = corona_symptom
        self.covid = covid
        self.age = age
        self.pre_existing_condition = pre_existing_condition
        self.location = location
        self.stay_duration = stay_duration


        # start_time and departure_time will be calculated later
        self.start_time = None
        self.departure_time = None
        self.assigned_bed = None

        self.priority = None


def get_priority(patient_obj, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER):
    priority_score = age_multiplier * patient_obj.age + pre_existing_condition_multiplier * patient_obj.pre_existing_condition + \
                     corona_symptom_multiplier * patient_obj.corona_symptom
    if priority_score >= HIGH_SCORE:
        priority_score -= HIGH_SCORE_PENALTY
    return priority_score


def generate_patient_obj_list(patient_df, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER):
    patient_lst = []
    for index, row in patient_df.iterrows():
        current_patient = Patient(row["patient_id"], row["query_time"], row["corona_symptom"], row["covid"],
                                  row["age"],
                                  row["pre_existing_condition"], row["stay_duration"],row["location"])
        current_patient.priority = get_priority(current_patient, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER)
        patient_lst.append(current_patient)
    lst = sorted(patient_lst, key=lambda x: x.priority, reverse=True)
    return lst


class Hospital(object):
    def __init__(self, name, max_num_patients):
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

    def simulate(self, patient_df, num_beds, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER):

        ### Can change this to take in some pre randomized list of patients ###
        '''
        Simulate a day of voting
        Input:
            seed: (int) Random seed to use in the simulation
            num_beds: (int) Number of booths to use in the simulation
        Return:
            List of voters who voted in the precinct
        '''

        patient_list = generate_patient_obj_list(patient_df, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER)
        final_patient_list = []

        # Initialize default base voter (not the first voter!)
        # as reference voter in self.next_patient
        current_time = patient_list[0].query_time

        # Create a single queue of VotingBooths class to hold
        # departure times of all people currently IN voting booths
        # Max queue size should be capped at num_beds
        all_beds = Bed(queue.PriorityQueue(num_beds))

        for patient_index in range(min(len(patient_list), self.max_num_patients)):
            new_patient = patient_list[patient_index]

            # When booths are full
            if not all_beds.check_full():
                # min_departure_time is the earliest departure time among
                # all people currently in all_beds
                new_patient.start_time = new_patient.query_time
            else:   
                min_departure_time = all_beds.get_remove_patient_dep()
                current_time = min_departure_time
                new_patient.start_time = max(new_patient.query_time, current_time)
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


def find_avg_wait_time(hospital_object, df, num_beds):
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

    final_patient_list = hospital_object.simulate(df, num_beds)
    average_one_trial = sum([(v.start_time - v.query_time) for v in final_patient_list]) / len(final_patient_list)

        # Increments seed in random.seed() used in simulate method
        # of Precinct class


    return average_one_trial  # Median trial average


def find_number_of_beds(hospital, df, target_wait_time, max_num_beds):
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
        avg_wait_time = find_avg_wait_time(hospital, df, num_beds)
        if avg_wait_time <= target_wait_time:
            return (num_beds, avg_wait_time)

    return (0, None)

'''
header_list = ["patient_id", "query_time", "corona_symptom", "covid", "age", "pre_existing_condition",\
"stay_duration","location"]
df = pd.read_csv("trial_priority_data.csv", names=header_list)

shitty_hospital = Hospital('Borja', 100)
print('priority', "query_time", 'start time', 'stay_duration','departure_time')
for i in shitty_hospital.simulate(df,2):
    print(i.priority, i.query_time, i.start_time, i.stay_duration, i.departure_time)
'''
def master_function(patient_df, hospital_id, num_beds_in_hospital, num_beds_for_sim, target_wait_time, max_num_beds,
    age_multiplier=AGE_MULTIPLIER, pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
    high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY, 
    corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER):

    '''
    Master function that combines all previous functions and gives all outputs that are needed for web app usage
    Inputs:
      patient_df: dataframe that contains patient information from questionaire
      hospital_id: name of hospital
      num_beds_in_hospital: total number of beds in a hospital
      num_beds_for_sim: number of beds in a hospital that should be used in simulation of coronavirus patient wait times
      target_awit_time: wait time desired by hospital input for find_number_of_beds
      max_num_beds: maximum possible number of beds that are to be used in find_number_of_beds function
      multipliers: inputs for getting patient score
    Outputs:
      patient_final_df: dataframe containing information on patient wait time, stay duration, priority number
      avg_wait_time: average wait time for a given hospital, given a number of beds
      find_number_of_beds: number of beds needed to reach an ideal wait time
    '''

    hospital = Hospital(hospital_id, num_beds_in_hospital)
    patient_df.columns = ["patient_id", "query_time", "corona_symptom", "covid", "age", "pre_existing_condition",\
    "stay_duration","location"]

    final_header_list = ["patient_id", "priority", "query_time", "start_time", "stay_duration", "departure_time"]
    patient_list = hospital.simulate(df, num_beds_for_sim, age_multiplier=AGE_MULTIPLIER,
                 pre_existing_condition_multiplier=PRE_EXISTING_CONDITION_MULTIPLIER,
                 high_score=HIGH_SCORE, high_score_penalty=HIGH_SCORE_PENALTY,
                 corona_symptom_multiplier=CORONA_SYMPTOM_MULTIPLIER)
    patient_attribute_list = []
    for i in patient_list:
        patient_attribute_list.append([i.patient_id, i.priority, i.query_time, i.start_time, i.stay_duration, i.departure_time])    
    patient_final_df = pd.DataFrame(patient_attribute_list, columns = final_header_list)
    avg_wait_time = find_avg_wait_time(hospital, patient_df, num_beds_for_sim)
    ideal_num_beds = find_number_of_beds(hospital, patient_df, target_wait_time, max_num_beds)

    return patient_final_df, avg_wait_time, ideal_num_beds

























