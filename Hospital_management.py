def input_valid_int(msg, start = 0, end = None):
    # keep iterating till the given input is valid
    # hidden assumption: both start and end either value or none. That is bad
    while True:
        inp = input(msg)

        if not inp.isdecimal():
            print('Invalid input. Try again!')
        elif start is not None and end is not None:
            if not (start <= int(inp) <= end):
                print('Invalid range. Try again!')
                # another way is to check if int(inp) in range(start, end+1)
            else:
                return int(inp)
        else:
            return int(inp)


class Patient:
    def __init__(self, name, status):
        self.name, self.status = name, status

    def __str__(self):
        status = ['Normal', 'Urgent', 'Super Urgent'][self.status]
        return f'Patient: {self.name} is {status}'

    def __repr__(self):
        return F'Patient(name="{self.name}", status={self.status})'

    def __lt__(self, other):    # see: def add_patient_smart
        return self.status > other.status   # given 2 patients: which one comes first? one with bigger status


# Observe. In this manager, there is only logic
# All interaction with user (read/write) are at the front end
class HospitalManger:
    def __init__(self, specializations_cnt):
        self.specializations = [[] for s in range(specializations_cnt)]
        self.MAX_QUEUE = 10
        self.NORMAL = 0
        self.URGENT = 1
        self.SUPER_URGENT = 2

    def can_add_more_patients(self, specialization):
        return len(self.specializations[specialization]) < self.MAX_QUEUE

    def add_patient_smart(self, specialization, name, status): # ignore for now or google
        spec = self.specializations[specialization]
        spec.append(Patient(name, status))  # Add at end
        spec.sort() # in-place sort based on large status first. it preserves the old order!
        # as python don't know how to compare objects (which comes first), you need to add __lt__

    def add_patient(self, specialization, name, status):
        spec = self.specializations[specialization]
        pat = Patient(name, status)

        if status == 0 or len(spec) == 0:           # Add normal
            spec.append(pat)      # Add at end
        elif status == 1:   # Add urgent
            # Add before the normal patients, but after current urgents / super-urgents
            if spec[-1].status != self.NORMAL:      # if no normals, then it should be added after the end
                spec.append(pat)
            else:   # Find the first normal and add before it
                for idx, patient in enumerate(spec):
                    if patient.status == self.NORMAL:
                        spec.insert(idx, pat)
                        break
        else:
            # Add before the normal or urgent patients, but after current super-urgents
            if spec[-1].status == self.SUPER_URGENT:      # if all are super urgent, just add at the end
                spec.append(pat)
            else:   # Find the first normal/urgent and add before it
                for idx, patient in enumerate(spec):
                    if patient.status == self.NORMAL or patient.status == self.URGENT:
                        spec.insert(idx, pat)
                        break

    def get_printable_patients_info(self):
        results = []    # send back results to front end to print on its way
        for idx, specialization in enumerate(self.specializations):
            if not specialization:
                continue
            cur_patients = []
            for patient in specialization:
                cur_patients.append(str(patient))
            results.append((idx, cur_patients))
        return results

    def get_next_patients(self, specialization):
        if len(self.specializations[specialization]) == 0:
            return None
        return self.specializations[specialization].pop(0)

    def remove_patient(self, specialization, name):
        spec = self.specializations[specialization]
        for idx, patient in enumerate(spec):
            if patient.name == name:
                del spec[idx]
                return True
        return False


class FrontendManager:
    def __init__(self, specializations_cnt = 20):
        self.specializations_cnt = specializations_cnt
        self.hospital_manger = HospitalManger(self.specializations_cnt)
        self.add_dummy_data()

    def print_menu(self):
        print('\nProgram Options:')
        messages = [
            'Add new patient',
            'Print all patients',
            'Get next patient',
            'Remove a leaving patient',
            'End the program'
        ]
        # let's add the order 1 2 3 4...
        messages = [f'{idx+1}) {msg}' for idx, msg in enumerate(messages)]
        print('\n'.join(messages))
        msg = f'Enter your choice (from 1 to {len(messages)}): '
        return input_valid_int(msg, 1, len(messages))

    def add_dummy_data(self):
        for i in range(10):
            self.hospital_manger.add_patient(2, 'Dummy' + str(i), i % 3)
        for i in range(4):
            self.hospital_manger.add_patient(5, 'AnotherDummy' + str(i), 0)
        for i in range(5):
            self.hospital_manger.add_patient(8, 'ThirdDummy' + str(i), 1)
        for i in range(3):
            self.hospital_manger.add_patient(12, 'ForthDummy' + str(i), 2)
        for i in range(3):
            self.hospital_manger.add_patient(13, 'FifthDummy' + str(i), 1)
            self.hospital_manger.add_patient(13, 'FifthDummy' + str(i+5), 2)

    def run(self):
        while True:
            choice = self.print_menu()
            if choice == 1:
                specialization = input_valid_int('Enter specialization: ', 1, self.specializations_cnt) - 1

                if self.hospital_manger.can_add_more_patients(specialization):
                    name = input('Enter patient name: ')
                    status = input_valid_int('Enter status (0 normal / 1 urgent / 2 super urgent): ', 0, 2)
                    self.hospital_manger.add_patient(specialization, name, status)
                else:
                    print("Sorry we can't add more patients for this specialization at the moment.")
            elif choice == 2:
                results = self.hospital_manger.get_printable_patients_info()
                if not results:
                    print('No patients at the moment')
                else:
                    for idx, patients_info in results:
                        print(f'Specialization {idx+1}: There are {len(patients_info)} patients.')
                        print("\n".join(patients_info) + '\n')
            elif choice == 3:
                specialization = input_valid_int('Enter specialization: ', 1, self.specializations_cnt) - 1
                patient = self.hospital_manger.get_next_patients(specialization)

                if patient is None:
                    print('No patients at the moment. Have rest, Dr')
                else:
                    print(f'{patient.name}, Please go with the Dr')
            elif choice == 4:
                specialization = input_valid_int('Enter specialization: ', 1, self.specializations_cnt) - 1
                name = input('Enter patient name: ')
                if not self.hospital_manger.remove_patient(specialization, name):
                    print('No patient with such a name in this specialization!')
            else:
                break


if __name__ == '__main__':
    app = FrontendManager()
    app.run()
