import csv
import glob

mat=[]
with open("thesisDatasets/finalLoad.csv", "w") as output:
	writer=csv.writer(output, delimiter=',')
	writer.writerow(['Day', 'Hour', 'Grid output (kWh)'])
	fileCount=0
	for file in glob.glob("Data/*.csv"):
		with open(file, "r") as inputFile:
			print(file)
			reader=csv.reader(inputFile)
			rowCount=0
			#print(mat)
			for row in reader:
				if rowCount!=0 and fileCount==0:
					rowMat=[]
					rowMat.append(row[0])
					rowMat.append(row[1])
					rowMat.append(float(row[5]))
					mat.append(rowMat)
				elif rowCount!=0:
					#print(mat['row'+str(rowCount)][2])
					#print(rowCount)
					temp=mat[rowCount-1][2]
					temp+=float(row[5])
					mat[rowCount-1][2]=temp
				rowCount+=1
			print(len(mat))
		fileCount+=1

	for key in mat:
		writer.writerow(key)
