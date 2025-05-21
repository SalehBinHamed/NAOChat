from src.Talker import LocalTalker, TerminalTalker
from src.Chatter import Chatter
from src.Listener import Listener
from src.NAO.NAOTalker import NAOTalker
from src.NAO.ChoregrapheTalker import ChoregrapheTalker
import warnings, yaml, sys, os, time
conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"configs")
kwargs = {key.lower() : value for key, value in [a.split("=") for a in sys.argv[1:]]}
base_params = yaml.safe_load(open(os.path.join(conf_path, "base_params.yaml"))) # Used to identify correct type of parameters

config = kwargs.get("config", "default")
if os.path.isfile(os.path.join(conf_path, config + ".yaml")):
    params = yaml.safe_load(open(os.path.join(conf_path, config + ".yaml")))
elif os.path.isfile(os.path.join(conf_path, "local", config + ".yaml")):
    params = yaml.safe_load(open(os.path.join(conf_path, "local", config + ".yaml")))
else:
    raise Exception("Can't find {}.yaml in configs or configs/local".format(config))
# Overwrite any parameters set during call. Take types from: current config or base_params if not included
for k,v in kwargs.items():
    if k in params: params[k] = type(params[k])(v)
    elif k in base_params: 
        params[k] = type(base_params[k])(v)
    elif not k == "config": warnings.warn("Parameter {} was not found in {} or identifed as a base parameter. Ignoring".format(k, config))

# Set up chatter
if "filt_keys" in params: # Format any parameterised filter keys (such as {name})
    for i, key in enumerate(params["filt_keys"]):
        params["filt_keys"][i] = key.format(**params)
chatter = Chatter(
    chat_prompt=params["chat_prompt"].format(**params),
    chat_horison=params.get("chat_horison",10),
    chat_tokens=params.get("chat_tokens",100),
    temp=params.get("temp",0.5),
    stream=params.get("stream",False),
    filt_prompt=params["filt_prompt"].format(**params) if params.get("filt_horizon",0) > 0 else "",
    filt_horizon=params.get("filt_horizon",0),
    filt_name=params.get("filt_name", "assistant").format(**params),
    filt_keys=params["filt_keys"] if params.get("filt_horizon",0) > 0 else "",
    filt_tokens=params.get("filt_tokens",5),
    chat_name=params.get("name", "assistant").format(**params)
)

# Set up talker
talker_type = params["talker"].lower()
if talker_type == "terminal":
    talker = TerminalTalker(
        language=params.get("language","en"),
        prefix=params.get("terminal_talker_prefix", "\nAssistant: ").format(**params)
    )
elif talker_type == "speaker":
    talker = LocalTalker(
        language=params.get("language","en")
    )
elif talker_type == "nao":
    talker = NAOTalker(
        ip=params["ip"],
        language=params.get("language","en"),
        stand=params.get("nao_stand",False),
        sleep_len=params.get("nao_sleep_len",0.03),
        volume=params.get("nao_volume",100)
    )
elif talker_type == "choregraphe":
    talker = ChoregrapheTalker(
        ip=params["ip"],
        language=params.get("language","en"),
        stand=params.get("nao_stand",False),
        sleep_len=params.get("nao_sleep_len",0.03),
        volume=params.get("nao_volume",100)
    )
else:
    raise Exception("Incorrect 'talker' specified! Use 'terminal', 'speaker', 'NAO', or 'choregraphe'")

# Set up listener
listener_type = params["listener"].lower()
if listener_type == "mic":
    listener = Listener(
        language=params.get("language","en"),
        default_mic=params.get("default_mic",True),
        use_whisper=params.get("use_whisper",False)
    )
elif listener_type == "terminal":
    listener = lambda : input(params.get("terminal_listener_prefix","User: "))
elif listener_type == "timer":
    listener = lambda : [time.sleep(params["listener_timer_delay"]), params.get("listener_timer_message", " ")][1]
else:
    raise Exception("Incorrect 'listener' specified! Use 'terminal', 'timer' or 'mic'.")

# Start conversation
try:
    # Test mode with single "hello" message if test parameter is set
    if params.get("test", False):
        print("TEST MODE: NAO will say 'hello' and then exit")
        response = chatter("hello")
        talker("hello")
        sys.exit()
    
    while True:
        if params.get("print_listening", True): print(params.get("print_listening", "Listening..."))
        heard = listener()
        if params.get("print_heard", True): print("Heard: {}".format(heard))
        if heard != "":
            response = chatter(heard)
            talker(response)
except (KeyboardInterrupt, EOFError):
    print("\n\nExiting...")
    sys.exit()