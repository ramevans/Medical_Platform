Medical platfrom includes a speech-to-text where users can submit an audio file to be analyzed. 
The speech-to-text service is built using Mozilla’s DeepSpeech project.
 - this api extract text from the given audio file. The audio file passed in should can be in any format that librosa understand. 
 - Librosa will read and resample the file as necessary before passing it to DeepSpeech for text extraction.
