# Scoring
The Python script 'score.py' recreates how organizers will score user-generated routes against driver-taken routes during the competition's scoring phase. This allows users to check the performance of their in-progress models on their own machines and incorporate the logic into their models.

# Scoring Logic
The scoring function below calculates the similarity between the true driver-taken sequence and a user-submitted sequence. It combines elements of Sequence Deviation and Edit Distance with Real Penalty. The score of each user-submitted route is defined as follows:

$score = \displaystyle\frac{SD(A,B) \cdot {ERP}_{norm}(A,B)}{{ERP}_e(A,B)}$

where sequence $A$ is the historically realized sequence of deliveries, sequence $B$ is the algorithm-produced sequence of deliveries, $SD$ denotes the Sequence Deviation of $B$ with respect to $A$, $ERP_{norm}$ denotes the Edit Distance with Real Penalty applied to sequences $A$ and $B$ with normalized travel times, and ${ERP}_e$ denotes the number of edits prescribed by the $ERP$ algorithm on sequence $B$ with respect to $A$. If edit distance with real penalty prescribes 0 edits, then the above formula is replaced by the sequence deviation, multiplied by 0.

If a user-submitted route is deemed invalid -- meaning it does not provide a valid sequence that contains the station (as Stop 0) and all stops -- the route is given a score equivalent to a typical complete random perturbation of the driver-taken sequence. 

User-submitted sequences that perfectly match the driver-taken sequence are given a score of 0. Scores increase as the user-submitted sequence differs more and more from the driver-taken sequence. Complete random shuffles of all the stops in the driver-taken route typically receive scores betweeen 0.8 and 1.2.

The score for an entire submission is the simple, unweighted average of all route scores within the submission.

# 'Evaluate' Function
To incorporate the scoring logic into your own models, call the function 'evaluate' located within the score.py script and provide it the following inputs:

## Inputs
- actual_routes_json: the filepath of the JSON object that contains the sequence of historically-realized stops in the route, given as a string
- submission_json: the filepath of the JSON object that contains the sequence of stops generated by the user's model, given as a string
- cost_matrices_json: the filepath of the JSON object that contains the transit times between each stop in the route, given as a string
- invalid_scores_json: the filepath of the JSON object that contains the scores assigned to the user-submitted routes if they are deemed invalid, given as a string

All JSON files above may contain the necessary information corresponding to one or more routes. 

## Outputs
- scores: a python dictionary that contains the submission score, the scores assigned to each route, the feasibility of each route, and any inputted kwargs.

## Specifications of submission_json
- The submission_json file must have the same format as the actual_routes_json file (e.g actual_sequences.json), but it should have 'proposed' everywhere actual_routes_json has 'actual'.
- The route sequences your model ouputs in submission_json should begin but not end at the station. In other words, the station's stop number should be 0 and only 0. To match reality, in which a driver must return to the station after completing a route, the station will be automatically appended to the end of the route during the scoring process.