import os
import sys
'''
sys.argv[1]
sys.argv[2]
sys.argv[3]
'''
par_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(par_dir)


for i in range(int(sys.argv[1]), int(sys.argv[2])):
    #print(i)        (1,4) 是 1，2，3   (0,10)
    os.system("python run_squad.py --predict_file=/home/yaliang/00_final/1.get_database/"+sys.argv[3]+"/test"+str(i)+".json")
    #os.system("python run_squad.py --predict_file=/home/yaliang/00_final/1.get_database/test/test"+str(i)+".json")