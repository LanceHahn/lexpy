# -*- coding: utf-8 -*-
from psychopy import event, core, data, gui, visual
from fileHandling import *


class Experiment:
    def __init__(self, win_color, txt_color):
        self.prime_position = [0, .1]
        self.target_position = [0, -.1]
        self.fix_position = [0, 0]
        self.win_color = win_color
        self.txt_color = txt_color
        self.window = None
        self.nonword_key = 'm'
        self.realword_key = 'z'

    def create_window(self, color=(1, 1, 1)):
        # type: (object, object) -> object
        color = self.win_color
        win = visual.Window(monitor="testMonitor",
                            color=color, fullscr=True)
        self.window = win
        return

    def settings(self):
        experiment_info = {'Subid': '', 'Age': '', 'Experiment Version': 0.1,
                           'Gender': ['Male', 'Female', 'Other'],
                           'Language': ['English'], u'date':
                               data.getDateStr(format="%Y-%m-%d_%H:%M")}

        info_dialog = gui.DlgFromDict(title='Lexical task', dictionary=experiment_info,
                                      fixed=['Experiment Version'])
        experiment_info[u'DataFile'] = u'Data' + os.path.sep + u'ldtData.csv'

        if info_dialog.OK:
            return experiment_info
        else:
            core.quit()
            return 'Cancelled'

    def create_text_stimuli(self, text=None, pos=[0.0, 0.0], name='',
                            color=None):
        '''Creates a text stimulus,
        '''
        if color is None:
            color = self.txt_color
        text_stimuli = visual.TextStim(win=self.window, ori=0, name=name,
                                       text=text, font=u'Arial',
                                       pos=pos,
                                       color=color, colorSpace=u'rgb')
        return text_stimuli

    def create_trials(self, trial_file):
        '''Doc string'''
        data_types = ['Response', 'RT', 'Sub_id', 'Gender', 'TrialType']
        with open(trial_file, 'r') as stimfile:
            _stims = csv.DictReader(stimfile)
            trials = data.TrialHandler(list(_stims), 1,
                                       method="random")
        [trials.data.addDataType(data_type) for data_type in data_types]
        return trials

    def present_stimuli(self, color, text, position, stim):
        _stimulus = stim
        _stimulus.pos = position
        _stimulus.setColor(color)
        _stimulus.setText(text)
        return _stimulus

    def running_experiment(self, trials, testtype):
        _trials = trials
        testtype = testtype
        timer = core.Clock()
        stimuli = [self.create_text_stimuli(self.window) for _ in range(4)]

        for trial in _trials:
            # Fixation cross
            fixation = self.present_stimuli(self.txt_color, '+',
                                            self.fix_position,
                                            stimuli[3])
            fixation.draw()
            self.window.flip()
            core.wait(.6)
            timer.reset()

            # Prime word
            prime = self.present_stimuli(self.txt_color, trial['prime'],
                                          self.prime_position, stimuli[0])
            prime.draw()
            self.window.flip()
            core.wait(.6)
            timer.reset()

            # target
            target = self.present_stimuli(self.txt_color, trial['target'],
                                          self.target_position, stimuli[1])
            target.draw()
            self.window.flip()

            keys = event.waitKeys(keyList=['z', 'm', 'q'])
            resp_time = timer.getTime()
            interpetKey = "Nonword" if keys[0] == self.nonword_key else "Real"

            if testtype == 'practice':
                if interpetKey in trial['trialType']:
                    instruction_stimuli['right'].draw()
                else:
                    instruction_stimuli['incorrect'].draw()

                self.window.flip()
                core.wait(2)

            if testtype == 'test':
                if interpetKey in trial['trialType']:
                    trial['Accuracy'] = 1
                else:
                    trial['Accuracy'] = 0

                trial['RT'] = resp_time
                trial['Response'] = keys[0]
                trial['Sub_id'] = settings['Subid']
                trial['Gender'] = settings['Gender']
                write_csv(settings[u'DataFile'], trial)
            print(f"{trial['prime']},{trial['target']},"
                  f"{keys},{interpetKey}"
                  f",{interpetKey in trial['trialType']} "
                  f",{resp_time}")
            event.clearEvents()
            if 'q' in keys:
                print(f"breaking because keys: {keys}")
                break

    def close(self):
        self.window.close()
        return

def create_instructions_dict(instr):
    start_n_end = [w for w in instr.split() if w.endswith('START') or w.endswith('END')]
    keys = {}

    for word in start_n_end:
        key = re.split("[END, START]", word)[0]

        if key not in keys.keys():
            keys[key] = []

        if word.startswith(key):
            keys[key].append(word)
    return keys


def create_instructions(input, START, END, window=None, color="Black"):
    instruction_text = parse_instructions(input, START, END)
    print(instruction_text)
    text_stimuli = visual.TextStim(window, text=instruction_text, wrapWidth=1.2,
                                   alignHoriz='center', color=color,
                                   alignVert='center', height=0.06)

    return text_stimuli


def display_instructions(start_instruction='', window=None):
    # Display instructions

    if start_instruction == 'Practice':
        instruction_stimuli['instructions'].pos = (0.0, 0.5)
        instruction_stimuli['instructions'].draw()

        positions = [[0, .1], [0, -.1]]
        examples = [experiment.create_text_stimuli() for pos in positions]
        example_words = ['green', 'uble']
        for i, pos in enumerate(positions):
            examples[i].pos = pos
            if i == 0:
                examples[0].setText(example_words[i])
            elif i == 1:
                examples[1].setText(example_words[i])

        [example.draw() for example in examples]

        instruction_stimuli['practice'].pos = (0.0, -0.5)
        instruction_stimuli['practice'].draw()

    elif start_instruction == 'Test':
        instruction_stimuli['test'].draw()

    elif start_instruction == 'End':
        instruction_stimuli['done'].draw()

    window.flip()
    event.waitKeys(keyList=['space'])
    event.clearEvents()


def swedish_task(word):
    swedish = '+'
    if word == "blue":
        swedish = u"blå"
    elif word == "red":
        swedish = u"röd"
    elif word == "green":
        swedish = u"grön"
    elif word == "yellow":
        swedish = "gul"
    return swedish


if __name__ == "__main__":
    background = "Black"
    back_color = (0, 0, 0)
    textColor = "White"
    # text_color = (1, 1, 1)
    experiment = Experiment(win_color=background , txt_color=textColor)
    settings = experiment.settings()
    language = settings['Language']
    instructions = read_instructions_file("INSTRUCTIONS", language, language + "End")
    instructions_dict = create_instructions_dict(instructions)
    instruction_stimuli = {}

    window = experiment.create_window(color=back_color)

    for inst in instructions_dict.keys():
        instruction, START, END = inst, instructions_dict[inst][0], instructions_dict[inst][1]
        instruction_stimuli[instruction] = create_instructions(instructions, START, END,
                                                               window=experiment.window, color=textColor)

    # We don't want the mouse to show:
    event.Mouse(visible=False)
    # Practice Trials
    display_instructions(start_instruction='Practice', window=experiment.window)

    practice = experiment.create_trials('practice_list_LDT.csv')
    experiment.running_experiment(practice, testtype='practice')
    # Test trials
    display_instructions(start_instruction='Test', window=experiment.window)
    trials = experiment.create_trials('wordList.csv')
    experiment.running_experiment(trials, testtype='test')

    # End experiment but first we display some instructions
    display_instructions(start_instruction='End', window=experiment.window)
    experiment.close()
