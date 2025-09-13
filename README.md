A Python script that takes a SW Maps project csv and converts it to Emlid project CSV in order to use in Emlid Studio Stop and Go PPK processing.

Run the .py file in python, select the input project csv (SW Maps project csv export format) and enter a name for the exported Emlid CSV project file.

Currently, the output is hard coded to use meters as the antenna height unit. 

Also, SW Maps does not appear to output the time stamps for averaged point records, so I have hardcoded the Emlid csv to just state 1 sample over 4 seconds average. IE, whatever SW Maps records as an average is all that is available as a fixed point if using averaging (so, use averaging with caution) 
