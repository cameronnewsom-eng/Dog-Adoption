# Dog Adoption Website
## Welcome
This is the start of a dog adoption website. When it first opens you can choose to have the adopters view or the employee view which have different functions (See the Adopt a Dog and Employee Portal sections).
## Tutorial
Download all the files and run app.py. Make sure that you have all the requirements to import the necessary libraries (See the Requirements section or the requirements.txt file). When the file first runs you will be directed to a page with two buttons, one to see the adopter point of view and one to see the employee point of view. Click on either and you should see a table with dogs.
If you see table headers but no table rows or dogs show up then run the create_dog_database.py file and relaunch app.py.
  ### Adopt a Dog
  All of the headers are interactive. For name a user can begin typing a name and as they type the rows will update to match the search.      The age column can sort by youngest or oldest. For breed the user selects all the breeds they want to look at. The dropdown menu only       shows breeds that are currently available based on other search parameters and the dogs in stock. Sex can sort by male or female.
  ### Employee Portal
  Similar to the Adopt a Dog menu all the headers are interactive. Now however there is an edit profile column with buttons to click to go    edit a profile.
    #### Edit Profile
    Users can type in new values and upload a new image. Some of the text boxes can be expanded downwards. When the user clicks submit          changes there submissions are checked. If they are all good then the submit button turns green. Otherwise the submit button will turn       red and all boxes with errors will have a red border.
    #### Add a dog
    Lets the user input info about a new dog. When they click save changes the button turns green and the dog is added to the database and      will now be shown to adopters. If any of there inputs were wrong when they set up the dog then the save changes button turns red and        all boxes with errors will have red backgrounds.
    #### Remove a dog
    All the edit profile buttons become delete buttons. If one gets checked the user if asked if they are sure. If they are the dog gets        deleted from the database and the image gets deleted from the folder. Users can click cancel to escape remove mode.
  ### Requirements
  blinker==1.9.0
  click==8.4.2
  Flask==3.1.3
  itsdangerous==2.2.0
  Jinja2==3.1.6
  MarkupSafe==3.0.3
  numpy==2.5.1
  pandas==3.0.5
  python-dateutil==2.9.0.post0
  six==1.17.0
  Werkzeug==3.1.8
## Areas for Continued Development
Updates are on their way! More changes will come to increase functionality.
1. The Adopt a Dog page will have buttons to adopt a dog, this will redirect a user to the dog's specific profile complete with a photo and description. The adopter can then choose to schedule a time to meet the dog in person or if they are really sure they can make a downpayment to put the dog on hold.
2. The Adopt a Dog page will have a link to take a short Dog Matcher quiz. Based on questions about the adopters lifestyle they will be matched with dogs who would fit.
3. The Employee Portal page will be updates so that the Adoption Status header functions like the Breed header allowing employees to search for dogs with specific adoption status's
4. The Adopt a Dog and Employee Edit Dog pages will both have an extra spot. (New column for Adopt a Dog and new box for Employee Edit Dog). This new spot is for Knows Tricks and will allow Employees to note what tricks a dog knows when they edit the dog and then Adopters will be able to search for dogs based on the tricks they know. This is so that adopters looking for dogs who already know sit can do so.
5. Large HTML/CSS updates to make the pages look better.
