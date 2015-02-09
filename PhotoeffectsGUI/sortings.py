def mergeSortScore(alist):
		if len(alist)>1:
			mid = len(alist)//2
			lefthalf = alist[:mid]
			righthalf = alist[mid:]
			mergeSortScore(lefthalf)
			mergeSortScore(righthalf)

			i=0
			j=0
			k=0
			while i<len(lefthalf) and j<len(righthalf):
				if lefthalf[i][0]>righthalf[j][0]:
					alist[k]=lefthalf[i]
					i=i+1
				else:
					alist[k]=righthalf[j]
					j=j+1
				k=k+1
			while i<len(lefthalf):
				alist[k]=lefthalf[i]
				i=i+1
				k=k+1
			while j<len(righthalf):
				alist[k]=righthalf[j]
				j=j+1
				k=k+1

def mergeSortFaces(alist):
		if len(alist)>1:
			mid = len(alist)//2
			lefthalf = alist[:mid]
			righthalf = alist[mid:]
			mergeSortFaces(lefthalf)
			mergeSortFaces(righthalf)

			i=0
			j=0
			k=0
			while i<len(lefthalf) and j<len(righthalf):
				if lefthalf[i].getID()>righthalf[j].getID():
					alist[k]=lefthalf[i]
					i=i+1
				else:
					alist[k]=righthalf[j]
					j=j+1
				k=k+1
			while i<len(lefthalf):
				alist[k]=lefthalf[i]
				i=i+1
				k=k+1
			while j<len(righthalf):
				alist[k]=righthalf[j]
				j=j+1
				k=k+1
