#usage: python attTTS.py txtfilename
#make sure the attTTSWav.wav file is there, along with a .txt file of the dialogue.

import httplib, urllib, sys, re, time, os, subprocess, wave, shutil

wavsList = []
wavfilename = sys.argv[1]+".wav"

def makettsresp(filename):
	infile = open(filename+'.txt', 'r')
	#cptext is the variable holding all the file's text
	cptext = infile.read().decode('utf8')
	infile.close()

	if not os.path.exists("./"+filename+"/"):
		os.makedirs("./"+filename+"/")

	#s is the regular expression for A1:, B5: etc.
	s = '[A-B]\d:'
	cptext = re.sub('\u2028', '', cptext)
	cptext = re.sub('\u2026', '', cptext)
	#this searches the text of the file for that regex, and splits on them all
	dtList = re.split(s, cptext)[1:]
	turn=0
	numchars=0
	for string in dtList:
		if turn%2==0:
			voice = 'crystal'
			letter = 'A'
		else:
			voice = 'mike'
			letter = 'B'
		time.sleep(5)
		#get the response
		tts_response = atts('POST', string.encode('utf8'), voice)
		timeincr=1
		while "RequestError" in tts_response:
			if "Rate limit" in tts_response:
				timeincr=timeincr+5
				print tts_response
				time.sleep(timeincr)
				print "incrementing time to "+str(timeincr)+"seconds..."
				tts_response = atts('POST', string.encode('utf8'), voice)
			else:
				sys.exit("issue with TTS response...probably best to stop and figure it out before ATT bans you...")

		#write response to wav file
		wavout = filename+"/"+filename+str((turn/2)+1)+letter+'.wav'
		outwav = open(wavout, 'w')
		outwav.write(tts_response)
		outwav.close()

		#write to list of wav paths to use for concatenation later...
		wavsList.append(filename+"/"+filename+str((turn/2)+1)+letter+'.wav')
		print "wavsList: "+str(wavsList)
		turn=turn+1
		continue

def atts(request_type, data, voice, OAuthToken="BF-ACSI~2~20150212053927~UQiNzAFXSuWwl7wFDBv40AgrWmcgGU9v"):
    """performs RESTful calls to ATT TTS API functions"""
    headers = {
    	"Authorization": "Bearer %s" % OAuthToken,
        "Content-type": "text/plain",
        "Accept": "audio/wav",
        "X-Arg": "VoiceName="+voice+",Volume=100",
        }
    conn = httplib.HTTPSConnection('api.att.com')
    conn.request(request_type,
        '/speech/v3/textToSpeech',
        data,
        headers,
        )
    response = conn.getresponse()
    return response.read()

def wavconcat(twoWavs, wavfilename):
	infiles = twoWavs
	outfile = wavfilename
	data= []
	for infile in infiles:
	    w = wave.open(infile, 'rb')
	    data.append( [w.getparams(), w.readframes(w.getnframes())] )
	    w.close()

	output = wave.open(outfile, 'wb')
	output.setparams(data[0][0])
	output.writeframes(data[0][1])
	output.writeframes(data[1][1])
	output.close()

makettsresp(sys.argv[1])
i=1
for wavFile in wavsList:
	if (i==1):
		wavconcat(["ATTttsWav.wav", wavFile], wavfilename)
	else:
		wavconcat([wavfilename, wavFile], wavfilename)
	i=i+1
shutil.rmtree(sys.argv[1]+'/')

