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
