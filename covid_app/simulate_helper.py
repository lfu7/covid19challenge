import queue


class Patient(object):
    def __init__(self, patient_id, query_time, corona_symptom, covid, age, pre_existing_condition, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier):
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
        self.age_multiplier = age_multiplier
        self.pre_existing_condition_multiplier = pre_existing_condition_multiplier
        self.corona_symptom_multiplier = corona_symptom_multiplier


        # start_time and departure_time will be calculated later
        self.start_time = None
        self.departure_time = None
        self.assigned_bed = None
        self.priority = None

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



def get_priority(patient_obj, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier):
    priority_score = age_multiplier * patient_obj.age + pre_existing_condition_multiplier * patient_obj.pre_existing_condition + corona_symptom_multiplier * patient_obj.corona_symptom


    return priority_score


def generate_patient_obj_list(patients, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier):
    patient_lst = []
    for i in range(0,len(patients)):
        current_patient = Patient(patients[i]["id"], patients[i]["query_time"], patients[i]["symptoms"], patients[i]["covid"], patients[i]["age"], patients[i]["conditions"], age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier)
        current_patient.priority = get_priority(current_patient, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier)
        patient_lst.append(current_patient)
    lst = sorted(patient_lst, key=lambda x: x.priority, reverse=True)
    return lst



def getWaitTime(patients, num_beds, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier):


    patient_lst = generate_patient_obj_list(patients, age_multiplier, pre_existing_condition_multiplier, corona_symptom_multiplier)
    
    final_patient_list = []
    current_time = patient_lst[0].query_time
    
    all_beds = Bed(queue.PriorityQueue(num_beds))

    for patient_index in range(len(patient_lst)):
        new_patient = patient_lst[patient_index]
        if not all_beds.check_full():
                # min_departure_time is the earliest departure time among
                # all people currently in all_beds
            new_patient.start_time = new_patient.query_time
        else:   
            min_departure_time = all_beds.get_remove_patient_dep()
            current_time = min_departure_time
            new_patient.start_time = max(new_patient.query_time, current_time)
        
        new_patient.departure_time = new_patient.start_time + 5
        all_beds.add_patient_dep(new_patient.departure_time)
        final_patient_list.append(new_patient)

    return final_patient_list

