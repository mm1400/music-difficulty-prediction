import sys
import cv2
import numpy as np
from .best_fit import fit
from .rectangle import Rectangle
from .note import Note
from concurrent.futures import ThreadPoolExecutor
from midiutil import MIDIFile
import os

def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w, h = int(w * scale), int(h * scale)
        img_locations.append([Rectangle(pt[0], pt[1], w, h) for pt in zip(*locations[i][::-1])])
    return img_locations

def merge_recs(recs, threshold):
    filtered = []
    while recs:
        r = recs.pop(0)
        recs.sort(key=lambda x: x.distance(r))
        merged = True
        while merged:
            merged = False
            i = 0
            while i < len(recs):
                if r.overlap(recs[i]) > threshold:
                    r = r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > (r.w + recs[i].w) / 2:
                    break
                else:
                    i += 1
        filtered.append(r)
    return filtered

def main(img_path):
    def load_images(paths):
        images = []
        
        base_path = os.path.join(os.getcwd(), "resources", "template")
        
        # Loop through paths and try to load the images
        for path in paths:
            img_path = os.path.join(base_path, path)
            
            # Check if the image path exists
            if os.path.exists(img_path):
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    images.append(img)
                else:
                    print(f"Failed to load image: {img_path}")
            else:
                print(f"Image path does not exist: {img_path}")
        
        return images
    
    # Load images for each template
    staff_imgs = load_images(["staff2.png", "staff.png"])
    quarter_imgs = load_images(["quarter.png", "solid-note.png"])
    sharp_imgs = load_images(["sharp.png"])
    flat_imgs = load_images(["flat-line.png", "flat-space.png"])
    half_imgs = load_images(["half-space.png", "half-note-line.png",
                             "half-line.png", "half-note-space.png"])
    whole_imgs = load_images(["whole-space.png", "whole-note-line.png",
                              "whole-line.png", "whole-note-space.png"])

    thresholds = {
        'staff': (50, 150, 0.77),
        'sharp': (50, 150, 0.70),
        'flat': (50, 150, 0.77),
        'quarter': (50, 150, 0.70),
        'half': (50, 150, 0.70),
        'whole': (50, 150, 0.70),
    }

    gray = cv2.imread(img_path, 0)
    _, img_thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    width, height = img_thresh.shape[::-1]

    staff_recs = [r for group in locate_images(img_thresh, staff_imgs, *thresholds['staff']) for r in group]
    y_hist = np.bincount([r.y for r in staff_recs])
    avg = np.mean(list(set(y_hist)))
    staff_recs = [r for r in staff_recs if y_hist[r.y] > avg]
    staff_recs = merge_recs(staff_recs, 0.01)
    staff_boxes = merge_recs([Rectangle(0, r.y, width, r.h) for r in staff_recs], 0.01)

    def match_and_merge(name, templates):
        recs = locate_images(img_thresh, templates, *thresholds[name])
        return merge_recs([r for group in recs for r in group], 0.5)

    # Parallelize the matching and merging of templates
    with ThreadPoolExecutor() as executor:
        futures = {
            "sharp": executor.submit(match_and_merge, "sharp", sharp_imgs),
            "flat": executor.submit(match_and_merge, "flat", flat_imgs),
            "quarter": executor.submit(match_and_merge, "quarter", quarter_imgs),
            "half": executor.submit(match_and_merge, "half", half_imgs),
            "whole": executor.submit(match_and_merge, "whole", whole_imgs),
        }
        sharp_recs = futures["sharp"].result()
        flat_recs = futures["flat"].result()
        quarter_recs = futures["quarter"].result()
        half_recs = futures["half"].result()
        whole_recs = futures["whole"].result()

    note_groups = []
    for box in staff_boxes:
        condition = lambda r: abs(r.middle[1] - box.middle[1]) < box.h * 5 / 8
        staff_sharps = [Note(r, "sharp", box) for r in sharp_recs if condition(r)]
        staff_flats = [Note(r, "flat", box) for r in flat_recs if condition(r)]
        notes = []
        notes += [Note(r, "4,8", box, staff_sharps, staff_flats) for r in quarter_recs if condition(r)]
        notes += [Note(r, "2", box, staff_sharps, staff_flats) for r in half_recs if condition(r)]
        notes += [Note(r, "1", box, staff_sharps, staff_flats) for r in whole_recs if condition(r)]
        notes.sort(key=lambda n: n.rec.x)

        staffs = sorted([r for r in staff_recs if r.overlap(box) > 0], key=lambda r: r.x)
        group, i, j = [], 0, 0
        while i < len(notes):
            if j < len(staffs) and notes[i].rec.x > staffs[j].x:
                if group: note_groups.append(group)
                group = []
                j += 1
            else:
                group.append(notes[i])
                i += 1
        if group: note_groups.append(group)

    midi = MIDIFile(1)
    midi.addTrackName(0, 0, "Track")
    midi.addTempo(0, 0, 140)

    time = 0
    for group in note_groups:
        for note in group:
            duration = {"1": 4, "2": 2, "4,8": 1 if len(group) == 1 else 0.5}[note.sym]
            midi.addNote(0, 0, note.pitch, time, duration, 100)
            time += duration

    with open("output.mid", 'wb') as f:
        midi.writeFile(f)

if __name__ == "__main__":
    main(sys.argv[1])
