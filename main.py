print('AutoMap V1')
import librosa
import pickle
import pd.concat, pd.DataFrame
a = input('Ultra hard? 1. Yes, 2. No')
name = input('Song Name:')
file = input('OGG File')
def get_features(song):
    y, sr = librosa.load(song)
    bpm, beat_frames = librosa.beat.beat_track(y=y,sr=sr,trim=False)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return bpm, beat_times, y, sr
def is_ultra_hard():
    if int(a) == 1:
        return True
    return False
def get_rate(diff):
    if diff == 'easy':
        if is_ultra_hard():
            rate = 2
        else:
            rate = 3
    elif diff == 'normal':
        if is_ultra_hard():
            rate = 1
        rate = 2
    else:
        rate = 0.5
def walk_to_df(walk):
    """Function for turning a Markov walk sequence into a DataFrame of note placement predictions"""
    sequence = []
    for step in walk:
        sequence.append(step.split(","))
    constant = ['notes_type_0', 'notes_lineIndex_0', 'notes_lineLayer_0',
                    'notes_cutDirection_0', 'notes_type_1', 'notes_lineIndex_1', 'notes_lineLayer_1', 
                    'notes_cutDirection_1', 'notes_type_3', 'notes_lineIndex_3',
                    'notes_lineLayer_3', 'notes_cutDirection_3']
    df = pd.DataFrame(sequence, columns = constant)
    return df
def write_level(notes_list,difficulty):
    """This function creates the 'level.dat' file that contains all the data for that paticular difficulty level"""
    
    level = {'_version': '2.0.0',
             '_customData': {'_time': '', #not sure what time refers to 
                             '_BPMChanges': [], 
                             '_bookmarks': []},
             '_events': events_list,
             '_notes': notes_list,
             '_obstacles': obstacles_list}
    
    with open(f"{difficulty}.dat", 'w') as f:
        json.dump(level, f)
def write_info(song,bpm):
    diffm = []
    for difficulty in diffs:
            difficulty_rank = None
            jump_movement = None
            if difficulty.casefold() == 'easy'.casefold():
                difficulty_rank = 1
                jump_movement = 8
                diff_name = 'Easy'
            elif difficulty.casefold() == 'normal'.casefold():
                difficulty_rank = 3
                jump_movement = 10
                diff_name = 'Normal'
            elif difficulty.casefold() == 'hard'.casefold():
                difficulty_rank = 5
                jump_movement = 12
                diff_name = 'Hard'
            elif difficulty.casefold() == 'expert'.casefold():
                difficulty_rank = 7
                jump_movement = 14
                diff_name = 'Expert'
            elif difficulty.casefold() == 'expertPlus'.casefold():
                difficulty_rank = 9
                jump_movement = 16
                diff_name = 'ExpertPlus'
            diff = {'_difficulty': diff_name,'_difficultyRank': difficulty_rank,'_beatmapFilename': f"{difficulty}.dat",'_noteJumpMovementSpeed': jump_movement,'_noteJumpStartBeatOffset': 0,'_customData': {}}
            diffm.append(diff)
    info = {'_version': '2.0.0',
        '_songName': f"{song_name}",
        '_songSubName': '',
        '_songAuthorName': '',
        '_levelAuthorName': 'BeatMapSynth',
        '_beatsPerMinute': round(bpm),
        '_songTimeOffset': 0,
        '_shuffle': 0,
        '_shufflePeriod': 0,
        '_previewStartTime': 10,
        '_previewDuration': 30,
        '_songFilename': 'song.egg',
        '_coverImageFilename': 'cover.jpg',
        '_environmentName': 'DefaultEnvironment',
        '_customData': {},
         '_difficultyBeatmapSets': [{'_beatmapCharacteristicName': 'Standard',
                                     '_difficultyBeatmaps': diffm}]}
diffs = ['easy','medium','hard','expert','expertPlus']
def write_song(beatl):
    models = {}
    notelists = []
    for i in ['easy','medium','hard','expert','expertPlus']:
        model = pickle.load('HMM_{}_v2.pkl','rb')
        models[i] = model
    model_rate = {}
    for i in models:
        model_rate[i] = get_rate(i)
    counter = 2
    beats = []
    outs = []
    for i in models:
        while counter <= len(beatl):
            beats.append(counter)
            counter += rate
        random_walk = models[i].walk()
        while len(random_walk) < len(beats):
            random_walk = models[i].walk()
        df_walk = walk_to_df(random_walk)
        df_preds = pd.concat([pd.DataFrame(beats,columns = ['_time']), df_walk], axis = 1, sort = True)
        df_preds.dropna(axis = 0, inplace = True)
        #Write notes dictionaries
        notes_list = []
        for index, row in df_preds.iterrows():
            for x in list(filter(lambda y: y.startswith('notes_type'), df_preds.columns)):
                if row[x] != '999':
                    num = x[-1]
                    note = {'_time': row['_time'],
                            '_lineIndex': int(row[f"notes_lineIndex_{num}"]),
                            '_lineLayer': int(row[f"notes_lineLayer_{num}"]),
                            '_type': num,
                            '_cutDirection': int(row[f"notes_cutDirection_{num}"])}
                    notes_list.append(note)
        for i, x in enumerate(notes_list):
            if notes_list[i]['_time'] >= 0 and notes_list[i]['_time'] <= 1.5:
                del notes_list[i]
            elif notes_list[i]['_time'] > beats[-1]:
                del notes_list[i]

        notelists.append(notes_list)
    return notelists
def export_map(music,name,diff):
    bpm, beat_times, y, sr = beat_features(music)
    beat_times = [x*(bpm/60) for x in beat_times]
    notes_list = HMM_notes_writer(beat_times)
    write_info(song_name, bpm)
    for i in range(5):
        write_level(notes_list[i],diffs)
    
    
    
