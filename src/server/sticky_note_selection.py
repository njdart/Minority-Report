import math

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class StickyNoteSelector():
    def __init__(self):
        self.stickyNoteSelections = [] # List of Sticky Notes that are actively being moved by a user.
        self.closedHands = [] # List of closed hands that have not been over a sticky note long enough to select it.
        self.stickyNotes = [] # List of sticky notes updated everytime there is a canvas update.
        self.timeThresh  = 2
        self.hoverThresh = 100

    def updateNotes(self, newNotes):
        self.stickyNotes = newNotes

    def handOverNote(self, handPosX, handPosY):
        for note in self.stickyNotes:
            distance = math.sqrt(((note.displayPosX-handPosX) ** 2) + ((note.displayPosY-handPosY) ** 2))
            if distance < self.hoverThresh:
                if note.physicalFor == "None" or note.physicalFor == None:
                    return note
        return None

    def update(self, new_hands):
        from src.model.StickyNote import StickyNote
        from src.server import (app, socketio)
        newStickyNoteSelections = []
        newClosedHands = []
        for newHand in new_hands:
            selectedNote = search(newHand["id"], self.stickyNoteSelections)
            closedHand = search(newHand["id"], self.closedHands)
            if selectedNote:
                if newHand["closed"]:
                    # Update sticky note position
                    newStickyNoteSelection = {"handID":selectedNote["handID"],
                                              "handXPos":newHand["posX"],
                                              "handYPos":newHand["posY"],
                                              "noteID":selectedNote["noteID"]}
                    newStickyNoteSelections.append(newStickyNoteSelection)
                    socketio.emit('move_sticky_note', newStickyNoteSelection)
                else:
                    StickyNote.get(selectedNote["noteID"]).set_display_pos(selectedNote["handXPos"],
                                                                           selectedNote["handYPos"])
                    socketio.emit('note_deselected', selectedNote["noteID"])
            elif closedHand:
                if newHand["closed"]:
                    overNote = self.handOverNote(newHand["posX"], newHand["posY"])
                    if overNote:
                        if overNote.id == closedHand["noteID"]:
                            if newHand["timestamp"] - closedHand["start"] > self.timeThresh:
                                newStickyNoteSelection = {"handID":closedHand["handID"],
                                                          "handXPos":newHand["posX"],
                                                          "handYPos":newHand["posY"],
                                                          "noteID":overNote.id}
                                newStickyNoteSelections.append(newStickyNoteSelection)
                                socketio.emit('note_selected', selectedNote["noteID"])
                            else:
                                # Keep old closed hand
                                newClosedHand = {"handID":closedHand["handID"],
                                                 "noteID":closedHand["noteID"],
                                                 "start":closedHand["start"]}
                                newClosedHands.append(newClosedHand)
                        else:
                            # Update hand stickyNote pair as the match has changed
                            newClosedHand = {"handID":closedHand["handID"],
                                             "noteID":overNote.id,
                                             "start":newHand["timestamp"]}
                            newClosedHands.append(newClosedHand)
            elif newHand["closed"]:
                overNote = self.handOverNote(newHand["posX"], newHand["posY"])
                if overNote:
                    newClosedHand = {"handID":newHand["id"],
                                     "noteID":overNote.id,
                                     "start":newHand["timestamp"]}
                    newClosedHands.append(newClosedHand)
        self.stickyNoteSelections = newStickyNoteSelections
        self.closedHands = newClosedHands

def search(handID, list):
    for item in list:
        if item["handID"] == handID:
            return item
    return None


