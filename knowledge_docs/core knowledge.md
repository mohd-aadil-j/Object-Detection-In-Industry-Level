problem:
an industry manufacture a component which like in image ./foxon/knowledge_docs/Nok.jpeg. In that sometimes the wires are saltered in worng seq or twisted when it comees to the which can be identified by the colors of the wires.
for this,
What I exactly need :
- It should be like a Software in the production line stations.
- In this software, the operator uploads a image, where there are four color wires were saltered.
- This software should verify the wire sequence is correctly saltered. 
- Ex: the expected seq. is - yellow, blue, black and red. the system should verify the status of the seq. saltered, if any mismatch it should indicate.
- the verification should take place like as I said below: 

     - Once the operator side or station camera start captiring the wires of the component which is saltered with some wires and the background in white, the system should plot three layers.
     - In each layer the system should plot the wires and extract its colors.
     - from the extracted colors it should make it as sequence for example, if the system reads the yellow color first and followed by blue, black and red, this should be a string like yellow - blue - black - red.
     - this extracted seq. should compare with operator given seq. which is knowns as expected seq.
     - if both are same, give positive indication and pass the component else give negative indication and send the components to rework.
     - we should store all the record irrespective of the result pass or rework. the components serial no., component name, result, tested time, tested operator Id and his/her name.
     - these all should be control with start, pause and stop button, once start or run is clicked the output should come like pass or rework. if stop pressed the process should be end completely. if pause is pressed the process should be tempreorily in hold, also the again the same pause is pressed the process should continue where it is stopped.

Note:

- There should be settings page where the operators can configuire the expected color seq., distance between layers.
- There always more than one color in the sequence so that should set by the operator dynamically.
- The RGB values also extract from the user choosen color.
- Results must include PASS, REWORK, and INSPECTION ERROR. INSPECTION ERROR is
  used when the system cannot find the number of wires configured by the operator.
- This should be a user-friendly software. every thing should be in Industry level standard.
- Use tech stack of React with JavaScript/JSX (not TypeScript) - MSSQL or local file storage, which can easily downloadable as well as accessible - Python(Django).
- Maintain the Architecture in the codebase : 
  - Avoid the unwanted codes and comments.
  - Use the comments where it essential.
  - Maintain seperate document for every layer of architecture frontend, backend and database.
  - The every changes should be update in each of the respective documents.
  - Gothourgh the project folder then start the implementation, wait for every next stage to my comfirmation.
  - Maintain this project properly in the github, the repo link ---> https://github.com/mohd-aadil-j/Object-Detection-In-Industry-Level.
  - push the code periodically with my conformation, with reasonable commits messages.


Now draft the implementation plan then start the immplementation once approve that else change that according to my later comments then start with my approval.