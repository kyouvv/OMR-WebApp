dict = {1 : 'test', 2 : '3', 3 : 'testui'}

for i in range(len(dict)):
    print(dict[i + 1])


# initialising dictionaries
ini_dictionary1 = {'nikhil': 1, 'akash' : 5, 'manjeet' : 10, 'akshat' : 15}
ini_dictionary2 = {'akash' : 7, 'akshat' : 5, 'm' : 15}
 
# printing initial dictionaries
print ("initial 1st dictionary", str(ini_dictionary1))
print ("initial 2nd dictionary", str(ini_dictionary2))
 
# combining dictionaries using merge operator
merged_dict = {**ini_dictionary1, **ini_dictionary2}
final_dict = {}
for key, value in merged_dict.items():
    final_dict[key] = final_dict.get(key, 0) + value

print ("final dictionary", str(final_dict))