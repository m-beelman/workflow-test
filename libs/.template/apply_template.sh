# This script should crate a project folder in the libs directory.
# It should also copy the template files into the project folder.
# It should also change the project name in the CMakeLists.txt file.
# The project name in the CMakeLists.txt can be replaced with the help of the pattern $PROJECT_NAME_REPLACE$ withi the file. (search and replace)

# Check if the project name is given
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

#
# get the "Project name" value for following json '{"Project Name":"user-lib"} with jq and store it in the variable "project_name"
#
project_name=$(cat $1 | jq -r '.["Project Name"]')

echo "Project name: $project_name"

# Check if the project name is valid
if [[ ! $project_name =~ ^[a-zA-Z0-9_\-]+$ ]]
  then
    echo "Invalid project name"
    exit 1
fi

# Check if the project already exists
if [ -d "libs/$project_name" ]
  then
    echo "Project already exists"
    exit 1
fi

# Create the project folder
mkdir libs/$project_name

# Copy the template files into the project folder except the apply_template.sh file
cp -r libs/.template/* libs/$project_name
rm libs/$project_name/apply_template.sh


# Replace the project name in the CMakeLists.txt file
sed -i "s/PROJECT_NAME_REPLACE/$project_name/g" libs/$project_name/CMakeLists.txt

# add the project to the top level CMakeLists.txt (add_subdirectory)
echo "add_subdirectory(libs/$project_name)" >> CMakeLists.txt

