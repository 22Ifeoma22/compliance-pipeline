from openpyxl import Workbook

wb = Workbook()

# Sheet 1: ISO27001 Annex A
ws1 = wb.active
ws1.title = "ISO27001 Annex A"
ws1.append(["Control ID","Control Objective","Implementation","Audit Evidence","Required Action",
            "Gap Assessment","Progress Status","Compliance Score (%)"])
ws1.append(["A.5.1","Policies","Policy in place","Policy.docx","Annual review","Partial","In Progress",80])
ws1.append(["A.6.3","Training","Annual training","LMS export","Increase coverage","Yes","Not Started",65])
ws1.append(["A.8.12","Backups","Nightly backups","Backup logs","Quarterly restores","Partial","In Progress",92])

# Sheet 2: ISO27701 Annex A&B
ws2 = wb.create_sheet("ISO27701 Annex A&B")
ws2.append(["Control ID","Control Objective","Implementation","Audit Evidence","Required Action",
            "Gap Assessment","Progress Status","Compliance Score (%)"])
ws2.append(["PIMS-A.6.1","Lawful basis","RoPA updated","RoPA.xlsx","Review HR basis","Partial","In Progress",78])
ws2.append(["PIMS-A.7.3","DSARs","Portal live","DSAR.csv","Automate responses","Yes","Not Started",55])

wb.save("data/inputs/Tech_Compliance_DayToDay_Pack.xlsx")
print("Created data/inputs/Tech_Compliance_DayToDay_Pack.xlsx")
