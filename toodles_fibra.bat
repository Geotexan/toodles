cd C:\Users\FabricaGeotexan\toodles
net use Z: \\192.168.1.29\sap /user:sap sapSAPkts /persistent:yes
pdm run python toodles.py daemon 1 COM3 Z:\fibra.txt 0
