"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: persona.py
Description: Defines the Persona class that powers the agents in Reverie. 

Note (May 1, 2023) -- this is effectively GenerativeAgent class. Persona was
the term we used internally back in 2022, taking from our Social Simulacra 
paper.
"""
import math
import sys
import datetime
import random
sys.path.append('../')

from global_methods import *

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *

from persona.cognitive_modules.perceive import *
from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.converse import *

class Persona: 
  def __init__(self, name, folder_mem_saved=False):
    # PERSONA BASE STATE 
    # <name> is the full name of the persona. This is a unique identifier for
    # the persona within Reverie. 
    self.name = name

    # PERSONA MEMORY 
    # If there is already memory in folder_mem_saved, we load that. Otherwise,
    # we create new memory instances. 
    # <s_mem> is the persona's spatial memory. 
    f_s_mem_saved = f"{folder_mem_saved}/bootstrap_memory/spatial_memory.json"
    self.s_mem = MemoryTree(f_s_mem_saved)
    # <s_mem> is the persona's associative memory. 
    f_a_mem_saved = f"{folder_mem_saved}/bootstrap_memory/associative_memory"
    self.a_mem = AssociativeMemory(f_a_mem_saved)
    # <scratch> is the persona's scratch (short term memory) space. 
    scratch_saved = f"{folder_mem_saved}/bootstrap_memory/scratch.json"
    self.scratch = Scratch(scratch_saved)


  def save(self, save_folder): 
    """
    Save persona's current state (i.e., memory). 

    INPUT: 
      save_folder: The folder where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    # Spatial memory contains a tree in a json format. 
    # e.g., {"double studio": 
    #         {"double studio": 
    #           {"bedroom 2": 
    #             ["painting", "easel", "closet", "bed"]}}}
    f_s_mem = f"{save_folder}/spatial_memory.json"
    self.s_mem.save(f_s_mem)
    
    # Associative memory contains a csv with the following rows: 
    # [event.type, event.created, event.expiration, s, p, o]
    # e.g., event,2022-10-23 00:00:00,,Isabella Rodriguez,is,idle
    f_a_mem = f"{save_folder}/associative_memory"
    self.a_mem.save(f_a_mem)

    # Scratch contains non-permanent data associated with the persona. When 
    # it is saved, it takes a json form. When we load it, we move the values
    # to Python variables. 
    f_scratch = f"{save_folder}/scratch.json"
    self.scratch.save(f_scratch)

  def save_conspiracy_belief(self, conspiracy_theory, rating, explanation, requested_by="user"):
    import datetime, json, os

    beliefs_file = f"{self.folder_mem_saved}/bootstrap_memory/conspiracy_beliefs.json"

    if os.path.exists(beliefs_file):
      with open(beliefs_file, 'r') as f:
        beliefs = json.load(f)
    else:
      beliefs = {"theories": {}}

    if conspiracy_theory not in beliefs["theories"]:
      beliefs["theories"][conspiracy_theory] = []

    new_rating = {
      "rating": rating,
      "explanation": explanation,
      "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      "requested_by": requested_by
    }
    beliefs["theories"][conspiracy_theory].append(new_rating)
    beliefs["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(beliefs_file, 'w') as f:
      json.dump(beliefs, f, indent=2)

    return beliefs

  def load_conspiracy_beliefs(self):
    import json, os

    beliefs_file = f"{self.folder_mem_saved}/bootstrap_memory/conspiracy_beliefs.json"

    if not os.path.exists(beliefs_file):
      return None

    with open(beliefs_file, 'r') as f:
      return json.load(f)

  @staticmethod
  def get_all_theories_in_simulation(sim_folder):
    from collections import Counter
    import os, json

    theories = Counter()

    personas_path = f"{sim_folder}/personas"
    if os.path.exists(personas_path):
      for persona_name in os.listdir(personas_path):
        if persona_name.startswith('.'):
          continue

        beliefs_file = f"{personas_path}/{persona_name}/bootstrap_memory/conspiracy_beliefs.json"
        if os.path.exists(beliefs_file):
          with open(beliefs_file, 'r') as f:
            beliefs = json.load(f)
            for theory in beliefs.get("theories", {}).keys():
              theories[theory] += 1

    return dict(theories)

  def auto_rate_all_theories(self, all_theories):
    """
    Automatically rate all existing theories for this persona.
    Called at end of each simulation step to update beliefs.
    """
    import json, os
    from persona.cognitive_modules.converse import interview_conspiracy_belief
    
    # Load existing beliefs
    beliefs_file = f"{self.folder_mem_saved}/bootstrap_memory/conspiracy_beliefs.json"
    
    if os.path.exists(beliefs_file):
      with open(beliefs_file, 'r') as f:
        beliefs = json.load(f)
    else:
      beliefs = {"theories": {}}
    
    # Rate any theories that exist in simulation but not yet rated by this persona
    new_ratings = []
    for theory in all_theories:
      if theory not in beliefs["theories"]:
        # Only rate if this persona hasn't rated this theory yet
        try:
          result = interview_conspiracy_belief(self, theory, save=True)
          new_ratings.append({
            "theory": theory,
            "rating": result["rating"],
            "explanation": result["explanation"]
          })
        except Exception as e:
          # Log error but don't crash simulation
          print(f"Error auto-rating {self.name} on '{theory}': {e}")
          continue
    
    # Also re-rate previously rated theories periodically (every 10 steps)
    # This allows beliefs to evolve over time
    for theory, ratings in beliefs.get("theories", {}).items():
      if len(ratings) > 0 and self.step % 10 == 0:
        last_rating = ratings[-1]["rating"]
        try:
          result = interview_conspiracy_belief(self, theory, save=True)
          # Only update if rating changed significantly (>1 point)
          if abs(result["rating"] - last_rating) > 1:
            new_ratings.append({
              "theory": theory,
              "old_rating": last_rating,
              "new_rating": result["rating"]
            })
        except Exception as e:
          print(f"Error re-rating {self.name} on '{theory}': {e}")
          continue
    
    return new_ratings






  def perceive(self, maze):
    """
    This function takes the current maze, and returns events that are 
    happening around the persona. Importantly, perceive is guided by 
    two key hyper-parameter for the  persona: 1) att_bandwidth, and 
    2) retention. 

    First, <att_bandwidth> determines the number of nearby events that the 
    persona can perceive. Say there are 10 events that are within the vision
    radius for the persona -- perceiving all 10 might be too much. So, the 
    persona perceives the closest att_bandwidth number of events in case there
    are too many events. 

    Second, the persona does not want to perceive and think about the same 
    event at each time step. That's where <retention> comes in -- there is 
    temporal order to what the persona remembers. So if the persona's memory
    contains the current surrounding events that happened within the most 
    recent retention, there is no need to perceive that again. xx

    INPUT: 
      maze: Current <Maze> instance of the world. 
    OUTPUT: 
      a list of <ConceptNode> that are perceived and new. 
        See associative_memory.py -- but to get you a sense of what it 
        receives as its input: "s, p, o, desc, persona.scratch.curr_time"
    """
    return perceive(self, maze)


  def retrieve(self, perceived):
    """
    This function takes the events that are perceived by the persona as input
    and returns a set of related events and thoughts that the persona would 
    need to consider as context when planning. 

    INPUT: 
      perceive: a list of <ConceptNode> that are perceived and new.  
    OUTPUT: 
      retrieved: dictionary of dictionary. The first layer specifies an event,
                 while the latter layer specifies the "curr_event", "events", 
                 and "thoughts" that are relevant.
    """
    return retrieve(self, perceived)


  def plan(self, maze, personas, new_day, retrieved):
    """
    Main cognitive function of the chain. It takes the retrieved memory and 
    perception, as well as the maze and the first day state to conduct both 
    the long term and short term planning for the persona. 

    INPUT: 
      maze: Current <Maze> instance of the world. 
      personas: A dictionary that contains all persona names as keys, and the 
                Persona instance as values. 
      new_day: This can take one of the three values. 
        1) <Boolean> False -- It is not a "new day" cycle (if it is, we would
           need to call the long term planning sequence for the persona). 
        2) <String> "First day" -- It is literally the start of a simulation,
           so not only is it a new day, but also it is the first day. 
        2) <String> "New day" -- It is a new day. 
      retrieved: dictionary of dictionary. The first layer specifies an event,
                 while the latter layer specifies the "curr_event", "events", 
                 and "thoughts" that are relevant.
    OUTPUT 
      The target action address of the persona (persona.scratch.act_address).
    """
    return plan(self, maze, personas, new_day, retrieved)


  def execute(self, maze, personas, plan):
    """
    This function takes the agent's current plan and outputs a concrete 
    execution (what object to use, and what tile to travel to). 

    INPUT: 
      maze: Current <Maze> instance of the world. 
      personas: A dictionary that contains all persona names as keys, and the 
                Persona instance as values. 
      plan: The target action address of the persona  
            (persona.scratch.act_address).
    OUTPUT: 
      execution: A triple set that contains the following components: 
        <next_tile> is a x,y coordinate. e.g., (58, 9)
        <pronunciatio> is an emoji.
        <description> is a string description of the movement. e.g., 
        writing her next novel (editing her novel) 
        @ double studio:double studio:common room:sofa
    """
    return execute(self, maze, personas, plan)


  def reflect(self):
    """
    Reviews the persona's memory and create new thoughts based on it. 

    INPUT: 
      None
    OUTPUT: 
      None
    """
    reflect(self)


  def move(self, maze, personas, curr_tile, curr_time):
    """
    This is the main cognitive function where our main sequence is called. 

    INPUT: 
      maze: The Maze class of the current world. 
      personas: A dictionary that contains all persona names as keys, and the 
                Persona instance as values. 
      curr_tile: A tuple that designates the persona's current tile location 
                 in (row, col) form. e.g., (58, 39)
      curr_time: datetime instance that indicates the game's current time. 
    OUTPUT: 
      execution: A triple set that contains the following components: 
        <next_tile> is a x,y coordinate. e.g., (58, 9)
        <pronunciatio> is an emoji.
        <description> is a string description of the movement. e.g., 
        writing her next novel (editing her novel) 
        @ double studio:double studio:common room:sofa
    """
    # Updating persona's scratch memory with <curr_tile>. 
    self.scratch.curr_tile = curr_tile

    # We figure out whether the persona started a new day, and if it is a new
    # day, whether it is the very first day of the simulation. This is 
    # important because we set up the persona's long term plan at the start of
    # a new day. 
    new_day = False
    if not self.scratch.curr_time: 
      new_day = "First day"
    elif (self.scratch.curr_time.strftime('%A %B %d')
          != curr_time.strftime('%A %B %d')):
      new_day = "New day"
    self.scratch.curr_time = curr_time

    # Main cognitive sequence begins here. 
    perceived = self.perceive(maze)
    retrieved = self.retrieve(perceived)
    plan = self.plan(maze, personas, new_day, retrieved)
    self.reflect()

    # <execution> is a triple set that contains the following components: 
    # <next_tile> is a x,y coordinate. e.g., (58, 9)
    # <pronunciatio> is an emoji. e.g., "\ud83d\udca4"
    # <description> is a string description of the movement. e.g., 
    #   writing her next novel (editing her novel) 
    #   @ double studio:double studio:common room:sofa
    return self.execute(maze, personas, plan)


  def open_convo_session(self, convo_mode): 
    open_convo_session(self, convo_mode)
    




































