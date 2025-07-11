pragma solidity ^0.8.0;


contract MedWise {
    enum status {Pending, Approved, Rejected}

    struct Patient {
        string name; 
        string email;
        uint age;
        string gender;
        bool exists;
    }
    struct Doctor {
        string name;
        string email;
        string speciality;
        bool exists;
    }
    struct Appointment {
        uint id;
        address patient;
        address doctor;
        string symptoms;
        uint timestamp;
        status status;
    }
    
    mapping(address => Patient) public patients;
    mapping(address => Doctor) public doctors;
    mapping(uint => Appointment) public appointments;

    //access control mapping
    mapping(address => mapping(address => bool)) public patientToDoctor;

    uint public appointmentCount;

    //events
    event PatientRegistered(address doctorID, string name);
    event DoctorRegistered(address patientID, string name);
    event AppointmentBooked(uint id, address indexed patient, address indexed doctor);
    event AppointmentApproved(uint id);
    event AppointmentRejected(uint id);
    event AccessGranted(address indexed patient, address indexed doctor);
    event AccessRevoked(address indexed patient, address indexed doctor);

    modifier onlyPatient() {
        require(patients[msg.sender].exists, "Not a registered patient");
        _;
    }

    modifier onlyDoctor() {
        require(doctors[msg.sender].exists, "Not a registered doctor");
        _;
    }
    
    //registers doctors
    function registerPatient(
        string memory _name,
        string memory _email,
        uint _age,
        string memory _gender
    ) public {
        require(!patients[msg.sender].exists, "Already registered as patient");
        patients[msg.sender] = Patient(_name, _email, _age, _gender, true);
        emit PatientRegistered(msg.sender, _name);
    }


    //registers patients
    function registerDoctor(
        string memory _name,
        string memory _email,
        string memory _specialty
    ) public {
        require(!doctors[msg.sender].exists, "Already registered as doctor");
        doctors[msg.sender] = Doctor(_name, _email, _specialty, true);
        emit DoctorRegistered(msg.sender, _name);
    }

    //book appointment - called by patients only
    function bookAppointment(
        address _doctor,
        string memory _symptom, 
        uint _timestamp
    ) public onlyPatient {
        require(doctors[_doctor].exists, "Doctor not found");

        appointments[appointmentCount] = Appointment(appointmentCount, msg.sender, _doctor, _symptom, _timestamp, status.Pending);
        emit AppointmentBooked(appointmentCount, msg.sender, _doctor);
        appointmentCount++;
    }

    //approve appointment - called by doctors only
    function approveAppointment(uint _appointmentID) public onlyDoctor {
        Appointment storage appointment = appointments[_appointmentID];
        require(appointment.doctor == msg.sender, "Not your appointment");
        require(appointment.status == status.Pending, "Already handled");

        appointment.status = status.Approved;
        emit AppointmentApproved(_appointmentID);
    }

    //reject appointment - called by doctors only
    function rejectAppointment(uint _appointmentID) public onlyDoctor {
        Appointment storage appointment = appointments[_appointmentID];
        require(appointment.doctor == msg.sender, "Not your appointment");
        require(appointment.status == status.Pending, "Already handled");

        appointment.status = status.Rejected;
        emit AppointmentRejected(_appointmentID);
    }

    //view appointments - for both doctor and patient
    function viewAppointment(uint _appointmentID) public view returns (
        address patient,
        address doctor,
        string memory symptoms,
        uint timestamp,
        status _status
    ) {
       Appointment memory appointment = appointments[_appointmentID]; 
       return (
            appointment.patient,
            appointment.doctor,
            appointment.symptoms,
            appointment.timestamp,
            appointment.status
       );
    }

    //view patient - called by doctor
    function viewPatient(address _patient) public view returns (
        string memory name,
        string memory email, 
        uint age,
        string memory gender
    ) {
        require(patients[_patient].exists, "Patient not found");
        require(patientToDoctor[_patient][msg.sender], "No permission to access patient details");
        Patient memory patient = patients[_patient];
        return (patient.name, patient.email, patient.age, patient.gender);
    }

    //view doctor - called by patient
    function viewDoctor(address _doctor) public view returns (
        string memory name,
        string memory email,
        string memory speciality
    ) {
        require(doctors[_doctor].exists, "Doctor not Found");
        Doctor memory doctor = doctors[_doctor];
        return (doctor.name, doctor.email, doctor.speciality);
    }

    //grant access
    function grantAccess(address _doctor) public onlyPatient {
        require(doctors[_doctor].exists, "Not a registered doctor");
        patientToDoctor[msg.sender][_doctor] = true;
        emit AccessGranted(msg.sender, _doctor);
    }

    //revoke access
    function revokeAccess(address _doctor) public onlyPatient {
        require(doctors[_doctor].exists, "Not a registered doctor");
        patientToDoctor[msg.sender][_doctor] = false;
        emit AccessRevoked(msg.sender, _doctor);
    }

    //check access
    function hasAccess(address _patient, address _doctor) public view returns (bool) {
    return patientToDoctor[_patient][_doctor];

}

    
}