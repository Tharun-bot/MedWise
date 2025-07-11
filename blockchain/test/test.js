const { expect } = require("chai");
const { ethers } = require("hardhat");


describe("MedWise", function () {
  let medWise, owner, patient, doctor;

  beforeEach(async () => {
    [owner, patient, doctor] = await ethers.getSigners();
    const MedWise = await ethers.getContractFactory("MedWise");
    medWise = await MedWise.deploy();
    await medWise.waitForDeployment(); // Instead of deployed()
    console.log("MedWise deployed to:", await medWise.getAddress());
  });

  it("should register a patient", async function () {
    await medWise.connect(patient).registerPatient("Alice", "alice@example.com", 25, "female");
    const data = await medWise.patients(patient.address);
    expect(data.exists).to.be.true;
    expect(data.name).to.equal("Alice");
  });

  it("should register a doctor", async function () {
    await medWise.connect(doctor).registerDoctor("Dr. Smith", "doc@example.com", "Cardiology");
    const doc = await medWise.doctors(doctor.address);
    expect(doc.exists).to.be.true;
    expect(doc.speciality).to.equal("Cardiology");
  });
  
  it("should let patient book an appointment", async function () {
    await medWise.connect(patient).registerPatient("Alice", "alice@example.com", 25, "female");
    await medWise.connect(doctor).registerDoctor("Dr. Smith", "doc@example.com", "Cardiology");

    const now = Math.floor(Date.now() / 1000) + 3600;
    await medWise.connect(patient).bookAppointment(doctor.address, "Headache", now);

    const appointment = await medWise.appointments(0);
    expect(appointment.patient).to.equal(patient.address);
    expect(appointment.status).to.equal(0); // Pending
  });

});
