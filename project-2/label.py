# Loop thru directories and collect image file names

# label
# read image
# classify image 
# recommendation

import os
    
def get_labels() -> list[dict]:
    furniture_path = './Furniture_Data'
    labels =  []
    for root, _, files in os.walk(furniture_path):
        for file in files:
            if file.endswith('.jpg'):
                
                path = os.path.join(root, file)
                dirs = path.split(os.path.sep)

                furniture = dirs[2][:-1] #Remove trailing `s` 
                style = dirs[3].lower() #lowercase

                label = {
                    'path': path,
                    'furniture': furniture,
                    'style': style
                }

                labels.append(label)
                print(path, furniture, style)

    return labels

labels = get_labels()
print(len(labels))
print(labels[0])